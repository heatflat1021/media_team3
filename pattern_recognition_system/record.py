import time

from cortex import Cortex

import EmotivInfo

class Record():
	def __init__(self, user):
		self.c = Cortex(user, debug_mode=False)
		self.c.do_prepare_steps()

	def create_record_then_export(self,
								record_name,
								record_description,
								record_length_s,
								record_export_folder,
								record_export_data_types,
								record_export_format,
								record_export_version):
		
		self.c.create_record(record_name,
							record_description)

		self.wait(record_length_s)

		self.c.stop_record()

		self.c.disconnect_headset()

		self.c.export_record(record_export_folder,
							record_export_data_types,
							record_export_format,
							record_export_version,
							[self.c.record_id])


	def wait(self, record_length_s):
		print('start recording -------------------------')
		length = 0
		while length < record_length_s:
			print('recording at {0} s'.format(length))
			time.sleep(1)
			length+=1
		print('end recording -------------------------')

# -----------------------------------------------------------
# 
# SETTING
# 	- replace your license, client_id, client_secret to user dic
# 	- specify infor for record and export
# 	- connect your headset with dongle or bluetooth, you should saw headset on EmotivApp
#
# RESULT
# 	- export result should be csv or edf file at location you specified
# 	- in that file will has data you specified like : eeg, motion, performance metric and band power
# 
# -----------------------------------------------------------
if __name__ == "__main__":
	user = EmotivInfo.user

	r = Record(user)

	# record parameters
	record_name = 'record'
	record_description = ''
	record_length_s = 15


	# export parameters
	record_export_folder = 'output'
	record_export_data_types = ['EEG', 'MOTION']
	record_export_format = 'CSV'
	record_export_version = 'V2'


	# start record --> stop record --> disconnect headset --> export record
	r.create_record_then_export(record_name,
								record_description,
								record_length_s,
								record_export_folder,
								record_export_data_types,
								record_export_format,
								record_export_version )
# -----------------------------------------------------------
