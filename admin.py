import tables
from common import C
from model import Select, Update, Insert, Delete
import template as tpl

Update = Update()
Select = Select()
Insert = Insert()
Delete = Delete()

#cu = tables.cu

class AdminCmds:
    """ Special commands for admins."""

    def __init__(self, sessions, ipsessions):
        self.sessions = sessions
        self.ipsessions = ipsessions

        self.twoway = {'north':'south','south':'north','up':'down','down':'up','northeast':'southwest',
                       'southwest':'northeast','northwest':'southeast','southeast':'northwest', 
                       'east':'west', 'west':'east'}

    def do_addroom(self, session, line):
        try:
            self.rid = Insert.addRoom()
            session.push(tpl.ADDROOM % self.rid)
        except:
            session.push(tpl.ADDROOM_ERR)

    def do_ban(self, session, line):
        try:
            Update.banPlayer(line.lower())
            session.push(tpl.BAN % line)
        except:
            session.push(tpl.BAN_ERR)

    def do_unban(self, session, line):
        try:
            Update.unbanPlayer(line.lower())
            session.push(tpl.UNBAN % line)
        except:
            session.push(tpl.UNBAN_ERR)

    def do_listbans(self, session):
        self.whole = Select.getBannedPlayers()
        session.push("%6s %20s\r\n" % ("ID", "NAME"))
        for i in self.whole:
            session.push("%6s %20s\r\n" % (str(i[0]), str(i[1])))

    def do_delroom(self, session, line):
        try:
            self.fop = Select.getRoom(line)
            Delete.deleteRoom(self.fop[0])
            Delete.deleteLink(self.fop[0])
            session.push(tpl.DELROOM % (fop,))
        except:
            session.push(tpl.DELROOM_ERR)

    def do_listrooms(self, session, line):
        self.whole = Select.getAllRooms()
        session.push("%6s %15s\r\n" % ("ID", "SHORT DESC"))
        for i in self.whole:
            session.push("%6s %15s\r\n" % (str(i[0]), str(i[1])))

    def do_addlink(self, session, line):
        if not line: session.push(tpl.ADDLINK_ERR)
        self.argu = line.lower()
        if not self.argu.strip(): session.push("> ")
        self.parts = self.argu.split(' ', 3)
        try:
            self.roomnum = int(self.parts[0])
            self.exitnum = int(self.parts[1])
            self.direction = str(self.parts[2])
            
            Insert.addLink(self.roomnum, self.exitnum, self.direction)
            session.push(tpl.ADDLINK)
        except:
            session.push(tpl.ADDLINK_ERR)

### Not really useful
#   def do_listlinks(self, session, line):
#       cu.execute("select * from links")
#       self.linksall = cu.fetchall()
#       session.push("%6s %6s %6s %4s\r\n" % ("ID", "ORIGIN", "DEST", "EXIT"))
#       for i in self.linksall:
#           session.push("%6s %6s %6s %4s\r\n" % (str(i[0]), str(i[1]), str(i[2]), str(i[3])))

    def do_dellink(self, session, line):
        if not line: session.push(tpl.DELLINK_ERR)
        self.linker = Select.getLink(line)
        
        if self.linker != []:
            Delete.deleteLinkById(self.linker[0])
            session.push(tpl.DELLINK % self.linker[0])
        else:
            session.push(tpl.DELLINK_ERR)

    def do_setshort(self, session, line):
        try:
            Update.setShortDesc(session.is_in, line)
            session.push(tpl.SETSHORT)
        except: session.push(tpl.SETSHORT_ERR)

    def do_setlong(self, session, line):
        try:
            Update.setLongDesc(session.is_in, line)
            session.push(tpl.SETLONG)
        except: session.push(tpl.SETLONG_ERR)

    def do_addhelp(self, session, line):
        if line == '': session.push(tpl.ADDHELP_ERR)
        else:
            self.argu = line.lower()
            self.parts = self.argu.split(' ', 1)
            try:
                cu.execute("update helps set command = ? and doc = ?", (self.parts[0], self.parts[2]))
            except:
                cu.execute("insert into helps(command, doc) values\
                           (?, ?)", (self.parts[0], self.parts[1]))
            session.push(tpl.ADDHELP)

    def do_locate(self, session, line):
        self.all = Select.getLocation()

        session.push("%4s %10s %5s %4s\r\n" % ("ID", "NAME", "LOC", "IP"))
        for i in self.all:
            session.push("%4s %10s %5s %4s\r\n" % (str(i[0]), i[1].capitalize(), str(i[2]), i[3]))

    def do_goto(self, session, line):
        try:
            self.room = Select.getRoom(line)
            Update.setLocation(self.room[0], session.p_id)
            session.is_in = self.room[0]
            session.push(tpl.GOTO)
        except: session.push(tpl.GOTO_ERR)

    def do_additem(self, session, line):
        if not line: session.push(tpl.ADDITEM_ERR)
        else:
            self.iid = Insert.addItem(line.lower())
            session.push(tpl.ADDITEM % (line.lower(), self.iid))

    def do_listitems(self, session, line):
        self.lookobj = Select.getAllItems()

        session.push("%5s %10s %4s\r\n" % ("ID", "NAME", "DESC"))
        for i in self.lookobj:
            session.push("%5s %10s %4s\r\n" % (i[0], i[1], i[2][:20]))

    def do_delitem(self, session, line):
        self.barn = Select.getItemNameId(line)
        try:
            Delete.deleteItem(self.barn[0])
            session.push(tpl.DELITEM % self.barn[1])
        except:
            session.push(tpl.DELITEM_ERR)

    def do_itemdesc(self, session, line):
        try:
            self.splitarg = line.split(' ', 1)
            self.rcount = Update.setItemDescription(self.splitarg[0].lower(), self.splitarg[1])
            if self.rcount == 1:
                session.push(tpl.ITEMDESC % str(self.splitarg[0]).lower())
            else: 
                session.push(tpl.ITEMDESC_ERR)

        except: session.push(tpl.)

    def do_clone(self, session, line):
        self.obj = Select.getItemNameId(line.lower())
        self.npc = Select.getNpc(line.lower())

        if self.obj:
            Insert.cloneItem(self.obj[0], session.p_id, time.time())
            session.push(tpl.CLONE % str(self.cloner[1]))
        elif self.npc:
            Insert.cloneItem(self.obj[0], session.p_id, time.time())
            session.push(tpl.CLONE % str(self.cloner[1]))
        else: session.push(tpl.CLONE_ERR)

    def do_list_oinst(self, session, line):
        self.instobj = Select.listObjectInstances()

        session.push("%6s %6s %7s %9s\r\n" % ("ID", "OBJ", "OWNER", "LOC"))
        for i in self.instobj:
            session.push("%6s %6s %7s %9s\r\n" % (str(i[0]), str(i[1]), str(i[2]), str(i[3])))

    def do_dest_obj(self, session, line):
        self.rcount = Delete.deleteObject(line)
        if self.rcount == 1: 
            session.push(tpl.DESTOBJ % line)
        else:
            session.push(tpl.DESTOBJ_ERR % line)

    def do_dest_npc(self, session, line):
        self.rcount = Delete.deleteNpcInst(line)
        if self.rcount == 1: 
            session.push(tpl.DESTNPC % line)
        else: 
            session.push(tpl.DESTNPC_ERR % line)

    def do_addnpc(self, session, line):
        if not line: session.push(tpl.ADDNPC_ERR)
        else:
            self.nid = Insert.addNpc(line.lower())
            session.push(tpl.ADDNPC % (line.lower(),self.nid))

    def do_npcdesc(self, session, line):
        if not line: session.push(tpl.NPCDESC_ERR)
        
        self.splitarg = line.split(' ', 1)
        self.barn = Select.getNpc(self.splitarg[0].lower())
        
        if self.barn:
            setNpcDesc(self.barn[0], self.splitarg[1])
            session.push(tpl.NPCDESC % str(self.splitarg[0]).lower())
        else: session.push(tpl.NPCDESC_ERR)

    def do_delnpc(self, session, line):
        self.barn = Select.getNpc(line)

        if self.barn: #If the object exists
            Delete.deleteNpc(self.barn[0])
            session.push(tpl.DELNPC % line)
        else: session.push(tpl.DELNPC_ERR)

    def do_listnpcs(self, session, line):
        self.whole = Select.listNpcs()

        session.push("%5s %10s %6s\r\n" % ("ID", "NAME", "DESC"))
        for i in self.whole:
            session.push("%5s %10s %6s\r\n" % (str(i[0]), str(i[1]), str(i[2])))

    def do_listplayers(self, session, line):
        self.allplay = Select.listPlayers()

        session.push("%5s %15s %20s\r\n" % ("ID", "NAME", "EMAIL"))
        for i in self.allplay:
            session.push("%5s %15s %20s\r\n" % (str(i[0]), str(i[1]), str(i[2])))

    def do_ridplayer(self, session, line):
        self.getrid = Select.getPlayerByName(line.lower())
        try:
            Delete.deletePlayer(self.getrid[1])
            session.push(tpl.RIDPLAYER % line.capitalize())
        except:
            session.push(tpl.RIDPLAYER_ERR % line.capitalize())

    def do_edig(self, session, line):
        c = C(session)
        if not line: session.push(tpl.EDIG_ERR1)
        else:
            self.splitarg = line.split(' ', 1)
            self.exists = Select.getExitsInRoom(session.is_in)

            try:
                self.flat = c.flatten(self.exists)
                if self.splitarg[1] in self.flat:
                    session.push(tpl.EDIG_ERR2)
                else:
                    self.count = Insert.addRoom(self.splitarg[0])
                    Insert.addLink(session.is_in, self.count, self.splitarg[1])
                    Insert.addLink(self.count, session.is_in, self.twoway[self.splitarg[1]])
                    session.push(tpl.EDIG % self.splitarg[1])
            except:
                session.push(tpl.EDIG_ERR1)

    ### Commented out, it's not useful for now.
    ###
    #def do_addalias(self, session, line):
        #if not line: session.push("Correct syntax: addalias <name> <alias>\r\n")
        #else:
            #line = line.lower()
            #self.splitarg = line.split(' ', 1)

            #cu.execute("select id,alias,name from objects where name = ?", (self.splitarg[0],))
            #self.test = cu.fetchone()

            #if self.test != []:
                #try:
                    #if self.test[1] != None:
                        #self.add = "%s:%s" % (self.test[1], self.splitarg[1])
                        #cu.execute("update objects set alias = ? where name = ?", (self.add, self.splitarg[0]))
                    #else:
                        #cu.execute("update objects set alias = ? where name = ?", (self.splitarg[1], self.splitarg[0]))
                #except: raise

    def do_email(self, session, line):
        if not line: session.push(tpl.EMAIL)
        else:
            self.email = Select.getEmail(line.lower())
            if self.email:
                session.push("%s: %s\r\n" % (self.email[0], self.email[1]))
            else:
                session.push(tpl.EMAIL_ERR)

    def do_kickout(self, session, line):
        try:
            self.kicked = Select.getPlayerByName(line.lower())
            self.kick = self.sessions[self.kicked[0]]
            self.kick.shutdown(0)
        except:
            session.push(tpl.EMAIL_ERR)

    def do_import(self, session, line):		
        self.splitarg = line.split(' ', 2)
        if len(self.splitarg) < 3: session.push(tpl.IMPORT_ERR1)
        else:
            self.map = self.splitarg[0]
            self.start = self.splitarg[1]
            self.dir = self.splitarg[2]			# Need to check if this exit already exists in this room

            # Not really secure.. remove all from inside the string instead
            self.file = open(self.map.strip('./'), "r")

            from mapper import Mapper
            get_this = Mapper(self.file)
            got_this = get_this.MapThis()

            self.lab = got_this[self.start]
            if self.start in got_this:

                for i in got_this:
                    Insert.addRoom(int(i))

                Insert.addLink(session.is_in, self.start, self.dir)
                Insert.addLink(self.start, session.is_in, self.twoway[self.dir])

                for i in got_this.items():
                    for j in i[1]:
                        Insert.addLink(str(i[0]), str(j[1]), str(j[0]))

                session.push(tpl.IMPORT)

            else: session.push(tpl.IMPORT_ERR2)
