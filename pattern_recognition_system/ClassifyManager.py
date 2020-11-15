import EmotivInfo
import sub_data

import csv
import os
import math

while True:
    print('以前に作成したユーザー名を入力してください')
    print('ユーザー名:', end='')
    username = input()

    current_dir = os.getcwd()
    files = os.listdir(current_dir)
    dir_list = [f for f in files if os.path.isdir(os.path.join(current_dir, f))]
    if not username in dir_list:
        print('{}は存在しません。再度ユーザー名を入力してください。'.format(username))
        continue

print('センシングを開始して最初の10秒間で基準となる向きを計測します。')
print('はじめの10秒間は必ず正面を向いていてください。')
print('準備ができたらEnterキーを押してください。')
s = input()

user = EmotivInfo.user
s = sub_data.Subcribe(user)
s.realtime_process()
