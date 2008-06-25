import tables
cu = tables.cu

class Select:
    def getAllPlayers(self):
        cu.execute("select id from players where location > 0")
        return cu.fetchall()
    
    def getItem(self, session, item):
        cu.execute("select id,o_id from obj_instances where location=? and owner is NULL and \
        o_id = (select id from objects where name = ?)", (int(session.is_in), item))
        return cu.fetchone()
    
    def getExit(self, session, exit):
        cu.execute("select origin, dest, exit from links where origin = ? and exit = ?", (session.is_in, exit))
        return cu.fetchone()
    
    def getHelp(self, command):
        cu.execute("select command, doc from helps where command = ?", (command,))
        return cu.fetchone()
    
    def getAllHelp(self):
        cu.execute("select command from helps")
        return cu.fetchall()

class Update:
    
    def setDescription(self, session, line):
        cu.execute("update players set description = ? where id = ?", (line, session.p_id))
        
    def setItemOwner(self, session, new_owner, obj_id):
        cu.execute("update obj_instances set owner = ?, location = NULL, npc_owner = NULL where id = ?", (new_owner, obj_id))

    def setItemNpcOwner(self, session, new_owner, obj_id):
        cu.execute("update obj_instances set npc_owner = ?, location = NULL, owner = NULL where id = ?", (new_owner, obj_id))
        
    def dropItem(self, session, obj_id):
        cu.execute("update obj_instances set owner = NULL, location = ?, npc_owner = NULL where id = ?", (session.is_in, obj_id))
        
    def setLocation(self, session, where):
        cu.execute("update players set location = ? where id = ?", (where, session.p_id))
        
    def setColors(self, session, color):
        cu.execute("update players set colors = ? where id = ?", (color, session.p_id))