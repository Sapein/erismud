import tables, time
from common import C
from model import Select, Update, Insert, Delete

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
            session.push("Your new room has id #%d.\r\n" % self.rid)
        except:
            session.push("Something didn't work.\r\n")

    def do_ban(self, session, line):
        try:
            Update.banPlayer(line.lower())
            session.push("%s has been banned and will not be able to log back in. Use <unban> to undo.\r\n" % line)
        except:
            session.push("Impossible to ban that player.\r\n")

    def do_unban(self, session, line):
        try:
            Update.unbanPlayer(line.lower())
            session.push("%s has been unbanned.\r\n" % line)
        except:
            session.push("Impossible to unban that player.\r\n")

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
            session.push("Room #%s and all of its links have been deleted.\r\n" % (fop,))
        except:
            session.push("Unable to find this room.\r\nCorrect syntax: delroom <room ID>\r\n")

    def do_listrooms(self, session, line):
        self.whole = Select.getAllRooms()
        session.push("%6s %15s\r\n" % ("ID", "SHORT DESC"))
        for i in self.whole:
            session.push("%6s %15s\r\n" % (str(i[0]), str(i[1])))

    def do_addlink(self, session, line):
        if not line: session.push("Correct syntax: addlink <origin> <destination> <direction>\r\n")
        self.argu = line.lower()
        if not self.argu.strip(): session.push("> ")
        self.parts = self.argu.split(' ', 3)
        try:
            self.roomnum = int(self.parts[0])
            self.exitnum = int(self.parts[1])
            self.direction = str(self.parts[2])
            
            Insert.addLink(self.roomnum, self.exitnum, self.direction)
            session.push("New link added.\r\n")
        except:
            session.push("Correct syntax: addlink <origin> <destination> <direction>\r\n")

#   def do_listlinks(self, session, line):
#       cu.execute("select * from links")
#       self.linksall = cu.fetchall()
#       session.push("%6s %6s %6s %4s\r\n" % ("ID", "ORIGIN", "DEST", "EXIT"))
#       for i in self.linksall:
#           session.push("%6s %6s %6s %4s\r\n" % (str(i[0]), str(i[1]), str(i[2]), str(i[3])))

    def do_dellink(self, session, line):
        if not line: session.push("Correct syntax: dellink <link ID>\r\n")
        self.linker = Select.getLink(line)
        
        if self.linker != []:
            Delete.deleteLinkById(self.linker[0])
            session.push("Link #%s has been deleted.\r\n" % self.linker[0])
        else:
            session.push("This link does not exist.\r\n")

    def do_setshort(self, session, line):
        try:
            Update.setShortDesc(session.is_in, line)
            session.push("Short description changed.\r\n")
        except: session.push("Unable to set the short description of this room.\r\n")

    def do_setlong(self, session, line):
        try:
            Update.setLongDesc(session.is_in, line)
            session.push("Long description changed.\r\n")
        except: session.push("Unable to set the long description of this room.\r\n")

    def do_addhelp(self, session, line):
        if line == '': session.push("Correct syntax: addhelp <title> <documentation>\r\n")
        else:
            self.argu = line.lower()
            self.parts = self.argu.split(' ', 1)
            try:
                cu.execute("update helps set command = ? and doc = ?", (self.parts[0], self.parts[2]))
            except:
                cu.execute("insert into helps(command, doc) values\
                           (?, ?)", (self.parts[0], self.parts[1]))
            session.push("Help database updated.\r\n")

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
        except: session.push("This room does not exist.\r\n")

    def do_additem(self, session, line):
        if not line: session.push("The object needs a name.\r\n")
        else:
            self.iid = Insert.addItem(line.lower())
            session.push("Item %s has been created with ID #%s.\r\n" % (line.lower(), self.iid))

    def do_listitems(self, session, line):
        self.lookobj = Select.getAllItems()

        session.push("%5s %10s %4s\r\n" % ("ID", "NAME", "DESC"))
        for i in self.lookobj:
            session.push("%5s %10s %4s\r\n" % (i[0], i[1], i[2][:20]))

    def do_delitem(self, session, line):
        self.barn = Select.getItemNameId(line)
        try:
            Delete.deleteItem(self.barn[0])
            session.push("%s and all its instances have been destroyed.\r\n" % self.barn[1])
        except:
            session.push("This object does not exist.\r\n")

    def do_itemdesc(self, session, line):
        try:
            self.splitarg = line.split(' ', 1)
            self.rcount = Update.setItemDescription(self.splitarg[0].lower(), self.splitarg[1])
            if self.rcount == 1:
                session.push("Description set on %s.\r\n" % str(self.splitarg[0]).lower())
            else: 
                session.push("Item not found.\r\n")

        except: session.push("This object does not exist.\r\n@itemdesc <item name> <description>")

    def do_clone(self, session, line):
        self.obj = Select.getItemNameId(line.lower())
        self.npc = Select.getNpc(line.lower())

        if self.obj:
#            Insert.cloneItem(self.cloner[0], session.p_id, time.time())
            Insert.cloneItem(self.obj[0], session.p_id, time.time())
            session.push("%s has been cloned.\r\n" % str(self.obj[1]))
        elif self.npc:
            Insert.cloneItem(self.obj[0], session.p_id, time.time())
            session.push("%s has been cloned.\r\n" % str(self.obj[1]))
        else: session.push("No such object or NPC.\r\n")

    def do_list_oinst(self, session, line):
        self.instobj = Select.listObjectInstances()

        session.push("%6s %6s %7s %9s\r\n" % ("ID", "OBJ", "OWNER", "LOC"))
        for i in self.instobj:
            session.push("%6s %6s %7s %9s\r\n" % (str(i[0]), str(i[1]), str(i[2]), str(i[3])))

    def do_dest_obj(self, session, line):
        self.rcount = Delete.deleteObject(line)
        if self.rcount == 1: 
            session.push("Object Instance #%s has been destroyed.\r\n" % line)
        else:
            session.push("Object Instance #%s does not exist.\r\n" % line)

    def do_dest_npc(self, session, line):
        self.rcount = Delete.deleteNpcInst(line)
        if self.rcount == 1: 
            session.push("NPC Instance #%s has been destroyed.\r\n" % line)
        else: 
            session.push("NPC Instance #%s does not exist.\r\n" % line)

    def do_addnpc(self, session, line):
        if not line: session.push("The NPC needs a name.\r\n> ")
        else:
            self.nid = Insert.addNpc(line.lower())
            session.push("NPC %s has been created with ID #%s.\r\n" % (line.lower(),self.nid))

    def do_npcdesc(self, session, line):
        if not line: session.push("Correct syntax: npcdesc <name> <description>\r\n")
        
        self.splitarg = line.split(' ', 1)
        self.barn = Select.getNpc(self.splitarg[0].lower())
        
        if self.barn:
            setNpcDesc(self.barn[0], self.splitarg[1])
            session.push("Description set on %s.\r\n" % str(self.splitarg[0]).lower())
        else: session.push("This NPC does not exist.\r\n")

    def do_delnpc(self, session, line):
        self.barn = Select.getNpc(line)

        if self.barn: #If the object exists
            Delete.deleteNpc(self.barn[0])
            session.push("NPC #%s had been deleted.\r\n" % line)
        else: session.push("This NPC does not exist.\r\n")

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
        cu.execute("select id,name from players where name = ?", (line.lower(),))
        self.getrid = cu.fetchone()
        try:
            Delete.deletePlayer(self.getrid[1])
            session.push("Player %s has been completely wiped out of the system.\r\n" % line.capitalize())
        except:
            session.push("Player %s not found in the database.\r\n" % line.capitalize())

    def do_edig(self, session, line):
        c = C(session)
        if not line: session.push("Usage: edig <exit> <room name/short description>\r\n")
        else:
            self.splitarg = line.split(' ', 1)
            self.exists = Select.getExitsInRoom(session.is_in)

            try:
                self.flat = c.flatten(self.exists)
                if self.splitarg[1] in self.flat:
                    session.push("This exit already exists here.\r\n")
                else:
                    self.count = Insert.addRoom(self.splitarg[0])
                    Insert.addLink(session.is_in, self.count, self.splitarg[1])
                    Insert.addLink(self.count, session.is_in, self.twoway[self.splitarg[1]])
                    session.push("New room created %s of here.\r\n" % self.splitarg[1])
            except:
                session.push("Usage: edig <exit> <room name/short description>\r\n")

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
        if not line: session.push("Correct syntax:\r\nemail <name>\r\n")
        else:
            self.email = Select.getEmail(line.lower())
            if self.email:
                session.push("%s: %s\r\n" % (self.email[0], self.email[1]))
            else:
                session.push("Player not found.\r\n")

    def do_kickout(self, session, line):
        try:
            self.kicked = Select.getPlayerByName(line.lower())
            self.kick = self.sessions[self.kicked[0]]
            self.kick.shutdown(0)
        except:
            session.push("Player not found.\r\n")

    def do_import(self, session, line):		
        self.splitarg = line.split(' ', 2)
        if len(self.splitarg) < 3: session.push("Usage: import <file> <first room> <direction>\r\n")
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

                session.push("Map imported successfully.\r\n")

            else: session.push("Connected room not found on the map.\r\n")
