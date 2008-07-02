import sys, os

import xml.dom.minidom
from xml.dom.minidom import getDOMImplementation

# try:
	# import xml.etree.ElementTree as ET
# except ImportError:
	# print "Unable to load xml.etree.ElementTree. You will be unable to load or save XML"
	# raw_input()

statsD = {}
othersD = {}
skillsD = {}
classesD = {}
racesD = {}
optionsD = {'opt1':'[ ]', 'opt2':'[ ]', 'opt3':'[ ]', 'opt4':'[ ]', 'opt5':'  '}

currentmenu = None

# TODO: Define the standard die throw for skill and stat checks.

class Menu(object):
	def __init__(self, parent, keyitems):
		keys, items = zip(*keyitems)
		for item in items:
			item.parent = self
		self.parent = parent
		self.items = list(items)
		self.actions = dict(keyitems)
	
	def draw_menu(self):
		itemdescs = []
		for item in self.items:
			itemdescs.append(item.get_label())
		maxlen = max(map(len, itemdescs))
		print "\t" + "-" * (maxlen + 4)
		for line in itemdescs:
			linelen = len(line)
			if line and line[0] == "-":
				print "\t|%s|" % ("-" * (maxlen+2))
			else:
				print "\t| %s%s%s |" % ( " " * ((maxlen-linelen)/2), line, " " * ((maxlen+1-linelen)/2))
		print "\t" + "-" * (maxlen + 4)

	def handle_response(self, response):
		try:
			self.actions[response.lower()].call()
		except KeyError:
			print "Invalid option"

	def close(self):
		global current_menu
		current_menu = self.parent

	def add_item(self, key, item):
		self.items.append(item)
		self.actions[key] = item
		item.parent = self

class MenuItem(object):
	def __init__(self, label, function):
		self.label = label
		self.function = function
		self.parent = None

	def call(self):
		self.function()
	
	def get_label(self):
		return self.label

class SubMenu(MenuItem, Menu):
	def __init__(self, label, keyitems):
		def set_menu():
			global current_menu
			current_menu = self
		Menu.__init__(self, None, keyitems)
		MenuItem.__init__(self, label, set_menu)

class FormattedMenuItem(MenuItem):
	def __init__(self, label, optionDict, function):
		self.label = label
		self.optionDict = optionDict
		self.function = function

	def get_label(self):
		return self.label % self.optionDict

class CloseMenuItem(MenuItem):
	def __init__(self, label):
		self.label = label

	def call(self):
		self.parent.close()

def showMain():
	while True:
		clear()
		current_menu.draw_menu()
		inp = raw_input("#> ")
		current_menu.handle_response(inp)

def typeofStat():
	while True:
		c = raw_input("(P)hysical stat, (M)ental stat or (O)ther stat: ")

		if c.lower() == "p":
			return "Physical"
		elif c.lower() == "m":
			return "Mental"
		elif c.lower() == "o":
			return "Other"

def addStat():
	a = raw_input("Full name of the stat you want to add: ")
	b = raw_input("Abbreviation of this stat: ")
	c = typeofStat()

	print "New Stat: " + a + " (" + b +"), " + c + "\r\n"
    
	r = raw_input("Is this correct? (Y/N) ")
    
	if r.lower() == "y":
		statsD[a] = (b, c)
	    
	elif r.lower() == "n":
		print "Not saving the new stat.\r\n"


def delStat():
	print "Current defined stats: "
	for i in statsD: print i
	print "\r\n"
	d = raw_input("Which stat do you want to delete? ")
	try:
		del statsD[d]
		print "Stat " + d + " deleted successfully.\r\n"
		statsMenu()
	except:
		print "No such stat.\r\n"
		statsMenu()

def set_points_per_level():
        cnpts = raw_input("How many Stat points every level: ")
        if len(cnpts) == 1: 
					cnpts = " " + cnpts
        optionsD['opt5'] = cnpts
        optionsD['opt3'] = "[X]"
        optionsD['opt4'] = "[ ]"
	
def set_stats_per_level():	
        optionsD['opt3'] = "[ ]"
        optionsD['opt4'] = "[X]"
        optionsD['opt5'] = "  "

def addSkill():
    a = raw_input("\r\nEnter the Skill name: ")
    bu = ""
    if len(statsD) > 0:
        for i in statsD:
            bu += i + "  "
        bu += "\r\n"
        print bu
            
        b = raw_input(a + " will be dependent of which Stat? ")
        if b in statsD:
            print a + " is now dependent of " + b + "\r\n"
            skillsD[a] = b

            rr = raw_input("<Press any key>")
            #skillsMenu()
            
        else:
             print "This Stat does not exist.\r\n"
             rr = raw_input("<Press any key>")
             #skillsMenu()

        
    else:
        print "You need to have at least one Stat defined.\r\n"
        #skillsMenu()

def viewSkills():
    print "List of currently defined skills\r\n"
    for i in skillsD:
        print i + "\t=>\t" + skillsD[i]

    rr = raw_input("<Press any key>")
    #skillsMenu()


def delSkill():
    for i in skillsD:
        print i
    d = raw_input("Delete which skill? ")
    try:
        del skillsD[d]
    except:
        print "Skill deleted.\r\n"
        rr = raw_input("<Press any key>\r\n")
        #skillsMenu()

def set_skill_range():
        minisk = raw_input("Minimum value of a skill: ")
        maxisk = raw_input("Maximum value of a skill: ")
        
        othersD['minisk'] = minisk
        othersD['maxisk'] = maxisk


def set_starting_skill_points():
        print "This option sets how many skill points or levels a new character will start with.\r\n"
        startsk = raw_input("How many starting skill points? ")
        othersD['StartingSkPts'] = startsk
        print "Starting skill points defined to " + str(startsk) + ".\r\n"


def set_type_of_skill_advancement():
        print "This option allows you to set how the skills will improve.\r\n"

        print """
        Choose an option:
        (A) Skills improve over time, every successful use adds some points
            towards the next level.
        (B) Skill points are given when the user gains a level (ex. AD&D).
        (C) Skills are improved using standard Points, which are used to
            raise Stats and other characteristics (ex. White Wolf, Shadowrun).
        """
    

def add_race():
        rana = raw_input("\r\nEnter the new Race name: ")

        #racesD[rana] = 

        print "Race " + rana + " created.\r\n"
        rr = raw_input("<Press any key>")
        
def del_race():
        rade = raw_input("\r\nEnter the Race name to delete: ")
        try:
            del racesD[rade]
            print rade + " Race deleted.\r\n"
            rr = raw_input("<Press any key>")
        except:
            print "Race not found.\r\n"
            rr = raw_input("<Press any key>")
            
def view_races():
        print "The following races have been defined:\n"
        for i in racesD:
            print i + " "

        rr = raw_input("\r\n<Press any key>")

def classesMenu():
    clear()
    print """
    ----------------------
    | Add Class (a)      |
    | Delete Class (d)   |
    | Class options (o)  |
    | View Classes (v)   |
    | Return to Main (r) |
    ----------------------
    """

    opt = raw_input("#> ")

def add_class():
        print "If classes have race restriction (ex. AD&D), you should setup Races first.\r\n"
        clna = raw_input("\r\nEnter the new Class name: ")

        clra = raw_input("Races allowed to join that Class ('*' for all).\nSeparate the Races with commas: ")

        classesD[clna] = clra.split(",")

        print "Class " + clna + " created.\r\n"
        rr = raw_input("<Press any key>")
        
def del_class():
        clde = raw_input("\r\nEnter the Class name to delete: ")
        try:
            del classesD[clde]
            print clde + " Class deleted.\r\n"
        except:
            print "Class not found.\r\n"
        rr = raw_input("<Press any key>")
    
def view_classes():
        stringa = ""
        for i in classesD:
            stringa += i + " \t\t | Restricted to: "
            for j in classesD[i]:
                stringa += j + " "
            stringa += "\n"

        print stringa
                
        rr = raw_input("<Press any key>")
    

def exportXml():
	filen = raw_input("Filename: ")
	
	impl = getDOMImplementation()
	doc = impl.createDocument(None, "world", None)
	root = doc.documentElement
	
	# Main Stats Element
	stats = doc.createElement("Stats")
	try:
		stats.setAttribute("Minimum", othersD['mini'])
		stats.setAttribute("Maximum", othersD['maxi'])
	except: pass
	try:
		stats.setAttribute("StartingMin", othersD['minStart'])
		stats.setAttribute("StartingMax", othersD['maxStart'])
	except: pass
	root.appendChild(stats)
	
	# Child Stat Nodes
	for i in statsD:
		try:
			stat = doc.createElement("Stat")
			stat.setAttribute("Name", i)
			stat.setAttribute("Abbrev", statsD[i][0])
			stat.setAttribute("Type", statsD[i][1])
			stats.appendChild(stat)
		except: pass
	
	# Main Skills Element
	skills = doc.createElement("Skills")
	try:
		skills.setAttribute("Minimum", othersD['minisk'])
		skills.setAttribute("Maximum", othersD['maxisk'])
	except: pass
	try: skills.setAttribute("StartingPoints", othersD['StartingSkPts'])
	except: pass
	
	for j in skillsD:
		try:
			sk = doc.createElement("Skill")
			sk.setAttribute("Name", j)
			sk.setAttribute("Uses", skillsD[j])
			skills.appendChild(sk)
		except: pass
	
	xmlfile = open("%s.xml" % filen, "w")
	xmlfile.write(root.toprettyxml("\t", "\r\n"))
	xmlfile.close()
	
	#showMain()
	
	
	

# def exportXmlOld():
    # filen = raw_input("Filename: ")

    # root = ET.Element("world")
    
    #Add the stats
    # stats = ET.SubElement(root, "Stats")
    # try:
        # stats.set("Minimum", othersD['mini'])
        # stats.set("Maximum", othersD['maxi'])
    # except: pass
    # try:
        # stats.set("StartingMin", othersD['minStart'])
        # stats.set("StartingMax", othersD['maxStart'])
    # except: pass

    # for i in statsD:
        # try:
            # st = ET.SubElement(stats, "Stat")
            # st.text = i
            # st.set("Abbrev", statsD[i][0])
            # st.set("Type", statsD[i][1])
        # except: pass

    #Add the skills
    # try:
		# skills = ET.SubElement(root, "Skills")
        # skills.set("Minimum", othersD['minisk'])
        # skills.set("Maximum", othersD['maxisk'])
    # except: pass
    
    # try: skills.set("StartingPoints", othersD['StartingSkPts'])
    # except: pass

    # for j in skillsD:
        # try:
            # sk = ET.SubElement(skills, "Skill")
            # sk.text = j
            # sk.set("Uses", skillsD[j])
        # except: pass

    #Add the classes
    # try: classes = ET.SubElement(root, "Classes")
	# except: pass
    # for z in classesD:
        # try:
            # cl = ET.SubElement(classes, "Class")
            # cl.text = z
            # cl.set("RacesAllowed", str(classesD[z][0]))
        # except: pass

    #General Options
    # options = ET.SubElement(root, "Options")
    # creationst = ET.SubElement(options, "CharCreation")
    # if optionsD['opt1'] == "[X]":
        # creationst.set("CreationStyle", "Points")
        # opti = ET.SubElement(creationst, "CharacterCreationPoints")
        # opti.text = othersD['StartingStatPoints']

    # elif optionsD['opt2'] == "[X]":
        # creationst.set("CreationStyle", "DieRoll")
        # opti = ET.SubElement(creationst, "Sides")
        # opti.text = othersD['StartingStatSides']
        # opti2 = ET.SubElement(creationst, "Dice")
        # opti2.text = othersD['StartingStatDice']
    # else: pass

    #Bonus Stat Points given every new character level
    # try:
        # rr = str(optionsD['opt5']).lstrip()
        # advsec = ET.SubElement(options, "Advancement")
        # advsec2 = ET.SubElement(advsec, "StatPoints")
        # advsec2.set("PerLevel", rr)
    # except: pass
    
    # tree = ET.ElementTree(root)
    # tree.write(filen + ".xhtml")

    # showMain()

def loadXml():
    filen = raw_input("File to load: ")

    tree = ET.parse(filen + ".xhtml")

    root = tree.getroot()

    statsD.clear()
    othersD.clear()
    skillsD.clear()
    classesD.clear()
    #optionsD.clear()

    # Load Stats info
    for i in tree.findall("Stats/Stat"):
        statsD[i.text] = (i.get('Abbrev'), i.get('Type'))
    
    # Load Skills info
    for j in tree.findall("Skills/Skill"):
        skillsD[j.text] = j.get('Uses')

    # Load Class info
    for h in tree.findall("Classes/Class"):
        classesD[h.text] = h.get([RacesAllowed])

    # Load stats/skills options

    for i in tree.findall("Stats"):
        if i.get('Maximum'):
            othersD['maxi'] = i.get('Maximum')
            othersD['mini'] = i.get('Minimum')
        if i.get('StartingMin'):
            othersD['minStart'] = i.get('StartingMin')
            othersD['maxStart'] = i.get('StartingMax')
        
    for j in tree.findall("Skills"):
        if j.get('Minimum'):
            othersD['minisk'] = j.get('Minimum')
            othersD['maxisk'] = j.get('Maximum')

        if j.get('StartingPoints'):
            othersD['StartingSkPts'] = j.get('StartingPoints')

    # Load other options
    for k in tree.findall("Options"):
        if k.get("CreationStyle") == "Points":
            optionsD['opt1'] = "[X]"
            optionsD['opt2'] = "[ ]"
            
            for l in tree.findall("Options/CharacterCreationPoints"):
                othersD['StartingStatPoints'] = l.text
           
        elif k.get("CreationStyle") == "DieRoll":
            optionsD['opt2'] = "[X]"
            optionsD['opt1'] = "[ ]"

            for m in tree.findall("Options/Sides"):
                othersD['StartingStatSides'] = m.text

            for n in tree.findall("Options/Dice"):
                othersD['StartingStatDice'] = n.text

    if tree.findall("Options/Advancement/StatPoints"):
        foop = tree.findall("Options/Advancement/StatPoints")[0]
        optionsD['opt5'] =  int(foop.get("PerLevel"))
        "PerLevel", optionsD['opt5']

    showMain()


def clear():
    import os
    if os.name == "posix":
        os.system('clear')
    elif os.name in ("nt", "dos", "ce"):
        os.system('CLS')
    else: pass

def showStats():
	for i in statsD:
		print "%i\t%s\t%s" % (i, statsD[i][0], statsD[i][1])
	print "\r\n"
	rr = raw_input("<Press any key>")

def get_min_start_vals():
				print """This option defines the starting Stats range when creating \
a new character. All stats will be randomized between these \
two values when generating a character.\r\n"""

				minis = raw_input("Minimum starting value: ")
				maxis = raw_input("Maximum starting value: ")

				othersD['minStart'] = minis
				othersD['maxStart'] = maxis

				print "Starting range defined.\r\n"
	

def set_point_allocation():
	optionsD['opt1'] = '[X]'
	optionsD['opt2'] = '[ ]'

	zz = raw_input("How many points to allocate in the stats?")
	othersD['StartingStatPoints'] = zz

def set_die_allocation():
	optionsD['opt1'] = '[ ]'
	optionsD['opt2'] = '[X]'

	print "Every stat is generated randomly with a dice roll.\r\n"
	zz = raw_input("How many sides per die? ")
	yy = raw_input("How many dice? ")
	othersD['StartingStatSides'] = zz
	othersD['StartingStatDice'] = yy
	
def set_stats_range():
	mini = raw_input("Minimum value of a stat: ")
	maxi = raw_input("Maximum value of a stat: ")

	othersD['mini'] = mini
	othersD['maxi'] = maxi

	print "Stats range defined.\r\n"

def unimplemented():
	print "This menu item hasn't been implemented yet."
	raw_input("Press enter to continue")
	
	
### Menu definitions

adv_options = SubMenu("Stats Improvement (i)", [
		('a', FormattedMenuItem("%(opt3)s %(opt5)2s Points every level (a)", optionsD, set_points_per_level)),
		('b', FormattedMenuItem("%(opt4)s Using the stats [OFF] (b)", optionsD, set_stats_per_level)),
		('r', CloseMenuItem("Return to Stats Options (r)")),
		])

stats_options_menu = SubMenu("Stats Options (o)", [
		(None, MenuItem('CHARACTER CREATION',None)),
		(None, MenuItem("", None)),
		('t', MenuItem("Set Starting Range (t)", get_min_start_vals)),
		('x', FormattedMenuItem("%(opt1)s Distributed Points (x)", optionsD, set_point_allocation)),
		('y', FormattedMenuItem("%(opt2)s Die rolls (y)", optionsD, set_die_allocation)),
		(None, MenuItem("----------", None)),
		('s', MenuItem("Set Stats Range (s)", set_stats_range)),
		('i', adv_options),
		(None, MenuItem("----------", None)),
		('r', CloseMenuItem("Return to Stats Menu (r)")),
		])
#stats_options_menu.add_item('r', MenuItem("Return to Stats Menu (r)", stats_options_menu.close))


stats_menu = SubMenu("Stats (a)", [
                                    ('a', MenuItem("Add Stat (a)", addStat)),
									('d', MenuItem("Delete Stat (d)", delStat)),
									('o', stats_options_menu),
                                    ('v', MenuItem("View Stats (v)", showStats)),
									('r', CloseMenuItem("Return to Main (r)"))
									])

skill_options = SubMenu("Skill options (o)", [
									('s', MenuItem("Set Skills Range", set_skill_range)),
									('t', MenuItem("Set Starting Skill Points (t)", set_starting_skill_points)),
									('a', MenuItem("Set Type of Advancement", set_type_of_skill_advancement)),
									('r', CloseMenuItem("Return to Skills Menu (r)")),
									])

skills_menu = SubMenu("Skills (s)", [
									('a', MenuItem("Add Skills(a)", addSkill)),
									('d', MenuItem("Delete Skills (d)", delSkill)),
									('o', skill_options),
									('v', MenuItem("View Skills (v)", viewSkills)),
									('r', CloseMenuItem("Return to Main (r)")),
									])

races_menu = SubMenu("Races [OFF] (r)", [
									('a', MenuItem("Add Race (a)", add_race)),
									('d', MenuItem("Delete Race (d)", del_race)),
									('o', MenuItem("Race options (o)", unimplemented)),
									('v', MenuItem("View Races (v)", view_races)),
									('r', CloseMenuItem("Return to Main (r)")),
									])

classes_menu = SubMenu("Classes (p)", [
									('a', MenuItem("Add Class (a)", add_class)),
									('d', MenuItem("Delete Class (d)", del_class)),
									('o', MenuItem("Class options (o)", unimplemented)),
									('v', MenuItem("View Classes (v)", view_classes)),
									('r', CloseMenuItem("Return to Main (r)")),
									])
main_menu = Menu(None, [
									('a', stats_menu),
									('s', skills_menu),
									('c', MenuItem("Combat [OFF] (c)", unimplemented)),
									('r', races_menu),
									('p', classes_menu),
									('d', MenuItem("Advancement (d)", unimplemented)),
									('e', MenuItem("Export to XML (e)", exportXml)),
									('g', MenuItem("Generate SQL Tables (g)", unimplemented)),
									('q', MenuItem("Quit (q)", sys.exit)),
									])

current_menu = main_menu
showMain()

