from asyncore import dispatcher
from asynchat import async_chat
import socket, asyncore, time, sys, ConfigParser
from login import *
from admin import *

from model import Select, Update
Update = Update()
Select = Select()

from TelnetIAC import TelnetTalk

# Initial configuration file reading.
config = ConfigParser.ConfigParser()
config.read("eris.conf")

# Global dictionaries holding the player's ID, socket and IP address.
sessions = {}
ipsessions = {}


logger = open(config.get("logging", "logfile"), 'a')
#logger = open("main.log", 'a')
def Log(line):
    "Just call Log('text') to log to the main log file."
    timer = time.asctime()
    print type(logger)
    logger.write("%s %s\n" % (line, timer))
    logger.flush()


class Handler:
    "Command parser, where all player commands go."

    def unknown(self, session, cmd):
        session.push('Unknown command: %s\r\n' % str(cmd))

    def handle(self, session, line):
        #Time of last command executed. Will be used for external timeout cleanup.
        Update.setLastAction(time.time(), session.p_id)

        if not line.strip(): session.push("> ")

        # Filter the telnet commands
        self.tiac = TelnetTalk()
        self.ndata = self.tiac.listen(line)
        line = self.ndata[0]

        session.push(self.ndata[1]) # Reply accordingly

        parts = line.split(' ', 1)
        cmd = parts[0]
        if not cmd: pass

        # Easier to do it here, as EndSession is defined outside of action.py
        elif (cmd == "logout") or (cmd == "quit"):
            raise EndSession

        else:
            try: line = parts[1].strip()
            except IndexError: line = ''
            meth = getattr(Actions, 'do_'+cmd, None) # Normal commands, actions.py

            if cmd.find('@') == 0 :
                methadm = getattr(Admincmd, 'do_'+cmd.strip('@'), None) # Admin commands, admin.py
                if session.pname in self.coders and callable(methadm):
                    methadm(session, line)
                    session.push("> ")
                else:
                    self.unknown(session, cmd)
                    session.push("> ")

            elif callable(meth): # Normal command
                meth(session, line)
                session.push("> ")
            else:
                self.unknown(session, cmd)
                session.push("> ")


class EndSession(Exception): pass


class EnterGame(Handler):

    def __init__(self, session):
        self.session = session
        self.admin = []
        self.coders = []

        #Coders file, for in-game creators/wizards/builders
        self.coder = open('coders', 'r')
        self.icoder = iter(self.coder)
        for line in self.icoder:
            self.coders.append(line.strip('\n'))
        self.coder.close()

    def enter(self, room):
        self.room = room
        room.add(self, self.session)

    def found_terminator(self):
        line = (''.join(self.data))
        self.data = []
        if not line: session.push("> ")
        else:
            try: self.handle(self, line)
            except: raise EndSession

    def add(self, session):
        self.ival = ipsessions.items()

        if session.addr[0] != "127.0.0.1" and session.addr[0] in self.ival: # Allow multiusers for the admin.
            session.push("You are already connected!\r\n\r\n")
            raise EndSession

        sessions[session.p_id] = session
        ipsessions[session.p_id] = session.addr[0]
        Update.setIP(session.addr[0], session.p_id)
        
        #Store the player's starting location in the socket object.
        session.is_in = 1
        Update.setLocation(session.p_id, 1)

        # Check if the user supports ANSI colors
        if Select.getColors(session.p_id) == "on": Actions.do_setansi(session, "on")
        else: Actions.do_setansi(session, "off")

        for i in sessions:
            try:
                i.push("%s enters the game.\r\n\r\n> " % (session.pname,))
            except: pass

        print "%s logged in." % session.pname
        Log("%s logged in from %s" % (session.pname,session.addr[0]))
        Actions.do_look(session, '') # To be replaced with something nicer.
        session.push("> ")

        #####
        #import browser1
        #browser1.dumpObj(session)

class SecondServSock(async_chat):
    #The chat server, instanced for all users

    def __init__(self, server, sock, addr):
        async_chat.__init__(self, sock)
        self.server = server
        self.ipaddr = addr
        self.set_terminator("\n")
        self.name = None
        self.data = []
        self.sock = sock
        self.enter(FirstLogin(server, addr[0])) #Call the login procedure before anything.

    def collect_incoming_data(self, data):
        self.data.append(data)
    def found_terminator(self):
        line = (''.join(self.data))
        line = line.strip('\r')
        self.tiac = TelnetTalk()
        self.ndata = self.tiac.listen(line)
        line = self.ndata[0]
        self.data = []

        try: 
            self.room.handle(self, line)
        except EndSession:
            self.handle_close()

    def handle_close(self):
        self.ival = ipsessions.items()
        for i in self.ival:
            self.test = str(sessions[i[0]])
            self.tesb = str(self.sock)
            try:
                if (self.ipaddr[0] == i[1]) & (self.test == self.tesb):
                    self.leaver = Select.getPlayerByID(i[0])
                    self.leaver = self.leaver[1].capitalize()
                    #In any case, if the player exits, remove him.
                    Update.LogoutPlayer(i[0])
                    Log("%s disconnected from %s" % (self.leaver, self.ipaddr[0]))
                    print "%s logged out." % self.leaver

                    del sessions[i[0]]
                    del ipsessions[i[0]]

                    self.locali = Select.getAllPlayersWithIP()
                    
                    for j in self.locali:
                        self.tmpsec = sessions[j[0]]
                        if self.tmpsec == None: # Shouldn't happen, do some cleaning
                            Update.LogoutPlayer(j[0])
                        else:
                            self.tmpsec.push("%s leaves the game.\r\n\r\n> " % (self.leaver,))

                    async_chat.handle_close(self)
                else: raise
            except: raise

    def enter(self, room):
        self.room = room
        room.add(self)


###
# Time related actions
# * All commented out for now since it's not used.
###

#schedule = {'heal':100.0}
#lastrun = {}

#def heal():
    #pass
    ###cu.execute("update pnames set curhp=curhp+1 where p_id=? and curhp<maxhp", session.p_id)


### The timer loop
#def Timer(timer):

    #sched = schedule.iteritems()
    #for i in sched:
        #try: lastrun[i[0]]
        #except: lastrun[i[0]] = time.time()

        #diff = timer - lastrun[i[0]]

        ### Every 100 seconds, run heal(), defined above.
        #if diff >= schedule['heal']:
            #heal()
            #lastrun['heal'] = time.time()


class MainServSock(dispatcher):
    # The Server

    def __init__(self, port):
        dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('', port))
        self.listen(int(config.get("server", "max_users")))
        self.enterg = EnterGame(self)
    def handle_accept(self):
        conn, addr = self.accept()
        SecondServSock(self, conn, addr)

if __name__ == '__main__':
    s = MainServSock(int(config.get("server", "port")))
    Update.resetAllIPs()

    try:
        import actions
        Actions = actions.Actions(sessions)
        Admincmd = AdminCmds(sessions, ipsessions)
        print "Accepting connections..."
        while 1:
            asyncore.loop(timeout=5, count=1) # Timer() called every 5 seconds.
            #Timer(time.time())
    except KeyboardInterrupt: #print
        print

