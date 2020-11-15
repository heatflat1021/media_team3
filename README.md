# media_team3

## 概要
このリポジトリは、2020年度メディア系演習IIのグループ3の作業リポジトリである。本演習でグループ3は「脳波でアバターを操作するRPGゲーム」を作った。

## 使い方
### パターン認識システム関連
1. pattern_recognition_systemディレクトリに移動する。
1. `pip install -r requirements.txt`で必要なパッケージをインストールする。
1. Emotiv PROをインストールする。([EmotivのHP](https://www.emotiv.com/))
1. EmotivInfo.samの内容をコピーして、同じディレクトリにEmotivInfo.pyを作成する。
1. EmotivInfo.pyの内容を適切に書き換える。
1. Emotiv EPOC+を接続する。
1. `python RequestAccess.py`でRequestAccess.pyを実行する。
1. Emotiv PROを実行し、認証を行う。
1. `python LearnManager.py`で脳波の計測及び、パターン認識モデルの生成を行う。
1. `python ClassifyManager.py`でパターン認識のプログラムを実行する。

### RPGゲーム関連
1. Unityをインストールする。本プロジェクトは、Unityバージョン2019.4.12f1で動作することを確認しています。([Unityのダウンロードページ](https://unity3d.com/jp/get-unity/download))
1. RPG_gameディレクトリをルートディレクトリとして、RPG_gameをUnityで開く。
1. 次の手順でビルドを行う。ファイル>ビルド設定>ビルド>(ビルド結果の出力先にmedia_team3を選択する。)
1. ビルドによって生成された実行ファイルを実行する。
