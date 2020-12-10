import os

import numpy as np
from sklearn.model_selection import train_test_split
import tensorflow as tf

TRAIN_VALID_PROPORTION = 0.8
TRAIN_PROPORTION = 0.8

DATA_LENGTH = 640
STEP_SIZE = 640
IGNORE_LENGTH = 80
CHANNEL_NUMBER = 14

LAYER_DEPTHS = [4, 5]
FILTER_MAGNIFICATIONS = [1, 2, 3]
LOSS_COEFFICIENT = 0.5

commands = ["neutral", "straight", "sword", "magic1", "magic2"]

###################################################

while True:
    print("以前に作成したユーザー名を入力してください")
    print("ユーザー名:", end="")
    username = input()

    current_dir = os.getcwd()
    files = os.listdir(current_dir)
    dir_list = [f for f in files if os.path.isdir(os.path.join(current_dir, f))]
    if not username in dir_list:
        print("{}は存在しません。再度ユーザー名を入力してください。".format(username))
        continue
    break

print("パターン認識モデルを生成しています。")

path = "./{}".format(username)

def normalize(x):
    min = x.min()
    max = x.max()
    result = (x-min)/(max-min)
    return result

all_files = os.listdir(path)
train_valid_files, test_files = all_files[:int(len(all_files) * TRAIN_VALID_PROPORTION)], all_files[int(len(all_files) * TRAIN_VALID_PROPORTION):]
train_files, valid_files = train_valid_files[:int(len(train_valid_files) * TRAIN_PROPORTION)], train_valid_files[int(len(train_valid_files) * TRAIN_PROPORTION):]

# 訓練データの前処理
X_train = np.zeros((0, DATA_LENGTH, CHANNEL_NUMBER), dtype="float32")
Y_train = []
for commandIdx, command in enumerate(commands):
    specific_command_data_list = np.zeros((0, DATA_LENGTH, CHANNEL_NUMBER), float)
    specific_files = [s for s in train_files if command.name in s and ".csv" in s]
    for specific_file in specific_files:
        l = np.loadtxt('{}/{}'.format(path, specific_file), delimiter=",", dtype="float32", skiprows=2, usecols=range(3, 3+CHANNEL_NUMBER))
        
        step = 0
        while IGNORE_LENGTH + STEP_SIZE * step + DATA_LENGTH < l.shape[0]:
            startIdx = IGNORE_LENGTH + STEP_SIZE * step
            endIdx = startIdx + DATA_LENGTH
            X_train = np.block([[[X_train]], [[normalize(l[startIdx:endIdx]).reshape(1, DATA_LENGTH, CHANNEL_NUMBER)]]])
            step += 1
        Y_train.append([commandIdx]*step)

X_train = X_train.reshape(X_train.shape[0], X_train.shape[1],X_train.shape[2], 1)
Y_train = np.asarray(Y_train)
Y_train = tf.keras.utils.to_categorical(Y_train, num_classes=len(commands))

# 検証データの前処理
X_valid = np.zeros((0, DATA_LENGTH, CHANNEL_NUMBER), dtype="float32")
Y_valid = []
for commandIdx, command in enumerate(commands):
    specific_command_data_list = np.zeros((0, DATA_LENGTH, CHANNEL_NUMBER), float)
    specific_files = [s for s in valid_files if command.name in s and ".csv" in s]
    for specific_file in specific_files:
        l = np.loadtxt('{}/{}'.format(path, specific_file), delimiter=",", dtype="float32", skiprows=2, usecols=range(3, 3+CHANNEL_NUMBER))
        
        step = 0
        while IGNORE_LENGTH + STEP_SIZE * step + DATA_LENGTH < l.shape[0]:
            startIdx = IGNORE_LENGTH + STEP_SIZE * step
            endIdx = startIdx + DATA_LENGTH
            X_valid = np.block([[[X_valid]], [[normalize(l[startIdx:endIdx]).reshape(1, DATA_LENGTH, CHANNEL_NUMBER)]]])
            step += 1
        Y_valid.append([commandIdx]*step)

X_valid = X_valid.reshape(X_valid.shape[0], X_valid.shape[1],X_valid.shape[2], 1)
Y_valid = np.asarray(Y_valid)
Y_valid = tf.keras.utils.to_categorical(Y_valid, num_classes=len(commands))

# テストデータの前処理
X_test = np.zeros((0, DATA_LENGTH, CHANNEL_NUMBER), dtype="float32")
Y_test = []
for commandIdx, command in enumerate(commands):
    specific_command_data_list = np.zeros((0, DATA_LENGTH, CHANNEL_NUMBER), float)
    specific_files = [s for s in test_files if command.name in s and ".csv" in s]
    for specific_file in specific_files:
        l = np.loadtxt('{}/{}'.format(path, specific_file), delimiter=",", dtype="float32", skiprows=2, usecols=range(3, 3+CHANNEL_NUMBER))
        
        step = 0
        while IGNORE_LENGTH + STEP_SIZE * step + DATA_LENGTH < l.shape[0]:
            startIdx = IGNORE_LENGTH + STEP_SIZE * step
            endIdx = startIdx + DATA_LENGTH
            X_test = np.block([[[X_test]], [[normalize(l[startIdx:endIdx]).reshape(1, DATA_LENGTH, CHANNEL_NUMBER)]]])
            step += 1
        Y_test.append([commandIdx]*step)

X_test = X_test.reshape(X_test.shape[0], X_test.shape[1],X_test.shape[2], 1)
Y_test = np.asarray(Y_test)
Y_test = tf.keras.utils.to_categorical(Y_test, num_classes=len(commands))

max_score = -1 # 最小値で初期化
optimal_model = None
for layer_depth in LAYER_DEPTHS:
    for filter_magnification in FILTER_MAGNIFICATIONS:
        #5層CNN for EEG
        model = tf.keras.models.Sequential()
        #1 入力(640,14,1)
        model.add(tf.keras.layers.Conv2D(25*filter_magnification, kernel_size=(11,1),activation="relu", input_shape=(640,14,1)))#時間軸１次畳み込み
        #2
        model.add(tf.keras.layers.Conv2D(25*filter_magnification , kernel_size=(1,14),activation="relu"))#空間軸1次畳み込み14->1
        model.add(tf.keras.layers.MaxPooling2D(pool_size=(3,1)))#3x1pooling
        #3
        model.add(tf.keras.layers.Conv2D(50*filter_magnification, kernel_size=(11,1),activation="relu"))#時間軸1次畳み込み
        model.add(tf.keras.layers.MaxPooling2D(pool_size=(3,1)))#3x1pooling
        #4
        model.add(tf.keras.layers.Conv2D(100*filter_magnification, kernel_size=(11,1),activation="relu"))#時間軸1次畳み込み
        model.add(tf.keras.layers.MaxPooling2D(pool_size=(3,1)))#3x1pooling
        #5
        if 5 <= layer_depth:
            model.add(tf.keras.layers.Conv2D(200*filter_magnification, kernel_size=(11,1),activation="relu"))#時間軸1次畳み込み
            model.add(tf.keras.layers.AveragePooling2D(pool_size=(2,1),strides=(2,1)))#2x1pooling  2strides
        #
        model.add(tf.keras.layers.Flatten())#
        model.add(tf.keras.layers.Dense(len(commands), activation="softmax"))#出力 サイズ4ベクトル

        # モデル構築
        model.compile(loss="categorical_crossentropy",
                    optimizer="adam",
                    metrics=["accuracy"])

        # モデル学習
        earlystopper = tf.keras.callbacks.EarlyStopping(min_delta=0.01,patience=5)
        history = model.fit(X_train,
                            Y_train,
                            batch_size= 16,
                            epochs=60,
                            verbose=0,
                            validation_data=(X_valid,Y_valid),
                            callbacks=[earlystopper])

        # 評価
        loss, acc = model.evaluate(X_test, Y_test)

        if acc - LOSS_COEFFICIENT * loss > max_score:
            max_score = acc - LOSS_COEFFICIENT * loss
            optimal_model = model

optimal_model.save("./{}/model.h5".format(username))

#####################################################

print("パターン認識モデルの生成が終了しました。")
