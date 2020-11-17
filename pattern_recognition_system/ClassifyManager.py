import EmotivInfo
import sub_data

import csv
import os
import shutil

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

    break

shutil.copy('./{}/model.h5'.format(username), './../')

user = EmotivInfo.user
subscribe = sub_data.Subcribe(user)

# y-z平面上の磁場の最小値と最大値を計測する
print('まずはじめに周辺磁場を計測します。')
print('計測を開始したら、回転椅子に座り10秒間程で2周ほど回転してください。')
print('準備ができたらEnterキーを押してください。')
s = input()

minY, maxY, minZ, maxZ = subscribe.get_magnetic_field_range()

# 基準方向を向いたときの磁場ベクトルを計測する
print('次に基準となる向きを計測します。')
print('計測を開始したら、10秒間程ディスプレイの正面に座ってディスプレイの中央を向いてください。')
print('準備ができたらEnterキーを押してください。')
s = input()

refY, refZ = subscribe.get_reference_direction_vector(minY, maxY, minZ, maxZ)

# コマンド生成
print('コマンド生成を実行します。')
print('準備ができたらEnterキーを押してください。')
s = input()

subscribe.realtime_process(minY, maxY, minZ, maxZ, refY, refZ)
