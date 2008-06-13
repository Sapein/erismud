import tables
from common import C
cu = tables.cu

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
			cu.execute( "insert into rooms(\
						id, s_desc, l_desc)\
						values (NULL,'A room','Set the description.')")
			session.push("Your new room has id #%d.\r\n" % cu.lastrowid)
		except:
			session.push("Something didn't work.\r\n")

	def do_delroom(self, session, line):
		try:
			cu.execute("select id from rooms where id = ?", (line,))
			fop = cu.fetchone()[0]
			cu.execute("delete from rooms where id = ?", (fop,))
			cu.execute("delete from links where origin = ? or dest = ?", (fop,))
			session.push("Room #%s and it's links have been deleted.\r\n" % (fop,))
		except:
			session.push("Unable to find this room.\r\nCorrect syntax: delroom <room ID>\r\n")

	def do_listrooms(self, session, line):
		cu.execute("select id, s_desc from rooms")
		self.whole = cu.fetchall()
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
			cu.execute( "insert into links(id, origin, dest, exit) values\
						(NULL, ?, ?, ?)", (self.roomnum, self.exitnum, self.direction))
			session.push("New link added.\r\n")
		except:
			session.push("Correct syntax: addlink <origin> <destination> <direction>\r\n")

	def do_listlinks(self, session, line):
		cu.execute("select * from links")
		self.linksall = cu.fetchall()
		session.push("%6s %6s %6s %4s\r\n" % ("ID", "ORIGIN", "DEST", "EXIT"))
		for i in self.linksall:
			session.push("%6s %6s %6s %4s\r\n" % (str(i[0]), str(i[1]), str(i[2]), str(i[3])))

	def do_dellink(self, session, line):
		if not line: session.push("Correct syntax: dellink <link ID>\r\n")
		self.todest = line.split(' ', 3)
		cu.execute("select * from links where id = ?", (self.todest[0], ))
		self.linker = cu.fetchall()
		if self.linker != []:
			cu.execute("delete from links where id = ?", (self.linker[0][0],))
			self.msg = "The link between Room #" + str(self.linker[0][0]) + " and Exit #" + str(self.linker[0][1]) + " going " + str(self.linker[0][2]) + " has been destroyed.\r\n"
			session.push(self.msg)
		else:
			session.push("This link does not exist.\r\n")

	def do_setshort(self, session, line):
		try:
			cu.execute("update rooms set s_desc = ? where id = ?", (line, session.is_in))
			session.push("Short description changed.\r\n")
		except: session.push("Unable to set the short description of this room.\r\n")

	def do_setlong(self, session, line):
		try:
			cu.execute("update rooms set l_desc = ? where id = ?", (line, session.is_in))
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
		cu.execute("select id,name,location,ip_addr from players where location > 0")
		self.all = cu.fetchall()

		session.push("%4s %10s %5s %4s\r\n" % ("ID", "NAME", "LOC", "IP"))
		for i in self.all:
			session.push("%4s %10s %5s %4s\r\n" % (str(i[0]), str(i[1]).capitalize(), str(i[2]), str(i[3])))

	def do_goto(self, session, line):
		try:
			cu.execute("select id from rooms where id = ?", (line,))
			self.exists = cu.fetchone()
			cu.execute("update players set location = ? where id = ?", (self.exists[0], session.p_id))
			session.is_in = self.exists[0]
		except: session.push("You cannot go there.\r\n")

	def do_additem(self, session, line):
		if not line: session.push("The object needs a name.\r\n")
		else:
			cu.execute("insert into objects(id,name,description) values\
					(NULL, ?, 'Set description')", (line.lower(),))
			session.push("Item %s has been created with ID #%s.\r\n" % (line.lower(), cu.lastrowid))

	def do_listitems(self, session, line):
		cu.execute("select id,name,description from objects")
		self.lookobj = cu.fetchall()

		session.push("%5s %10s %4s\r\n" % ("ID", "NAME", "DESC"))
		for i in self.lookobj:
			session.push("%5s %10s %4s\r\n" % (i[0], i[1], i[2][:20]))

	def do_delitem(self, session, line):
		cu.execute("select id,name from objects where id = ? or where name = ?", (line,line))
		self.barn = cu.fetchone()
		if self.barn != None: #If the object exists
			cu.execute("delete from objects where id = ?", (self.barn[0],))
			cu.execute("delete from obj_instances where o_id = ?", (self.barn[0],))
			session.push("%s and all its instances have been destroyed.\r\n" % self.barn[0])
		else:
			session.push("This object does not exist.\r\n")

	def do_itemdesc(self, session, line):
		try:
			self.splitarg = line.split(' ', 1)
			cu.execute("select name from objects where name = ?", (self.splitarg[0].lower(),))
			self.barn = cu.fetchone()
			if self.barn != None: #If the object exists
				cu.execute("update objects set description = ? where name = ?", (self.splitarg[1], self.splitarg[0].lower()))
				session.push("Description set on %s.\r\n" % str(self.splitarg[0]).lower())
			else: session.push("This object does not exist.\r\n")
		except: session.push("> ")

	def do_clone(self, session, line):
		cu.execute("select id,name from objects where name = ?", (line.lower(),))
		self.obj = cu.fetchone()
		cu.execute("select id,name from npcs where name = ?", (line.lower(),))
		self.npc = cu.fetchone()
		
		if self.obj:
			cu.execute("select id,name from objects where name = ?", (line.lower(),))
			self.cloner = cu.fetchone()
			cu.execute("insert into obj_instances(id,o_id,owner,creation) values\
						(NULL, ?, ?,?)", (self.cloner[0], session.p_id, time()))
			session.push("%s has been cloned.\r\n" % str(self.cloner[1]))
		elif self.npc:
			cu.execute("select id,name from npcs where name = ?", (line.lower(),))
			self.cloner = cu.fetchone()
			cu.execute("insert into npcs_instances(id,o_id,owner,creation) values\
						(NULL, ?, ?,?)", (self.cloner[0], session.p_id, time()))
			session.push("%s has been cloned.\r\n" % str(self.cloner[1]))
		else: session.push("No such object or NPC.\r\n")

	def do_list_oinst(self, session, line):
		cu.execute("select id,o_id,owner,location from obj_instances")
		self.instobj = cu.fetchall()

		session.push("%6s %6s %7s %9s\r\n" % ("ID", "OBJ", "OWNER", "LOC"))
		for i in self.instobj:
			session.push("%6s %6s %7s %9s\r\n" % (str(i[0]), str(i[1]), str(i[2]), str(i[3])))

	def do_dest_obj(self, session, line):
		cu.execute("select id from obj_instances where id = ?", [line])
		self.barn = cu.fetchone()
		if self.barn != None: #If the instance exists, try:
			try:
				cu.execute("delete from obj_instances where id = ?", (line,))
				session.push("Object Instance #%s has been destroyed.\r\n" % line)
			except: session.push("Object Instance #%s does not exist.\r\n" % line)
		else: pass
		
	def do_dest_npc(self, session, line):
		cu.execute("select id from npc_instances where id = ?", [line])
		self.barn = cu.fetchone()
		if self.barn != None: #If the instance exists, try:
			try:
				cu.execute("delete from npc_instances where id = ?", (line,))
				session.push("NPC Instance #%s has been destroyed.\r\n" % line)
			except: session.push("NPC Instance #%s does not exist.\r\n" % line)
		else: pass

	def do_addnpc(self, session, line):
		if not line: session.push("The NPC needs a name.\r\n> ")
		else:
			cu.execute("insert into npcs(id,name,description) values\
						(NULL, ?, 'Set description.')", (line.lower(),))
			session.push("NPC %s has been created with ID #%s.\r\n" % (line.lower(),cu.lastrowid))

	def do_npcdesc(self, session, line):
		if not line: session.push("Correct syntax: npcdesc <name> <description>\r\n")
		self.splitarg = line.split(' ', 1)
		cu.execute("select name from npcs where name = ?", (self.splitarg[0].lower(),))
		self.barn = cu.fetchone()
		if self.barn != None: #If the object exists
			try:
				cu.execute("update npcs set description = ? where name = ? or id = ?", (self.splitarg[1], self.splitarg[0].lower()))
				session.push("Description set on %s.\r\n" % str(self.splitarg[0]).lower())
			except: session.push("This NPC does not exist.\r\n")
		else: pass

	def do_delnpc(self, session, line):
		cu.execute("select id from npcs where id = ?", (line,))
		self.barn = cu.fetchone()
		self.splitarg = line.split(' ', 1)
		if self.barn != None: #If the object exists
			try:
				cu.execute("delete from npcs where id = ?", (line,))
				session.push("NPC #%s had been destroyed.\r\n" % line)
			except: session.push("This NPC does not exist.\r\n")
		else: pass

	# def do_clonenpc(self, session, line):
		# try:
			# cu.execute("select id,name from npcs where name = ?", (line.lower(),))
			# self.cloner = cu.fetchone()
			# cu.execute("insert into npc_instances(id,n_id,location) values\
						# (NULL, ?, ?)", (self.cloner[0], session.is_in))
			# session.push("%s cloned (Inst #%s).\r\n" % str(self.cloner[1]).capitalize(), cu.lastrowid)
		# except: session.push("No such NPC.\r\n")

	def do_listnpcs(self, session, line):
		cu.execute("select id,name,description from npcs")
		self.whole = cu.fetchall()

		session.push("%5s %10s %6s\r\n" % ("ID", "NAME", "DESC"))
		for i in self.whole:
			session.push("%5s %10s %6s\r\n" % (str(i[0]), str(i[1]), str(i[2])))

	def do_listplayers(self, session, line):
		cu.execute("select id,name,email from players")
		self.allplay = cu.fetchall()

		session.push("%5s %15s %20s\r\n" % ("ID", "NAME", "EMAIL"))
		for i in self.allplay:
			session.push("%5s %15s %20s\r\n" % (str(i[0]), str(i[1]), str(i[2])))

	def do_ridplayer(self, session, line):
		cu.execute("select id,name from players where name = ?", (line.lower(),))
		self.getrid = cu.fetchone()
		try:
			cu.execute("delete from players where name = ?", (self.getrid[1],))
			session.push("Player %s has been wiped out of the system.\r\n" % line.capitalize())
		except:
			session.push("Player %s not found in the database.\r\n" % line.capitalize())

	def do_edig(self, session, line):
		c = C(session)
		if not line: session.push("Usage: edig <exit> <room name/short description>\r\n")
		else:
			self.splitarg = line.split(' ', 1)
			cu.execute("select id,exit from links where origin = ?", (session.is_in,))
			self.exists = cu.fetchall()
			
			try:
				self.flat = c.flatten(self.exists)
				if self.splitarg[0] in self.flat:
					session.push("This exit already exists here.\r\n")
				else:
					cu.execute("insert into rooms(id, s_desc, l_desc) values(NULL,?,'Set description.')", (self.splitarg[1],))
					self.count = cu.lastrowid
					cu.execute("insert into links(id,origin,dest,exit) values(NULL,?,?,?)", (session.is_in, self.count, self.splitarg[0]))
					cu.execute("insert into links(id,origin,dest,exit) values(NULL,?,?,?)", (self.count, session.is_in, self.twoway[self.splitarg[0]]))
					session.push("New room created %s of here.\r\n" % self.splitarg[0])
			except:
				session.push("Usage: edig <exit> <room name/short description>\r\n")

	def do_addalias(self, session, line):
		if not line: session.push("Correct syntax: addalias <name> <alias>\r\n")
		else:
			line = line.lower()
			self.splitarg = line.split(' ', 1)

			cu.execute("select id,alias,name from objects where name = ?", (self.splitarg[0],))
			self.test = cu.fetchone()

			if self.test != []:
				try:
					if self.test[1] != None:
						self.add = "%s:%s" % (self.test[1], self.splitarg[1])
						cu.execute("update objects set alias = ? where name = ?", (self.add, self.splitarg[0]))
					else:
						cu.execute("update objects set alias = ? where name = ?", (self.splitarg[1], self.splitarg[0]))
				except: raise

	def do_email(self, session, line):
		if not line: session.push("Correct syntax:\r\nemail <name>\r\n")
		else:
			cu.execute("select name,email from players where name = ?", (line.lower(),))
			self.email = cu.fetchone()
			if self.email != []:
				session.push("%s: %s\r\n" % (str(self.email[0]), str(self.email[1])))
			else:
				session.push("Player not found.\r\n")

	def do_kickout(self, session, line):
		try:
			cu.execute("select id,name from players where name = ?", (line.lower(),))
			self.kicked = cu.fetchone()
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
					cu.execute( "insert into rooms(id, s_desc, l_desc) values (%s,'A room', 'No description')" % (int(i),))
							
				cu.execute( 'insert into links(origin, dest, exit) values ("%s", "%s", "%s")' % (str(session.is_in), str(self.start), str(self.dir)))
				cu.execute( 'insert into links(id, origin, dest, exit) \
							values (NULL, "%s", "%s", "%s")' % (self.start, str(session.is_in), str(self.twoway[self.dir])))
							
				for i in got_this.items():
					for j in i[1]:
						cu.execute('insert into links(id, origin, dest, exit) values (NULL, "%s", "%s", "%s")' % (str(i[0]), str(j[1]), str(j[0])))					
						
				session.push("Map imported successfully.\r\n")
				
			else: session.push("Connected room not found on the map.\r\n")
			
			
			

