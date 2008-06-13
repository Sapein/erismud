import tables, ConfigParser
from common import C
cu = tables.cu

config = ConfigParser.ConfigParser()
config.read("eris.conf")

class Actions:

	def __init__(self, sessions):
		self.sessions = sessions
		global Effects
		Effects = EffectsC(self.sessions)

	def do_chat(self, session, line):
		cu.execute("select id from players where location > 0")
		self.everybody = cu.fetchall()
		self.talker = session.BOLD+session.WHITE + session.pname + session.RESET
		for i in self.everybody:
			self.listen = self.sessions.get(i[0])
			if self.listen == None:
				pass
			else:
				self.listen.push(session.BOLD+session.GREEN+"["+session.RESET+ self.talker +session.BOLD+session.GREEN+"] "+session.RESET + line + "\r\n")

	def do_description(self, session, line):
		cu.execute("update players set description = ? where id = ?", (line, session.p_id))
		session.push("Description set.\r\n")

	def do_drop(self, session, line):
		try:
			cu.execute("select objects.name,oi.id from obj_instances oi, objects where oi.owner = ? and \
			objects.name = ? and objects.id = oi.o_id", (session.p_id, line.lower()))
			self.drop = cu.fetchone()
			
			cu.execute("update obj_instances set owner=NULL,location = ? where id = ?", (session.is_in, self.drop[1]))
			#self.msg = session.pname + " dropped " + line + "."
			#self.RoomBroadcast(session, session.is_in, self.msg)
			session.push(str(self.drop[0])+" dropped.\r\n")
		except: session.push("You cannot drop this.\r\n")

	def do_emote(self, session, line):
		if line == '' : session.push("You feel emotional.\r\n")
		else:
			self.emote = " " + line
			Effects.RoomBroadcast(session, session.is_in, self.emote)
			session.push("Emote: %s %s \r\n" % (session.pname, self.emote))

	def do_get(self, session, line):
		cu.execute("select id,o_id from obj_instances where location=? and owner is NULL and \
		o_id = (select id from objects where name = ?)", (int(session.is_in), line.lower()))
		self.objonfloor = cu.fetchone()
		
		try:
			cu.execute("update obj_instances set owner=?,location=NULL where id = ?", (session.p_id, self.objonfloor[0]))
			session.push("You pick up %s.\r\n" % line)
		except:
			session.push("This is not here.\r\n")

	def do_give(self, session, line):
		if not line: session.push("Correct syntax is: give <item> to <player>\r\n")
		else:
			self.argu = line.lower()
			#if not self.argu.strip(): session.push("> ")
			self.parts = line.split(' ', 3)

			if self.parts[1] == "to":
				try:
					cu.execute("select oi.id from obj_instances oi where \
								oi.owner = ? and \
								oi.o_id = (select id from objects where name = ?)", (session.p_id, self.parts[0].lower()))
					self.itom = cu.fetchone() # Given item info
					
					# Check if given to a player.
					cu.execute("select id from players where name = ? and location = ?", (self.parts[2].lower(), session.is_in))
					self.transf = cu.fetchone()
					
					# Check if given to a mob.
					cu.execute("select id from npc_instances ni where location = ? and \
							ni.n_id = (select id from npcs where name = ?)", (session.is_in, self.parts[2]))
					self.mob = cu.fetchone()

					if self.transf:
						cu.execute("update obj_instances set owner = ? where id = ?", (self.transf[0], self.itom[0]))
						session.push("You give %s to %s.\r\n" % (self.parts[0],self.parts[2]))
						self.RoomBroadcast(session, session.is_in, " gives %s to %s" % (self.parts[0],self.parts[2]))

					elif self.mob:
						cu.execute("update obj_instances set npc_owner = ?,owner=NULL where id = ?", (self.mob[0], self.itom[0]))
						session.push("You give %s to %s.\r\n" % (self.parts[0], self.parts[2]))
						Effects.RoomBroadcast(session, session.is_in, " gives %s to %s" % (self.parts[0], self.parts[2]))
					else: session.push("This person is not here.\r\n")

				except: session.push("Correct syntax is: give <item> to <player>\r\n")
	
			else: session.push("Correct syntax is: give <item> to <player>\r\n")

	def do_go(self, session, line):
		if not line: session.push("You don't go anywhere.\r\n")
		else:
			try:
				cu.execute("select origin, dest, exit from links where origin = ? and exit = ?", (session.is_in, line))
				self.isexit = cu.fetchone()
			except:
				session.push("No exit this way.\r\n")

			try:
				# Actually move
				Effects.RoomBroadcast(session, session.is_in, " leaves %s." % str(self.isexit[2]))
				cu.execute("update players set location = ? where id = ?", (self.isexit[1], session.p_id))
				session.is_in = self.isexit[1]
				Effects.RoomBroadcast(session, session.is_in, " enters the room.")
				self.do_look(session, '') # Force a look, to be replaced by something nicer.

			except: 
				session.push("You can't move that way.\r\n")

	def do_help(self, session, line):
		if not line: # help command alone
			cu.execute("select command from helps")
			self.allh = cu.fetchall()
			self.allhelp = []
			for i in self.allh:
				self.allhelp.append(i[0])

			self.allhelp.sort()
			self.counter = 0
			for i in self.allhelp:
				self.counter += 1

			#Make 2 columns of help files
			self.counter = self.counter / 2
			self.counter = int(self.counter)
			self.first = self.allhelp[:self.counter]
			self.second = self.allhelp[self.counter:]
			session.push("The following help topics exist:\r\n")
			for x, y in map(None, self.first, self.second):
				if x == None:
					x = ' '
					session.push(str(x).ljust(15) + str(y).ljust(10) + "\r\n")
				else: session.push(str(x).ljust(15) + str(y).ljust(10) + "\r\n")
				

		else: #If help <foo>
			try:
				cu.execute("select command, doc from helps where command = ?", line)
				self.helper = cu.fetchone()
				session.push("Help for " + line + ":\r\n")
				self.docu = self.helper[1].split('\\n')
				for i in self.docu:
					session.push(i + "\r\n")
				session.push("\r\n")
			except:
				session.push("Help is not available on this topic.\r\n")

	def do_inv(self, session, line):
		c = C(session)
		
		cu.execute("select objects.name from objects, obj_instances oi where \
					oi.owner = ? and objects.id = oi.o_id", (session.p_id,))
					
		self.owned = cu.fetchall()
		self.owned = c.flatten(self.owned)
		session.push(c.B_WHITE("Inventory\r\n"))
		
		self.stufa = {}
		for i in self.owned:
			self.stufa[i] = self.owned.count(i)

		for i in self.stufa:
			if self.stufa[i] > 1:
				c.B_GREEN(str(i))
				session.push("%s (%s)\r\n" % (c.B_GREEN(str(i)),str(self.stufa[i])))
			else:
				session.push("%s\r\n" % (c.B_GREEN(str(i)),))

	def do_look(self, session, line):
		c = C(session)
		if not line: # Looking at the room itself
			cu.execute("select s_desc,l_desc from rooms where id = ?", (session.is_in,))
			self.descr = cu.fetchone()
			session.push("%s \r\n" % (c.CYAN(self.descr[0]),))				# short desc
			session.push("%s \r\n" % self.descr[1].replace('\\n', '\r\n'))	# long desc
	
			# Players in the room.
			cu.execute("select name from players where location = ?", (session.is_in,))
			self.look_com = cu.fetchall()
			session.push("%s %s" % (session.BOLD, session.RED))
			for i in self.look_com:
				if str(i[0].capitalize()) == session.pname: pass
				else: session.push("%s \r\n" % str(i[0].capitalize()))
			session.push("%s" % session.RESET)
			
			#Get list of NPCs in the room.
			cu.execute("select name from npcs where id in (select n_id from npc_instances where location = ?)", [session.is_in])
			self.mobonfloor = cu.fetchall()
			
			#Get list of objects in the room.
			cu.execute("select name,oi.o_id,count(*) from objects,obj_instances oi where objects.id = oi.o_id \
			and oi.location = ?", (session.is_in,))
			self.objonfloor = cu.fetchall()
			
			if self.mobonfloor != []:
				for i in self.mobonfloor:
					session.push("%s%s%s %s\r\n" % (session.BOLD, session.MAGENTA, str(i[0]), session.RESET))

			if self.objonfloor != []:
				for i in self.objonfloor:
					if i[0] == None or i[1] == None: pass
					elif i[2] > 1:
						session.push("%s%s%s%s (%s) " % (session.BOLD,session.GREEN,str(i[0]),session.RESET,str(i[2])))
					else:
						session.push("%s%s%s%s" % (session.BOLD,session.GREEN,str(i[0]),session.RESET))
				session.push("\r\n")
				
			# List exits
			session.push("%s%sExits: " % (session.BOLD,session.CYAN))
			cu.execute("select exit from links where origin = ?", (session.is_in,))
			self.tmpgoto = cu.fetchall()
			for i in self.tmpgoto:
				session.push("%s " % i[0])
			session.push("%s\r\n" % session.RESET)

		else: # Looking at something specific
			#Check if looked-at player is there
			cu.execute("select id,description,location,name from players where name\
						 = ? and location = ?", (line.lower(), session.is_in))
			self.peeps = cu.fetchone()
			
			#Get list of items possessed by player or in the room
			cu.execute("select o.name, o.description from objects o, obj_instances oi where \
						o.id = oi.o_id and o.name = ? and oi.owner = ? or oi.location = ?", (session.p_id,line.lower(), session.is_in))
			self.obj = cu.fetchone()
			
			#Get list of mobs in the room.
			cu.execute("select npcs.name, npcs.description from npc_instances ni,npcs where \
			npcs.id = ni.n_id and npcs.name = ? and ni.location = ?", (line.lower(), session.is_in))
			self.mobonfloor = cu.fetchone()
		
			try:
				if self.peeps: #Looking at a player
					session.push("%s \r\n" % self.peeps[1].replace('\\n', '\r\n'))
					Effects.RoomBroadcast(session, session.is_in, " looks at " + line)
					
				elif self.obj: #An object in your inventory or on the floor
					session.push("%s \r\n" % self.obj[1].replace('\\n', '\r\n'))

				elif self.mobonfloor: #A mob/NPC
					cu.execute("select instances.parent_id,instances.sub_id,instances.is_owned,instances.is_in,\
								objects.obj_id,objects.name,instances.npc_own\
								from instances,objects where instances.sub_id = 1 and instances.is_owned = 0 and instances.parent_id = objects.obj_id\
								and instances.is_in = 0 and instances.npc_own = ?", [self.mobonfloor[0][7]])
					self.mobinv = cu.fetchall()

					self.descri = self.mobonfloor[0][6].split('\\n') # Print the description
					for i in self.descri:
						session.push(str(i) + "\r\n")

					if self.mobinv != []: # Print the mob's inventory
						self.stuff = []
						self.stufa = {}
						session.push(session.BOLD+session.WHITE+"Inventory:\r\n"+session.RESET)

						for i in self.mobinv:
							self.stuff.append(i[5])
							self.stufa[i[5]] = self.stuff.count(i[5])
						for i in self.stufa:
							if self.stufa[i] > 1:
								session.push(str(i) + " ("+str(self.stufa[i])+")" + "\r\n")
							else:
								session.push(str(i) + "\r\n")
					else: pass

				else: session.push("You do not see that here.\r\n")

			except: session.push("ERROR - You do not see that here.\r\n")

	def do_say(self, session, line):
		if not line: pass
		session.push("You say: %s \r\n" % line)
		Effects.RoomBroadcast(session, session.is_in, "says: %s" % line)

	def do_setansi(self, session, arg):
		if arg == "on":
			session.BLACK, session.RED, session.GREEN = '\033[30m', '\033[31m', '\033[32m'
			session.YELLOW, session.BLUE, session.MAGENTA = '\033[33m', '\033[34m', '\033[35m'
			session.CYAN, session.WHITE = '\033[36m', '\033[37m'
			session.RESET, session.BOLD = '\033[0;0m', '\033[1m'
			cu.execute("update players set colors = ? where id = ?", (arg, session.p_id))
		elif arg == "off": # Empty strings.
			session.BLACK, session.RED, session.GREEN, session.YELLOW, session.BLUE = '','','','',''
			session.MAGENTA, session.CYAN, session.WHITE, session.RESET, session.BOLD = '','','','',''
			cu.execute("update players set colors = ? where id = ?", (arg, session.p_id))
		else: session.push("Syntax:\r\nsetansi [off|on]\r\n")

	# def do_skills(self, session, line):
		# cu.execute("select * from skills where p_id = ?", (session.p_id,))
		# self.ski = cu.fetchone()
		# session.push("Your skills are:\r\n")
		# session.push("Loiter: "+str(self.ski[1])+"\r\n"+
					# "Whistle: "+str(self.ski[2])+"\r\n"+
					# "Spam: "+str(self.ski[2])+"\r\n")

	# def do_stats(self, session, line):
		# cu.execute("select names,str,stm,dex,agl,int,wil,prs,per,app from pnames where p_id = ?", [session.p_id])
		# self.stats = cu.fetchone()
		# session.push(session.BOLD+session.WHITE+"Stats for " + str(self.stats[0].capitalize()) +session.RESET+"\r\n")
		# session.push("STR: " + str(self.stats[1]) + "\r\n")
		# session.push("STM: " + str(self.stats[2]) + "\r\n")
		# session.push("DEX: " + str(self.stats[3]) + "\r\n")
		# session.push("AGL: " + str(self.stats[4]) + "\r\n")
		# session.push("INT: " + str(self.stats[5]) + "\r\n")
		# session.push("WIL: " + str(self.stats[6]) + "\r\n")
		# session.push("PRS: " + str(self.stats[7]) + "\r\n")
		# session.push("PER: " + str(self.stats[8]) + "\r\n")
		# session.push("APP: " + str(self.stats[9]) + "\r\n")

	def do_who(self, session, line):
		c = C(session)
		session.push("The following players are logged on:\r\n")
		cu.execute("select name from players where location > 0")
		self.whoin = cu.fetchall()
		for i in self.whoin:
			session.push("%s\r\n" % (c.B_RED(i[0].capitalize()),))
		session.push("\r\n")

	# Shortcuts
	def do_n(self, session, line): self.do_go(session, 'north')
	def do_s(self, session, line): self.do_go(session, 'south')
	def do_w(self, session, line): self.do_go(session, 'west')
	def do_e(self, session, line): self.do_go(session, 'east')
	def do_u(self, session, line): self.do_go(session, 'up')
	def do_d(self, session, line): self.do_go(session, 'down')
	def do_se(self, session, line): self.do_go(session, 'southeast')
	def do_sw(self, session, line): self.do_go(session, 'southwest')
	def do_nw(self, session, line): self.do_go(session, 'northwest')
	def do_ne(self, session, line): self.do_go(session, 'northeast')
	do_north = do_n
	do_south = do_s
	do_west = do_w
	do_east = do_e
	do_up = do_u
	do_down = do_d
	do_i = do_inv
	do_l = do_look



### Proof Of Concept


	def do_loiter(self, session, line):
		# Example of an action depending on a skill.
		# Skills vary between 1-20. Throw 1D20:
		cu.execute("select loiter from skills where p_id = ?", [session.p_id])
		self.curskill = cu.fetchone()[0]
		self.die = randrange(1, 20)
		# If the result is lower than the skill, it's successful.
		if self.die < self.curskill:
			self.do_emote(session, "loiters")
		else:
			session.push("You fail to loiter.\r\n")

	def do_maim(self, session, line):
		# Proof of concept for a basic damage system.
		# Lose 3 HPs then call heal(), which will heal 1 HP every 10 second until back to normal.
		session.push("You damage yourself and lose 3 HPs.\r\n")
		cu.execute("select curhp,maxhp from pnames where p_id = ?", [session.p_id])
		self.health = cu.fetchone()
		self.current = self.health[0] - 3
		session.push("Current HP: " + str(self.current) + "\r\n")
		session.push("Max HP: " + str(self.health[1]) + "\r\n")
		cu.execute("update pnames set curhp = ? where p_id = ?", (self.current, session.p_id))

		self.heal(session, '')

	def do_juggle(self, session, line):
		print type(self), dir(self)
		self.skich = self.skillcheck(session, "juggling", 60)
		if self.skich[0] == "success":
			Effects.RoomBroadcast(session, session.is_in, " juggles")
			session.push("You juggle.\r\n")
		elif self.skich[0] == "fail":
			Effects.RoomBroadcast(session, session.is_in, " fails to juggle")
			session.push("You fail to juggle.\r\n")

	def do_duchie(self, session, line):
		if line == '': session.push("A skill is needed in argument.\r\n")
		try:
			cu.execute("select ? from learningpts where p_id = ?", (line, session.p_id))
			self.duchie = cu.fetchone()[0]
			session.push("Learning points in " + line + ": " + str(self.duchie) + "\r\n")
		except:
			session.push("You do not have that skill.\r\n")


class EffectsC:

	def __init__(self, sessions):
		self.sessions = sessions

	def RoomBroadcast(self, session, inroom, line):
		"By calling this method, 'line' is sent to all players in 'inroom'."
		c = C(session)

		cu.execute("select id from players where location = ?", (inroom,))
		self.local = cu.fetchall()
		self.pnamer = c.B_WHITE(session.pname)
		if not line:
			pass
		else:
			for i in self.local:
				self.tmpses = self.sessions.get(i[0]) # sessions dict
				if not self.tmpses: # Player is not logged in
					pass
				elif self.tmpses.p_id == session.p_id: # Is the player
					pass
				else:
					self.tmpses.push("%s %s\r\n" % (self.pnamer,line))


	def skillcheck(self, session, pskill, diff):
		self.skassoc = {'disguise': 'app', 'juggling':'dex', 'evasion':'per', 'dodge':'agl'}

		#toDo = 'SELECT ? FROM skills WHERE p_id = ?'
		#print "pskill", pskill
		#cu.execute('SELECT juggling FROM skills WHERE p_id = ?', session.p_id)
		cu.execute("select ? from skills where p_id = ?", (pskill, session.p_id))
		self.skill = cu.fetchone()[0]
		print 'skill', self.skill
		self.assoc = self.skassoc[pskill]
		cu.execute("select * from pnames where p_id = ?", [session.p_id])
		cu.execute("select ? from pnames where p_id = ?", [self.assoc, session.p_id])
		self.stat = cu.fetchone()[0]
		print 'stat', self.stat

		cu.execute("select * from skills")
		print cu.fetchall()

		self.roll = randrange(1, 6) + randrange(1, 6) + randrange(1, 6) + randrange(1, 6) + randrange(1, 6) + randrange(1, 6)
		self.subtotal = self.skill + self.stat + self.roll
		self.bonus = self.roll
		self.malus = 0
		self.skillp = 0
		if self.roll >= 26:
			self.roll2 = randrange(1, 30)
			self.bonus += self.roll2
			self.skillp += randrange(1, 3) + 1

			if self.roll2 >= 28:
				self.roll3 = randrange(1, 20)
				self.bonus += self.roll3
				self.skillp += randrange(1, 3) + + randrange(1, 3) + 2

				if self.roll3 == 20:
					self.bonus += randrange(1, 10)
					self.skillp += randrange(1, 3) + randrange(1, 3) + randrange(1, 3) + 3

		elif self.roll <= 9:
			self.roll2 = randrange(1, 30)
			self.malus += self.roll2
			self.skillp += randrange(1, 3) + 1

			if self.roll2 <= 3:
				self.roll3 = randrange(1, 20)
				self.malus += self.roll3
				self.skillp += randrange(1, 3) + + randrange(1, 3) + 2

				if self.roll3 == 1:
					self.malus += randrange(1, 10)
					self.skillp += randrange(1, 3) + randrange(1, 3) + randrange(1, 3) + 3

		self.total = self.subtotal + self.bonus - self.malus

		if self.total >= diff:
			self.skillp += randrange(1, 4) + randrange(1, 4) + 2
			# DEBUG
			#session.push("Die throw: " + str(self.total) + "\r\n")
			#session.push("Skill: " + str(self.skill) + "\r\n")
			#session.push("Learning points: " + str(self.skillp) + "\r\n")
			#cu.execute("update learningpts set ? = ? where p_id = %?" % pskill, self.skillp, session.p_id)
			cu.execute("select ? from learningpts where p_id = ?", (pskill, session.p_id))
			self.current = cu.fetchone()[0] + self.skillp
			cu.execute("update learningpts set ? = ? where p_id = ?", (pskill, self.current, session.p_id))
			return ("success", self.skillp)
		else:
			self.skillp += 1
			# DEBUG
			#session.push("Die throw: " + str(self.total) + "\r\n")
			#session.push("Skill: " + str(self.skill) + "\r\n")
			#session.push("Learning points: " + str(self.skillp) + "\r\n")
			cu.execute("select ? from learningpts where p_id = ?", (pskill, session.p_id))
			self.current = cu.fetchone()[0] + self.skillp
			cu.execute("update learningpts set ? = ? where p_id = ?", (pskill, self.current, session.p_id))
			return ("fail", self.skillp)
