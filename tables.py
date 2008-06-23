import os
# First try importing the sqlite2 version (Python 2.4)
# Then the version packed with Python 2.5.
try:
	from pysqlite2 import dbapi2 as sqlite
except ImportError:
	import sqlite3 as sqlite

if os.path.exists("data"):
	cx = sqlite.connect("data", isolation_level=None)
	cu = cx.cursor()
else:
	cx = sqlite.connect("data", isolation_level=None)
	cu = cx.cursor()
	
	cu.execute("CREATE TABLE players( 				\
				id 			INTEGER PRIMARY KEY,	\
				name 		TEXT NOT NULL ,			\
				email		TEXT NOT NULL ,			\
				passwd 		TEXT NOT NULL ,			\
				salt		TEXT NOT NULL ,			\
				location	INTEGER NOT NULL ,		\
				description TEXT ,					\
				colors		TEXT ,					\
				last_action TEXT ,					\
				ip_addr		TEXT ,					\
				banned		INTEGER)")
				
	cu.execute("CREATE TABLE rooms( 			\
				id		INTEGER PRIMARY KEY ,	\
				s_desc 	TEXT NOT NULL ,			\
				l_desc 	TEXT)")
				
	cu.execute("CREATE TABLE links( 			\
				id		INTEGER PRIMARY KEY ,	\
				origin	INTEGER ,				\
				dest	INTEGER ,				\
				exit	TEXT)")

	cu.execute("CREATE TABLE npcs( 					\
				id 			INTEGER PRIMARY KEY ,	\
				name		TEXT NOT NULL ,			\
				alias		TEXT ,					\
				description TEXT)")
				
	cu.execute("CREATE TABLE objects( 				\
				id			INTEGER PRIMARY KEY ,	\
				name		TEXT NOT NULL ,			\
				alias		TEXT ,					\
				description TEXT)")
	
	cu.execute("CREATE TABLE obj_instances( 		\
				id 		 	INTEGER PRIMARY KEY ,	\
				o_id	 	INTEGER ,				\
				owner	 	INTEGER ,				\
				npc_owner	INTEGER ,				\
				location	INTEGER ,				\
				creation	TEXT)")
	
	cu.execute("CREATE TABLE npc_instances( 		\
				id 			INTEGER PRIMARY KEY ,	\
				n_id		INTEGER ,				\
				location	INTEGER ,				\
				creation	TEXT)")

	cu.execute("CREATE TABLE skills( 			\
				id		INTEGER PRIMARY KEY ,	\
				name	TEXT NOT NULL)")
	
	# Create 2 basic rooms
	cu.execute( "insert into rooms(\
				id, s_desc, l_desc)\
				values (NULL,'first room','This is the first room')")
	cu.execute( "insert into rooms(\
				id, s_desc, l_desc)\
				values (NULL,'second room','This is the second room')")
				
	# Link the two rooms
	cu.execute( "insert into links(id, origin, dest, exit) values\
				(1, 1, 2, 'north')")
	cu.execute( "insert into links(id, origin, dest, exit) values\
				(2, 2, 1, 'south')")


	# Create the HELP database.
	cu.execute("create table helps(	\
				command TEXT,		\
				doc TEXT)")

	# Build basic help content.
	cu.execute("insert into helps(command,doc) values('look', 'Look command.')")
	cu.execute("insert into helps(command,doc) values('drop', 'drop <item>')")
	cu.execute("insert into helps(command,doc) values('say', 'say <text>')")
	cu.execute("insert into helps(command,doc) values('logout', 'Quit the MUD.')")
	cu.execute("insert into helps(command,doc) values('quit', 'Same as logout.')")
	cu.execute("insert into helps(command,doc) values('who', 'Players currently online.')")
	cu.execute("insert into helps(command,doc) values('description', 'description <your player description>')")
	cu.execute("insert into helps(command,doc) values('inv', 'Look at your inventory.')")
	cu.execute("insert into helps(command,doc) values('get', 'Get an item on the floor.')")
	cu.execute("insert into helps(command,doc) values('emote', 'emote <action>')")
	cu.execute("insert into helps(command,doc) values('give', 'give <item> to <player>')")
	cu.execute("insert into helps(command,doc) values('stats', 'Check your statistics.')")
	cu.execute("insert into helps(command,doc) values('setansi', 'Set your terminal to use ANSI colors or not.')")
	cu.execute("insert into helps(command,doc) values('skills', 'Get a list of your skills.')")
