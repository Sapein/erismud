import sha, re
import tables
from random import randrange, getrandbits
from asynchat import simple_producer
cu = tables.cu

from TelnetIAC import TelnetTalk

try:
    motd = ""
    mot = open("motd.txt", "r")
    bou = mot.read()
    mot.close()
    bou = bou.splitlines()
    for i in bou:
        motd += i + '\r\n'

except:
    print "File \'motd.txt\' not found, login prompt set to default."
    motd = "MOTD not set.\r\n\r\nLogin:"

class MiniProducer:
    def __init__(self, contents):
        self.contents = contents

    def more(self):
        c = self.contents
        self.contents = None
        return c

class EndSession(Exception): pass

class FirstLogin:
    """Class to manage state while logging in user"""

    def __init__(self, server, addr):
        self.server = server
        self.ipaddr = addr
        self.line = None
        self.plname = None
        self.email = None
        self.ansi = None
        self.step = 1
        self.check = 0
        self.nak = []
        self.enc_pass = ''

    def echo_off(self, session):
        #session.push("\033[8m\xff\373\001") # ECHO OFF
        session.push("\xff\373\001") # ECHO OFF

    def echo_on(self, session):
        #session.push("\033[8m\xff\374\001") # ECHO ON
        session.push("\xff\374\001") # ECHO ON

    def generate_salt(self):
        salt = ""
        possible = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.;,=+!:?$%@-_"

        while len(salt) < 64:
            char = possible[randrange(len(possible))]
            if salt.find(char) == -1:
                salt += char

        return salt

    def encpass(self, ppass, salt):
        ma = sha.new()
        ma.update(salt)
        ma.update(ppass)
        return ma.hexdigest()

    def check_password(self, passtest):
        cu.execute("select passwd,salt from players where name = ?", (self.plname,))
        cchk = cu.fetchall()[0]

        test = self.encpass(passtest, cchk[1])
        if test == cchk[0]: return 0
        else: return -1
        
    def check_ban(self, uname):
        cu.execute("select banned from players where name = ?", (uname,))
        self.bchk = cu.fetchall()[0]

        if self.bchk[0] == 1: return 1
        else: return 0

    def handle(self, session, cmd):
        """ This is ugly. asynchat doesn't implement interactive sessions so we have
			to simulate a dialog using a counter that is incremented at every step.
		"""

        if not cmd: cmd = " "

        # Filter the telnet commands
        self.tiac = TelnetTalk()
        self.ndata = self.tiac.listen(cmd)
        self.cmd = self.ndata[0]

        session.push(self.ndata[1]) # Reply accordingly

        if self.step == 1:
            self.plname = self.cmd.lower().strip()
            if not self.plname:
                session.push("You will need a name. \r\n\r\n")
                session.push("Please enter your name: ")
                return
            if not self.plname.isalpha():
                session.push("You name can only contain letters.\r\n")
                session.push("Please enter your name: ")
                return

            wrongname = False
            badnames = open('badnames', 'r')
            for naughtyword in badnames:
                if naughtyword.strip() in self.plname:
                    wrongname = True
                    break
            badnames.close()

            if wrongname:
                session.push("This name is not allowed. Choose something else.\r\n")
                session.push("Please enter your name: ")
                return

            try:
                cu.execute("select name from players where name = ?", (self.plname,))
                self.nak = cu.fetchone()
                session.push(str("Welcome in, %s\r\n" % self.nak[0].capitalize()))
                session.push("Password: ")
                self.echo_off(session)
                self.step = 5 # Existing user
                #return self
            except: 
                session.push("New player! Welcome to ErisMUD!\r\n")
                self.plname = str(self.plname)
                session.push(str("Your name is %s\r\n" % self.plname.capitalize()))
                session.push("Please enter your password: ")
                self.echo_off(session)
                self.step = 2 # New user

        elif self.step == 2:
            #self.echo_on(session)
            self.fpass = self.cmd
            if not self.fpass:
                session.push("Please enter a password: ")
                self.echo_off(session)
                return
            else:
                session.push("\r\nConfirm your password: ")
                self.echo_off(session)
                self.step = 3

        elif self.step == 3:
            self.spass = self.cmd
            if self.fpass == self.spass:
                self.echo_on(session)
                session.push("\r\nDo you want ANSI colors? (yes, no) ")
                self.step = 6
            else:
                session.push("Passwords don't match.\r\n")
                session.push("Please enter your password: ")
                self.echo_off(session)
                self.step = 2

        elif self.step == 5:
            self.echo_on(session)

            if not self.cmd:
                session.push("Password: ")
                self.echo_off(session)
                return

            if self.check_password(self.cmd) == 0:
                # Check if the user is banned.
                if self.check_ban(self.plname) == 1:
                    session.push("You have been banned. Get out.\r\n")
                    session.close()
                else:
                    session.push("\r\nYou've logged in successfully!\r\n\r\n")
                    session.push("Press <enter> to join.\r\n")
                    session.push("> ")
                    self.step = 8
            else:
                session.push("Wrong password.\r\n")
                session.push("Password: ")
                self.echo_off(session)

        elif self.step == 6:
            self.echo_on(session)
            self.colors = cmd.lower()
            if (self.colors == "y") or (self.colors == "yes"):
                self.ansi = 'on'
            else:
                self.ansi = 'off'
            session.push("What is your email address?\r\n")
            self.step = 7

        elif self.step == 7: # CHANGE
            #self.echo_on(session)
            emailreg = re.compile('^[0-9a-z_.+\-]+@[0-9a-z_.\-]+\.[a-z]{2,4}', re.IGNORECASE)
            if emailreg.match(self.cmd) != None:
                self.email = self.cmd
                self.step = 8
                self.createUser(session, self.plname, self.fpass)
            else:
                session.push("Invalid format for an email address.\r\n")
                session.push("What is your email address?\r\n")
                self.step = 7

        elif self.step == 8:
            cu.execute("select id,ip_addr from players where name = ?", (self.plname,))
            self.nak = cu.fetchone()

            if self.nak[1] != None and self.nak[1] != "127.0.0.1":
                session.push("This player is already in.\r\n")
                session.close()
            else:
                # Store some basic info into the socket object.
                session.p_id = self.nak[0]
                session.pname = str(self.plname.capitalize())
                #session.ipaddr = self.ipaddr[0]

                session.push("> ")
                session.enter(self.server.enterg)
                #EnterGame.add(self)
                #return self

        else:
            session.push("Something is wrong, contact the admin.\r\n")

    def createUser(self, session, pname, ppass):
        # Initialize attributes
        # self.stre = randrange(15, 60)
        # self.stm = randrange(15, 60)
        # self.dex = randrange(15, 60)
        # self.agl = randrange(15, 60)
        # self.intl = randrange(15, 60)
        # self.wil = randrange(15, 60)
        # self.prs = randrange(15, 60)
        # self.per = randrange(15, 60)
        # self.app = randrange(15, 60)
        # session.push("Your stats are:\r\n")
        # session.push("Strength: " + str(self.stre) + "\r\n")
        # session.push("Stamina: " + str(self.stm) + "\r\n")
        # session.push("Dexterity: " + str(self.dex) + "\r\n")
        # session.push("Agility: " + str(self.agl) + "\r\n")
        # session.push("Intelligence: " + str(self.intl) + "\r\n")
        # session.push("Willpower: " + str(self.wil) + "\r\n")
        # session.push("Presence: " + str(self.prs) + "\r\n")
        # session.push("Perception: " + str(self.per) + "\r\n")
        # session.push("Appearance: " + str(self.app) + "\r\n")

        self.salty = self.generate_salt()
        self.truepass = self.encpass(ppass, self.salty)

        self.test = (pname, self.email, self.truepass, self.salty, self.ansi)
        cu.execute("insert into players(id,name,email,passwd,salt,location,description,colors)\
                   values (NULL,?,?,?,?,0,'Description not set',?)", self.test)

        # Initialize skills
        # cu.execute("select p_id from pnames where names = ?", [self.plname])
        # self.pook = cu.fetchall()
        #self.skil = (randrange(1, 20), randrange(1, 20), 0)
        # cu.execute("insert into skills(p_id, disguise, dodge, evasion, juggling, sneak)\
                    # values(?, ?, ?, ?, ?, ?)", (self.pook[0][0], 0, 0, 0, 0, 0))
        # cu.execute("insert into learningpts(p_id, disguise, dodge, evasion, juggling, sneak)\
                    # values(?, ?, ?, ?, ?, ?)", (self.pook[0][0], 0, 0, 0, 0, 0))

        session.push("\r\nNew player created!\r\n")
        session.push("Press <enter> to join.\r\n")

    def add(self, session):
        # First session reference
        self.session = session
        session.push(motd)
