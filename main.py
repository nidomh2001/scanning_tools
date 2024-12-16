<<<<<<< HEAD
import streamlit as st
import json
import os
import time

from module.stagecontroller_shot304gs import StageController
import csv
import matplotlib.pyplot as plt
import seaborn as sns

# JSONファイルのパス
json_file_path = "setinfo.json"

# JSONファイルからデータを読み込む関数
def load_data():
    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as file:
            return json.load(file)
    return {}

# JSONファイルにデータを書き込む関数
def save_data(data):
    with open(json_file_path, "w") as file:
        json.dump(data, file)

# データの読み込み
data = load_data()

# タイトル
st.title("ステージコントローラ GUI")

# カラムを作成
col1, col2 = st.columns(2)

# 1軸方向の初期位置およびステップ幅
with col1:
    st.header("1軸方向")
    axis1_initial_position = st.text_input("初期位置 (1軸) [um]", value=data.get("axis1_initial_position", ""))
    axis1_step_size = st.text_input("ステップ幅 (1軸) [um]", value=data.get("axis1_step_size", ""))
    axis1_steps = st.text_input("ステップ数 (1軸)", value=data.get("axis1_steps", ""))
    axis1_direction = st.selectbox("移動方向 (1軸)", ["+", "-"], index=0 if data.get("axis1_direction", "+") == "+" else 1)

# 2軸方向の初期位置およびステップ幅
with col2:
    st.header("2軸方向")
    axis2_initial_position = st.text_input("初期位置 (2軸) [um]", value=data.get("axis2_initial_position", ""))
    axis2_step_size = st.text_input("ステップ幅 (2軸) [um]", value=data.get("axis2_step_size", ""))
    axis2_steps = st.text_input("ステップ数 (2軸)", value=data.get("axis2_steps", ""))
    axis2_direction = st.selectbox("移動方向 (2軸)", ["+", "-"], index=0 if data.get("axis2_direction", "+") == "+" else 1)

# 移動後待機時間
st.header("移動後待機時間")
wait_time = st.text_input("待機時間 [ms]", value=data.get("wait_time", ""))

# 測定結果保存フォルダ
st.header("測定結果保存フォルダ")
save_folder = st.text_input("保存フォルダ", value=data.get("save_folder", ""))

# 測定結果保存ファイル名
st.header("測定結果保存ファイル名")
save_file_name = st.text_input("保存ファイル名", value=data.get("save_file_name", ""))

placeholder = st.empty()

# スキャンスタートボタン
if st.button("スキャンスタート"):
    st.write("スキャンを開始します...")
    
    try:
        axis1_initial_position = float(axis1_initial_position)
        axis1_step_size = float(axis1_step_size)
        axis1_steps = int(axis1_steps)
        axis2_initial_position = float(axis2_initial_position)
        axis2_step_size = float(axis2_step_size)
        axis2_steps = int(axis2_steps)
        wait_time = float(wait_time)
    except ValueError:
        st.error("数値に変換できない入力があります。入力を確認してください。")
        st.stop()

    # 入力されたデータを保存
    data = {
        "axis1_initial_position": axis1_initial_position,
        "axis1_step_size": axis1_step_size,
        "axis1_steps": axis1_steps,
        "axis1_direction": axis1_direction,
        "axis2_initial_position": axis2_initial_position,
        "axis2_step_size": axis2_step_size,
        "axis2_steps": axis2_steps,
        "axis2_direction": axis2_direction,
        "wait_time": wait_time,
        "save_folder": save_folder,
        "save_file_name": save_file_name
    }
    save_data(data)

    # ステージコントローラの初期化
    stage_controller = StageController()
    stage_controller.moveAbs(2, axis1_initial_position)
    stage_controller.moveAbs(4, axis2_initial_position)
    
    # 測定結果保存フォルダの作成
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    
    # 測定結果を保存するための2次元配列を初期化
    results = [[0.0 for _ in range(axis2_steps)] for _ in range(axis1_steps)]
    
    # ===============================
    # 測定ループ開始
    # ===============================    

    # 測定ループ開始
    for i in range(axis1_steps):
        for j in range(axis2_steps):
            # 1軸方向に移動
            move1 = axis1_initial_position + i * axis1_step_size if axis1_direction == "+" else axis1_initial_position - i * axis1_step_size
            stage_controller.moveAbs(2, move1)
            # 2軸方向に移動
            move2 = axis2_initial_position + j * axis2_step_size if axis2_direction == "+" else axis2_initial_position - j * axis2_step_size
            stage_controller.moveAbs(4, move2)
            # 移動後待機
            time.sleep(wait_time/1000)
            print(f"スキャン中... 1軸: {i+1}/{axis1_steps}, 2軸: {j+1}/{axis2_steps}")
            # *******************************
            # ここに測定処理を記述
            # *******************************
            # 測定結果をリストに追加（例としてダミーデータを追加）
            results[i][j] = i + j
            
            # ヒートマップを描画(この処理のままだと遅いです)
            fig, ax = plt.subplots()
            sns.heatmap(results, annot=True, cmap="viridis", ax=ax)
            ax.set_title("heatmap")
            ax.set_xlabel("2axis step")
            ax.set_ylabel("1axis step")

            # Streamlitに表示
            placeholder.pyplot(fig)

    # 測定結果をCSVファイルに保存
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    sweep_conditions = f"_{axis1_initial_position}_{axis1_step_size}_{axis1_steps}_{axis1_direction}_{axis2_initial_position}_{axis2_step_size}_{axis2_steps}_{axis2_direction}_{wait_time}ms"
    csv_file_path = os.path.join(save_folder, save_file_name + sweep_conditions + "_" + timestamp)
    with open(csv_file_path+".csv", "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        # 測定結果を書き込む
        csvwriter.writerows(results)
    
    stage_controller.moveBasePosition()
    st.success("スキャンが完了しました。")
    # ===============================


    
# 入力された値を表示
st.write("1軸初期位置:", axis1_initial_position)
st.write("1軸ステップ幅:", axis1_step_size)
st.write("1軸ステップ数:", axis1_steps)
st.write("1軸移動方向:", axis1_direction)
st.write("2軸初期位置:", axis2_initial_position)
st.write("2軸ステップ幅:", axis2_step_size)
st.write("2軸ステップ数:", axis2_steps)
st.write("2軸移動方向:", axis2_direction)
st.write("待機時間:", wait_time)
st.write("保存フォルダ:", save_folder)
=======
import streamlit as st
import json
import os
import time

from module.stagecontroller_shot304gs import StageController
import csv
import matplotlib.pyplot as plt
import seaborn as sns

# JSONファイルのパス
json_file_path = "setinfo.json"

# JSONファイルからデータを読み込む関数
def load_data():
    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as file:
            return json.load(file)
    return {}

# JSONファイルにデータを書き込む関数
def save_data(data):
    with open(json_file_path, "w") as file:
        json.dump(data, file)

# データの読み込み
data = load_data()

# タイトル
st.title("ステージコントローラ GUI")

# カラムを作成
col1, col2 = st.columns(2)

# 1軸方向の初期位置およびステップ幅
with col1:
    st.header("1軸方向")
    axis1_initial_position = st.text_input("初期位置 (1軸) [um]", value=data.get("axis1_initial_position", ""))
    axis1_step_size = st.text_input("ステップ幅 (1軸) [um]", value=data.get("axis1_step_size", ""))
    axis1_steps = st.text_input("ステップ数 (1軸)", value=data.get("axis1_steps", ""))
    axis1_direction = st.selectbox("移動方向 (1軸)", ["+", "-"], index=0 if data.get("axis1_direction", "+") == "+" else 1)

# 2軸方向の初期位置およびステップ幅
with col2:
    st.header("2軸方向")
    axis2_initial_position = st.text_input("初期位置 (2軸) [um]", value=data.get("axis2_initial_position", ""))
    axis2_step_size = st.text_input("ステップ幅 (2軸) [um]", value=data.get("axis2_step_size", ""))
    axis2_steps = st.text_input("ステップ数 (2軸)", value=data.get("axis2_steps", ""))
    axis2_direction = st.selectbox("移動方向 (2軸)", ["+", "-"], index=0 if data.get("axis2_direction", "+") == "+" else 1)

# 移動後待機時間
st.header("移動後待機時間")
wait_time = st.text_input("待機時間 [ms]", value=data.get("wait_time", ""))

# 測定結果保存フォルダ
st.header("測定結果保存フォルダ")
save_folder = st.text_input("保存フォルダ", value=data.get("save_folder", ""))

# 測定結果保存ファイル名
st.header("測定結果保存ファイル名")
save_file_name = st.text_input("保存ファイル名", value=data.get("save_file_name", ""))

placeholder = st.empty()

# スキャンスタートボタン
if st.button("スキャンスタート"):
    st.write("スキャンを開始します...")
    
    try:
        axis1_initial_position = float(axis1_initial_position)
        axis1_step_size = float(axis1_step_size)
        axis1_steps = int(axis1_steps)
        axis2_initial_position = float(axis2_initial_position)
        axis2_step_size = float(axis2_step_size)
        axis2_steps = int(axis2_steps)
        wait_time = float(wait_time)
    except ValueError:
        st.error("数値に変換できない入力があります。入力を確認してください。")
        st.stop()

    # 入力されたデータを保存
    data = {
        "axis1_initial_position": axis1_initial_position,
        "axis1_step_size": axis1_step_size,
        "axis1_steps": axis1_steps,
        "axis1_direction": axis1_direction,
        "axis2_initial_position": axis2_initial_position,
        "axis2_step_size": axis2_step_size,
        "axis2_steps": axis2_steps,
        "axis2_direction": axis2_direction,
        "wait_time": wait_time,
        "save_folder": save_folder,
        "save_file_name": save_file_name
    }
    save_data(data)

    # ステージコントローラの初期化
    stage_controller = StageController()
    stage_controller.moveAbs(2, axis1_initial_position)
    stage_controller.moveAbs(4, axis2_initial_position)
    
    # 測定結果保存フォルダの作成
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    
    # 測定結果を保存するための2次元配列を初期化
    results = [[0.0 for _ in range(axis2_steps)] for _ in range(axis1_steps)]
    
    # ===============================
    # 測定ループ開始
    # ===============================    

    # 測定ループ開始
    for i in range(axis1_steps):
        for j in range(axis2_steps):
            # 1軸方向に移動
            move1 = axis1_initial_position + i * axis1_step_size if axis1_direction == "+" else axis1_initial_position - i * axis1_step_size
            stage_controller.moveAbs(2, move1)
            # 2軸方向に移動
            move2 = axis2_initial_position + j * axis2_step_size if axis2_direction == "+" else axis2_initial_position - j * axis2_step_size
            stage_controller.moveAbs(4, move2)
            # 移動後待機
            time.sleep(wait_time/1000)
            print(f"スキャン中... 1軸: {i+1}/{axis1_steps}, 2軸: {j+1}/{axis2_steps}")
            # *******************************
            # ここに測定処理を記述
            # *******************************
            # 測定結果をリストに追加（例としてダミーデータを追加）
            results[i][j] = i + j
            
            # ヒートマップを描画(この処理のままだと遅いです)
            fig, ax = plt.subplots()
            sns.heatmap(results, annot=True, cmap="viridis", ax=ax)
            ax.set_title("heatmap")
            ax.set_xlabel("2axis step")
            ax.set_ylabel("1axis step")

            # Streamlitに表示
            placeholder.pyplot(fig)

    # 測定結果をCSVファイルに保存
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    sweep_conditions = f"_{axis1_initial_position}_{axis1_step_size}_{axis1_steps}_{axis1_direction}_{axis2_initial_position}_{axis2_step_size}_{axis2_steps}_{axis2_direction}_{wait_time}ms"
    csv_file_path = os.path.join(save_folder, save_file_name + sweep_conditions + "_" + timestamp)
    with open(csv_file_path+".csv", "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        # 測定結果を書き込む
        csvwriter.writerows(results)
    
    stage_controller.moveBasePosition()
    st.success("スキャンが完了しました。")
    # ===============================


    
# 入力された値を表示
st.write("1軸初期位置:", axis1_initial_position)
st.write("1軸ステップ幅:", axis1_step_size)
st.write("1軸ステップ数:", axis1_steps)
st.write("1軸移動方向:", axis1_direction)
st.write("2軸初期位置:", axis2_initial_position)
st.write("2軸ステップ幅:", axis2_step_size)
st.write("2軸ステップ数:", axis2_steps)
st.write("2軸移動方向:", axis2_direction)
st.write("待機時間:", wait_time)
st.write("保存フォルダ:", save_folder)
>>>>>>> 33cf9df3bde27ecbf3980b30826af3a28889b4f3
st.write("保存ファイル名:", save_file_name)