import time
import re
import os

from cortex import Cortex
import EmotivInfo

def ready_confirm():
    print('準備ができたらEnterキーを押してください。')
    s = input()

def count_down(second):
    for i in range(second):
        print(second - i)
        time.sleep(1)

def isascii(s):
    return re.compile(r'^[!-~]+$').match(s) is not None

class Command:
    def __init__(self, name, instruction, mesurement_times):
        self.name = name
        self.instruction = instruction
        self.mesurement_times = mesurement_times

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

commands = [
    Command('neutral', '平常心をイメージしてください。', 10),
    Command('straight', '直進をイメージしてください。', 10),
    Command('sword', '剣で攻撃するイメージをしてください。', 10),
    Command('magic1', '火炎を放出するイメージをしてください。', 10),
    Command('magic2', '岩を動かすイメージをしてください。', 10)
]

user = EmotivInfo.user

r = Record(user)

MESUREMENT_SECOND = 20

###############################################

username = ''
while True:
    print('ユーザー名を入力してください')
    print('ユーザー名には英数字及び記号が使えますが、日本語文字は使えません。')
    print('ユーザー名:', end='')
    username = input()

    if not isascii(username):
        print('! ユーザー名に日本語文字は使えません。')
        continue

    current_dir = os.getcwd()
    files = os.listdir(current_dir)
    dir_list = [f for f in files if os.path.isdir(os.path.join(current_dir, f))]
    if username in dir_list:
        print('ユーザー{}は既に存在します。別のユーザー名で新しくユーザーを登録する場合はMを、そのユーザーで続きから計測をする場合はそれ以外の入力をしてください。'.format(username))
    else:
        print("ユーザー名は{}で間違いないですか。修正する場合はMを、間違い無い場合はそれ以外の入力をしてください。".format(username))
    print('入力:', end='')
    s = input()
    if(s in 'mM'):
        continue

    if not username in dir_list:
        os.mkdir(os.path.join(current_dir, username))
    break

print('計測秒数や計測回数を指定しますか？指定する場合はMを、指定しない場合はそれ以外を入力してください。')
print('入力:', end='')
s = input()
if(s in 'mM'):
    recordTime = recordNum = 0
    while True:
        print("計測秒数:", end='')
        n = input()
        try:
            recordTime = int(n)
        except:
            continue
        break

    while True:
        print("計測回数:", end='')
        n = input()
        try:
            recordNum = int(n)
        except:
            continue
        break

    MESUREMENT_SECOND = recordTime
    for command in commands:
        command.mesurement_times = recordNum

print("計測を開始します。")
ready_confirm()

record_id_list = []
for idx, command in enumerate(commands):
    print("{}番目のコマンド[{}]の計測を開始します。".format((idx + 1), command.name))
    print("計測中は{}".format(command.instruction))
    print("{}秒間の計測を{}セット行います。".format(MESUREMENT_SECOND, command.mesurement_times))

    for i in range(command.mesurement_times):
        ready_confirm()
        count_down(3)
        print("計測中")

        # record parameters
        record_name = '{}_{}'.format(command.name, i)
        record_description = ''

        r.c.create_record(record_name, record_description)
        r.wait(MESUREMENT_SECOND)
        r.c.stop_record()
        record_id_list.append(r.c.record_id)

        print("完了[{}/{}]:{}".format((i + 1), command.mesurement_times, command.name))

# export parameters
record_export_folder = os.path.join(current_dir, username)
record_export_data_types = ['EEG', 'MOTION']
record_export_format = 'CSV'
record_export_version = 'V2'

# export EEG data to CSV
r.c.disconnect_headset()
r.c.export_record(record_export_folder,
	record_export_data_types,
	record_export_format,
	record_export_version,
    record_id_list)

# 不要なJSONファイルの削除
data_files = os.listdir(record_export_folder)
json_files = [s for s in data_files if '.json' in s]
for json_file in json_files:
    os.remove('./{}/{}'.format(username, json_file))

print("計測お疲れ様でした。")
