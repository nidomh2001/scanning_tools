# scanning_tools
pythonを使用してステージコントローラーshot302gsおよびshot304gs を操作するモジュールとGUIです。
GUIではstreamlitを使用しています。

# 環境構築
## ドライバーのインストール
NIのドライバーツールをインストール

## 仮想環境の構築
コマンドプロンプトを管理者権限で起動


保存するフォルダを作成・移動（C:\pysrc\scanning_toolsに保存する方法を例示）
```
mkdir C:\pysrc\scanning_tools
cd C:\pysrc\scanning_tools
```

Github上のソースをクローン
```
git clone https://github.com/nidomh2001/scanning_tools.git
```

バージョンを指定して仮想環境を作成
```
py -3.12 -m venv .venv
```
仮想環境を有効化
```
.\.venv\Scripts\activate
```

必要なパッケージをインストール
```
pip install -r requirements.txt
```

## ハードウェアのメモリ設定
ステージコントローラー本体にコントロールパッドを接続し、「Ctrl」+「SET」ボタンを同時押しでメモリスイッチ設定画面にする。コントロールパッドの操作方法は次の通り。


**メモリスイッチ設定画面操作方法**
```
十字ボタン　：上下で設定項目切り替え
十字ボタン　：左右でカーソル移動
SETボタン 　 ：設定内容を変更（数値データの場合増加）
SPDボタン     ：設定内容を変更（数値データの場合減少）
MODEボタン ：設定終了時（完了確認画面へ移行）
Ctrl ＋ ORG ＋ ZERO ボタン：メモリスイッチの内容が初期値（出荷時の状態）に戻る
```


次のように設定を行う。

|番号|メモリスイッチ内容|設定内容|
|:-:|:-:|:-:|
|14|制御軸数選択|2|
|15|通信インターフェースの設定|GP-IB|
|18|GP-IB アドレス設定|8|
|19~22|各軸の表示単位選択|MICRO|
|27~30|各軸の基本（フル）ステップでの 1 パルス当たりの移動量入力|ネジリード[mm] × 20。例1) ネジリード1mmのSGSP20-35の場合：BASE_LATE=1×20=20。例2) ネジリード2mmのSGSP26-150の場合：BASE_LATE=2×20=20|
|64~67|各軸の制御方式|OPEN|


# 実行方法
次のコマンドを実行

shot302使用の場合
```
streamlit run ./module/gui_stagecontroller_shot302gs.py
```

shot304gs使用の場合
```
streamlit run ./module/gui_stagecontroller_shot304gs.py
```

試作main.py
```
streamlit run main.py
```
