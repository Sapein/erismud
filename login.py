import sha, re
import tables
from random import randrange, getrandbits
from asynchat import simple_producer
cu = tables.cu

from model import Select, Insert
Insert = Insert()
Select = Select()

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
        self.cchk = Select.getPassword(self.plname)

        self.test = self.encpass(passtest, self.cchk[1])
        if self.test == self.cchk[0]: return 0
        else: return -1
        
    def check_ban(self, uname):
        self.bchk = Select.getBan(uname)

        if self.bchk[0] == 1: return 1
        else: return 0

    def handle(self, session, cmd):
        """ This is ugly. asynchat doesn't implement interactive sessions so we have
            to simulate a dialog using a counter that is incremented at every step."""

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
                self.nak = Select.getPlayerByName(self.plname)
                session.push(str("Welcome in, %s\r\n" % self.nak[1].capitalize()))
                session.push("Password: ")
                self.echo_off(session)
                self.step = 5 # Existing user
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
                    session.push("Press <enter> to join.\r\n>")
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
            self.nak = Select.getIP(self.plname)

            if self.nak[1] != None and self.nak[1] != "127.0.0.1":
                session.push("This player is already in.\r\n")
                session.close()
            else:
                # Store some basic info into the socket object.
                session.p_id = self.nak[0]
                session.pname = str(self.plname.capitalize())

                session.push("> ")
                session.enter(self.server.enterg)

        else:
            session.push("Something is wrong, contact the admin.\r\n")

    def createUser(self, session, pname, ppass):
        self.salty = self.generate_salt()
        self.truepass = self.encpass(ppass, self.salty)

        self.test = (pname, self.email, self.truepass, self.salty, self.ansi)
        Insert.newPlayer(self.test)

        session.push("\r\nNew player created!\r\n")
        session.push("Press <enter> to join.\r\n")

    def add(self, session):
        # First session reference
        self.session = session
        session.push(motd)
