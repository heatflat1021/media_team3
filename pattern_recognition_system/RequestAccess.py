from cortex import Cortex

import EmotivInfo

class RequestAccess():
	def __init__(self, user):
		self.c = Cortex(user, debug_mode=True)
		self.c.request_access()

user = EmotivInfo.user

s = RequestAccess(user)
