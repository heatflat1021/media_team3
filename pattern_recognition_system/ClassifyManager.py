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
        print('ユーザー: {}は存在しません。再度ユーザー名を入力してください。'.format(username))
        continue
    
    #todo: ユーザーのCSVを読んで基準となる方向を計算する

    os.mkdir(os.path.join(current_dir, username))
    break

user = EmotivInfo.user
s = sub_data.Subcribe(user)
s.realtime_process()
