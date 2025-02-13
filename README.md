# scanning_tools
pythonを使用してステージコントローラーshot304gs を操作するモジュールとGUIです。
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

# 実行方法
次のコマンドを実行

shot302使用の場合
```
streamlit run ./module/gui_stagecontroller_shot302.py
```

shot304gs使用の場合
```
streamlit run ./module/gui_stagecontroller_shot304gs.py
```

試作main.py
```
streamlit run main.py
```
