import time
import re
import os
import csv
import threading

import cv2
import numpy as np
from sklearn.model_selection import train_test_split
import tensorflow as tf

import record
import EmotivInfo

###################################################

DATA_LENGTH = 640
STEP_SIZE = 640
IGNORE_LENGTH = 80
CHANNEL_NUMBER = 14

LAYER_DEPTHS = [4, 5]
FILTER_MAGNIFICATIONS = [1, 2, 3]

path = "./{}".format(username)

def normalize(x):
    min = x.min()
    max = x.max()
    result = (x-min)/(max-min)
    return result

all_files = os.listdir(path)

X = np.zeros((0, DATA_LENGTH, CHANNEL_NUMBER), dtype='float32')
Y = []
for commandIdx, command in enumerate(commands):
    specific_command_data_list = np.zeros((0, DATA_LENGTH, CHANNEL_NUMBER), float)
    specific_files = [s for s in all_files if command.name in s and '.csv' in s]
    for specific_file in specific_files:
        l = np.loadtxt('{}/{}'.format(path, specific_file), delimiter=',', dtype='float32', skiprows=2, usecols=range(3, 3+CHANNEL_NUMBER))
        
        step = 0
        while IGNORE_LENGTH + STEP_SIZE * step + DATA_LENGTH < l.shape[0]:
            startIdx = IGNORE_LENGTH + STEP_SIZE * step
            endIdx = startIdx + DATA_LENGTH
            X = np.block([[[X]], [[normalize(l[startIdx:endIdx]).reshape(1, DATA_LENGTH, CHANNEL_NUMBER)]]])
            step += 1
        Y.append([commandIdx]*step)
Y = np.asarray(Y)

#reshape
X = X.reshape(X.shape[0], X.shape[1],X.shape[2], 1)
# 教師データをOne-hot表現に直す
Y = tf.keras.utils.to_categorical(Y, num_classes=len(commands))

# 学習：検証 ＝ 7：3 で分割
X_train, X_valid, Y_train, Y_valid = train_test_split(X, Y, test_size=0.3)

max_score = -1 # 最小値で初期化
optimal_model = None

for layer_depth in LAYER_DEPTHS:
    for filter_magnification in FILTER_MAGNIFICATIONS:
        #5層CNN for EEG
        model = tf.keras.models.Sequential()
        #1 入力(640,14,1)
        model.add(tf.keras.layers.Conv2D(25*filter_magnification, kernel_size=(11,1),activation='relu', input_shape=(640,14,1)))#時間軸１次畳み込み
        #2
        model.add(tf.keras.layers.Conv2D(25*filter_magnification , kernel_size=(1,14),activation='relu'))#空間軸1次畳み込み14->1
        model.add(tf.keras.layers.MaxPooling2D(pool_size=(3,1)))#3x1pooling
        #3
        model.add(tf.keras.layers.Conv2D(50*filter_magnification, kernel_size=(11,1),activation='relu'))#時間軸1次畳み込み
        model.add(tf.keras.layers.MaxPooling2D(pool_size=(3,1)))#3x1pooling
        #4
        model.add(tf.keras.layers.Conv2D(100*filter_magnification, kernel_size=(11,1),activation='relu'))#時間軸1次畳み込み
        model.add(tf.keras.layers.MaxPooling2D(pool_size=(3,1)))#3x1pooling
        #5
        if 5 <= layer_depth:
            model.add(tf.keras.layers.Conv2D(200*filter_magnification, kernel_size=(11,1),activation='relu'))#時間軸1次畳み込み
            model.add(tf.keras.layers.AveragePooling2D(pool_size=(2,1),strides=(2,1)))#2x1pooling  2strides
        #
        model.add(tf.keras.layers.Flatten())#
        model.add(tf.keras.layers.Dense(len(commands), activation='softmax'))#出力 サイズ4ベクトル

        # モデル構築
        model.compile(loss='categorical_crossentropy',
                    optimizer='adam',
                    metrics=['accuracy'])

        # モデル学習
        earlystopper = tf.keras.callbacks.EarlyStopping(min_delta=0.01,patience=5)
        history = model.fit(X_train,
                            Y_train,
                            batch_size= 16,
                            epochs=60,
                            verbose=0,
                            validation_data=(X_valid,Y_valid),
                            callbacks=[earlystopper])

        ####評価
        loss, acc = model.evaluate(X_test, Y_test)

        if acc - 0.5 * loss > max_score:
            max_score = acc - 0.5 * loss
            optimal_model = model

optimal_model.save('./{}/model.h5'.format(username))

#####################################################

print("学習器の生成が終了しました。")
