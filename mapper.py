import re
import xml.dom.minidom
from xml.dom.minidom import getDOMImplementation, parse, parseString, Document

class NotTextNodeError:
	pass

class Mapper:

	def __init__(self, file):
		self.file = file
	
	def MapThis(self):

		allLines = {}
		allRooms = {}

		linecount = 1
		for liner in self.file:
			if "####" in liner: break

			allLines[linecount] = liner
			linecount += 1

		for line in allLines:
			for i in re.finditer("\[(\d+)\]", allLines[line]):
				allRooms[i.group(1)] = []
			
		for line in allLines:
		
			hor = re.compile("(?=\[(\d+)\]\-+\[(\d+)\])")
			ew = hor.findall(allLines[line])
			if ew != []: 
				for combo in ew:
					allRooms[combo[0]].append(('east', combo[1]))
					allRooms[combo[1]].append(('west', combo[0]))
					
			for i in re.finditer("\[(\d+)\]", allLines[line]):
				loc = i.start()
				end = i.end()
				
				try:	# Finds all North-South connections
					for x in range(line - 1, 0, -1):
						if allLines[line-1][loc+1] == "|" and allLines[x][loc+1].isdigit():
							gg = re.compile("\[(\d+)\]").search(allLines[x], loc)
							
							allRooms[i.group(1)].append(('north', gg.group(1)))
							allRooms[gg.group(1)].append(('south', i.group(1)))
							break
				except: pass
				
				try:	# Finds all NE-SW connections
					offset = 2
					if allLines[line-1][end] == "/":
						for x in range(line - 2, 0, -1):
							if allLines[x][end+offset].isdigit():
								gg = re.compile("\[(\d+)\]").search(allLines[x], end)
								
								allRooms[i.group(1)].append(('northeast', gg.group(1)))
								allRooms[gg.group(1)].append(('southwest', i.group(1)))
								break
							else:
								offset += 1
				except: pass				
		
				try:	# Finds all NW-SE connections
					offset = 3
					if allLines[line-1][loc-1] == "\\":
						for x in range(line - 2, 0, -1):
							if allLines[x][loc-offset].isdigit():
								gg = re.compile("\[(\d+)\]").search(allLines[x], loc-offset-5)
								
								allRooms[i.group(1)].append(('northwest', gg.group(1)))
								allRooms[gg.group(1)].append(('southeast', i.group(1)))
								break
							else:
								offset += 1
				except: pass		
		
		return allRooms
		
	def GetXml(self, rawXml):
		try:
			domf = parseString(rawXml)
		except: #Malformed XML
			raise	
			
		for i in domf.childNodes:
			if i.nodeType != i.ELEMENT_NODE:
				continue
				
			
			
		#print domf.documentElement.tagName
		#root = domf.getAll("rooms")
		#print getElementsByTagName("rooms")
		
		#if root:
		#	db = root[0]
		#	print db
			# print "Rooms:", db["name"]
			# for table in db.getAll("table"):
				# print "  Table:", table["name"]
				# for field in db.getAll("field"):
					# print "    Field:", field["name"], "- Type:", field["type"]
				
		domf.unlink()
		
		
if __name__ == '__main__':
	filer = open("map3.txt", "r")
	mp = Mapper(filer)
	#map = mp.MapThis()
	
	stuff = filer.read()
	eof = re.compile("(\#\#\#\#)")
	res = eof.search(stuff)
	
	if res != None:
		mp.GetXml(stuff[res.end(1):])
	
	#mp.GetXml()
	
	
	
	
	
	
	
	