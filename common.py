
### Common methods shared by all files

class C:
	def __init__(self, session):
		self.session = session

	def CYAN(self, str):
		return "%s%s%s" % (self.session.CYAN,str,self.session.RESET)
	def B_WHITE(self, str):
		return "%s%s%s%s" % (self.session.BOLD,self.session.WHITE,str,self.session.RESET)
	def B_RED(self, str):
		return "%s%s%s%s" % (self.session.BOLD,self.session.RED,str,self.session.RESET)
	def B_GREEN(self, str):
		return "%s%s%s%s" % (self.session.BOLD,self.session.GREEN,str,self.session.RESET)
		
	def flatten(self, x):
	    result = []
	    for el in x:
	        if hasattr(el, "__iter__") and not isinstance(el, basestring):
	            result.extend(self.flatten(el))
	        else:
	            result.append(el)
	    return result