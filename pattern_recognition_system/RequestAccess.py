import EmotivInfo

from cortex import Cortex

class RequestAccess():
	def __init__(self, user):
		self.c = Cortex(user, debug_mode=True)
		self.c.request_access()

user = EmotivInfo.user

s = RequestAccess(user)
