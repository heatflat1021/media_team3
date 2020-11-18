import time
import re
import os
import csv

import numpy as np
from sklearn.model_selection import train_test_split
import tensorflow as tf

import record
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

commands = [
    Command('neutral', '平常心をイメージしてください。', 3),
    Command('straight', '直進をイメージしてください。', 3),
    Command('sword', '剣で攻撃するイメージをしてください。', 3),
    Command('magic1', '火炎を放出するイメージをしてください。', 3),
    Command('magic2', '岩を動かすイメージをしてください。', 3)
]

user = EmotivInfo.user

r = record.Record(user)

MESUREMENT_SECOND = 6

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

    print("ユーザー名は{}で間違いないですか？".format(username))
    print("修正する場合はMを、間違い無い場合はそれ以外の入力をしてください。")
    s = input()
    if(s in 'mM'):
        continue

    current_dir = os.getcwd()
    files = os.listdir(current_dir)
    dir_list = [f for f in files if os.path.isdir(os.path.join(current_dir, f))]
    if username in dir_list:
        print('同一名のユーザーが存在します。ユーザー名を変更してださい。')
        continue

    os.mkdir(os.path.join(current_dir, username))
    break

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

        print("完了[{}/{}]".format((i + 1), command.mesurement_times))

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
    os.remove(json_file)

print("計測お疲れ様でした。")
print("ただいま脳波データから分類器を生成しています。")
print("終了を知らせる表示が出るまで、今しばらくお待ちください。")

###################################################

DATA_LENGTH = 640
STEP_SIZE = 100
IGNORE_LENGTH = 100
CHANNEL_NUMBER = 14

path = "./{}".format(username)

def normalize(x):
    min = x.min()
    max = x.max()
    result = (x-min)/(max-min)
    return result

all_files = os.listdir(path)

X = np.zeros((0, DATA_LENGTH, CHANNEL_NUMBER), float)
Y = np.zeros(0)
for command in commands:
    specific_command_data_list = np.zeros((0, DATA_LENGTH, CHANNEL_NUMBER), float)
    specific_files = [s for s in all_files if command.name in s and '.csv' in s]
    for commandIdx, specific_file in enumerate(specific_files):
        with open(path + "/" + specific_file) as f:
            reader = csv.reader(f)
            l = [row for row in reader]
        l = [[float(v) for v in row[3:3+CHANNEL_NUMBER]] for row in l[2:]] # EEGに該当する部分のみスライス
        l = np.array(l)
        l = l.astype(np.float)
        
        step = 0
        while IGNORE_LENGTH + STEP_SIZE * step + DATA_LENGTH < l.shape[0]:
            startIdx = IGNORE_LENGTH + STEP_SIZE * step
            endIdx = IGNORE_LENGTH + STEP_SIZE * step + DATA_LENGTH
            X = np.block([[[X]], [[normalize(l[startIdx:endIdx]).reshape(1, DATA_LENGTH, CHANNEL_NUMBER)]]])
            step += 1
        Y = np.append(Y, np.full(step, commandIdx))

#reshape
X = X.reshape(X.shape[0], X.shape[1],X.shape[2], 1)
# 教師データをOne-hot表現に直す
Y = tf.keras.utils.to_categorical(Y, num_classes=len(commands))

# 学習：検証 ＝ 7：3 で分割
X_train, X_valid, Y_train, Y_valid = train_test_split(X, Y, test_size=0.3)

#5層CNN for EEG
model = tf.keras.models.Sequential()
#1 入力(640,14,1)
model.add(tf.keras.layers.Conv2D(25, kernel_size=(11,1),activation='relu', input_shape=(640,14,1)))#時間軸１次畳み込み
#2
model.add(tf.keras.layers.Conv2D(25, kernel_size=(1,14),activation='relu'))#空間軸1次畳み込み14->1
model.add(tf.keras.layers.MaxPooling2D(pool_size=(3,1)))#3x1pooling
#3
model.add(tf.keras.layers.Conv2D(50, kernel_size=(11,1),activation='relu'))#時間軸1次畳み込み
model.add(tf.keras.layers.MaxPooling2D(pool_size=(3,1)))#3x1pooling
#4
model.add(tf.keras.layers.Conv2D(100, kernel_size=(11,1),activation='relu'))#時間軸1次畳み込み
model.add(tf.keras.layers.MaxPooling2D(pool_size=(3,1)))#3x1pooling
#5
model.add(tf.keras.layers.Conv2D(200, kernel_size=(11,1),activation='relu'))#時間軸1次畳み込み
model.add(tf.keras.layers.MaxPooling2D(pool_size=(2,1),strides=(2,1)))#2x1pooling  2strides
#
model.add(tf.keras.layers.Flatten())#
model.add(tf.keras.layers.Dense(len(commands), activation='softmax'))#出力 サイズ4ベクトル

# モデル構築
model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

# モデル学習
history = model.fit(X_train,
                    Y_train,
                    batch_size= 16,
                    epochs=30,
                    verbose=1,
                    validation_data=(X_valid,Y_valid))
model.save('./{}/model.h5'.format(username))

#####################################################

print("学習器の生成が終了しました。")
