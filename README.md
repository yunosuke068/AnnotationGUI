# AnnotationGUI

## 環境構築手順
pythonのバージョン確認。バージョン3.10.xでなければ、pythonをインストール。
Windowsでのインストール方法。（
https://www.python.jp/install/windows/install.html ）

```Console
python -V
```

アノテーションアプリのインストール
```
git clone https://github.com/yunosuke068/AnnotationGUI.git
cd AnnotationGUI
```

仮想環境での作業が良ければ、以下のコードをコンソールで実行。

```
python -m venv myenv
myenv\Scripts\activate.bat
```

必要なライブラリのインストール。

```
pip install -r requirements.txt
```

GoogleDrive（ https://drive.google.com/file/d/1Nd0MIjzmMQsCZ8aJ4Diw2a3g_nJDhl0_/view?usp=sharing ）からzipファイルをインストール。解凍してdbディレクトリに中身をコピー。


アノテーションアプリの起動。
```
python main.py
```

## キーボード

|  キー  |  TH  |
| ---- | ---- |
|  A  |  前フレームに移動  |
|  D  |  次フレームに移動  |
|  Q  |  ラベルモード変更1。all:両手同時にラベル付け。right:右手のみラベル付け。left:左手のみラベル付け。  |
|  -  |  ラベルモード変更2。単発：フレームごとにラベル付け。連続：A,Dの連打でラベル付け。  |
|  0~6  |  ラベルボタン  |


## ER図
https://app.diagrams.net/?src=about#Hyunosuke068%2FAnnotationGUI%2Fdevelop%2FER.drawio
