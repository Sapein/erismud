IAC  = '\377'
DONT = '\376'
DO   = '\375'
WONT = '\374'
WILL = '\373'

ECHO = '\001'
		
class TelnetTalk:

	def __init__(self):
		self.reply = ""

	def listen(self, cmd):
		
		while IAC in cmd:
			iac = cmd.find(IAC)
			
			if cmd[iac+1] == DO and cmd[iac+2] == ECHO:				# Got a DO ECHO, reply WILL ECHO
				self.reply += "%s%s%s" % (IAC, WILL, ECHO)
				cmd = cmd[:iac] + cmd[iac+3:]
				
			elif cmd[iac+1] == DONT and cmd[iac+2] == ECHO:			# Got a DONT ECHO, reply WONT ECHO
				self.reply += "%s%s%s" % (IAC, WONT, ECHO)
				cmd = cmd[:iac] + cmd[iac+3:]
			
			elif cmd[iac+1] == DO:									# Got DO (other than ECHO), reply WONT
				self.reply += "%s%s%s" % (IAC, WONT, cmd[iac+2])
				cmd = cmd[:iac] + cmd[iac+3:]
				
			elif cmd[iac+1] == DONT:								# Got DONT, reply WONT
				self.reply += "%s%s%s" % (IAC, WONT, cmd[iac+2])
				cmd = cmd[:iac] + cmd[iac+3:]				

			elif cmd[iac+1] == WILL:	 							# Got WILL, reply DONT
				self.reply += "%s%s%s" % (IAC, DONT, cmd[iac+2])
				cmd = cmd[:iac] + cmd[iac+3:]
			
			elif cmd[iac+1] == WONT: 								# Got WONT, shut up
				cmd = cmd[:iac] + cmd[iac+3:]

			elif ord(cmd[iac+1]) in range(0,50):					# Clean the various possible options
				cmd = cmd[:iac] + cmd[iac+2:]
			elif ord(cmd[iac+2]) in range(0,50):
				cmd = cmd[:iac] + cmd[iac+3:]
		
		return (cmd, self.reply)

