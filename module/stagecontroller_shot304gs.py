from setuptools import errors
import pyvisa
import time

READY_CHECK_PERIOD_S = 1/1000

# TODO: BASE_LATEの値は使用するステージのネジリード[mm] × 20
# 例1: ネジリード1mmのSGSP20-35の場合 ：BASE_LATE = 1 × 20 = 20
# 例2: ネジリード2mmのSGSP26-150の場合：BASE_LATE = 2 × 20 = 40
BASE_LATE1 = 40 # 軸1のBASE_LATE
BASE_LATE2 = 40 # 軸2のBASE_LATE
BASE_LATE3 = 40 # 軸1のBASE_LATE
BASE_LATE4 = 40 # 軸2のBASE_LATE
# TODO: ステージコントローラのメモリスイッチの値も同様に設定してください

class StageController:
    
    def __init__(self):
        self.connected = False
        try:
            rm = pyvisa.ResourceManager()
            # ============================
            # ここでGPIBデバイスをリストアップ
            # ============================
            resources = rm.list_resources()
            gpib_devices = [resource for resource in resources if 'GPIB' in resource]
            print("Connected GPIB devices:")
            for device in gpib_devices:
                print(device)
            # ============================
            # TODO: GPIB0の番号は使用するステージコントローラに合わせて変更
            # ============================
            self.stage = rm.open_resource('GPIB0::8::INSTR')
            # ============================
            self.connected = True
            self.waitReady()
            
            # 速度設定
            self.setSpeed()
            
            # 分解能
            self.axis1_resolution_um = 1
            self.axis2_resolution_um = 1
            self.axis3_resolution_um = 1
            self.axis4_resolution_um = 1
            self.setResolution(self.axis1_resolution_um, self.axis2_resolution_um, self.axis3_resolution_um, self.axis4_resolution_um)
            
        except ValueError as e:
            print(f"無効なパラメータが指定されました: {e}")
        except OSError as e:
            print(f"OSレベルでエラーが発生しました: {e}")
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e}")
    
    def list_gpib_devices(self):
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()
        gpib_devices = [resource for resource in resources if 'GPIB' in resource]
        print("Connected GPIB devices:")
        for device in gpib_devices:
            print(device)
    
    def check_connection(self):
        if not self.connected:
            print("ステージコントローラに接続されていません。")
            return False
        return True
    
    # 使用するステージに応じて数値を変更。どう変更するかは試して探せ
    def setSpeed(
        self, 
        ax1_min_speed=2000, ax1_max_speed=5000, ax1_acceleration=100,
        ax2_min_speed=2000, ax2_max_speed=5000, ax2_acceleration=100,
        ax3_min_speed=2000, ax3_max_speed=5000, ax3_acceleration=100,
        ax4_min_speed=2000, ax4_max_speed=5000, ax4_acceleration=100):
        if not self.check_connection():
            return
        self.stage.query(f"D:WS{ax1_min_speed}F{ax1_max_speed}R{ax1_acceleration}S{ax2_min_speed}F{ax2_max_speed}R{ax2_acceleration}T{ax3_min_speed}F{ax3_max_speed}R{ax3_acceleration}U{ax4_min_speed}F{ax4_max_speed}R{ax4_acceleration}")
        self.waitReady()
        
    # 分解能の設定
    # axis1_resolution: Axis 1の分解能[um]
    # axis2_resolution: Axis 2の分解能[um]
    # axis3_resolution: Axis 3の分解能[um]
    # axis4_resolution: Axis 4の分解能[um]
    # 分解能は次の値のいずれかを指定することができます[um]: 2, 1, 0.5, 0.4, 0.25, 0.2, 0.1, 0.08, 0.05, 0.04, 0.025, 0.02, 0.016, 0.01, 0.008
    # 分解能を細かくすればするほど1パルス当たりの移動量が小さくなります。そのため、細かく動かすことができますが、その代わり移動速度が遅くなります。
    # クローズドループ制御を行う際はステージのセンサー分解能以上に設定してください
    def setResolution(self, axis1_resolution=1, axis2_resolution=1, axis3_resolution=1, axis4_resolution=1):
        valid_resolutions_um = [2, 1, 0.5, 0.4, 0.25, 0.2, 0.1, 0.08, 0.05, 0.04, 0.025, 0.02, 0.016, 0.01, 0.008]
        if not self.check_connection():
            return
        if axis1_resolution not in valid_resolutions_um or axis2_resolution not in valid_resolutions_um or axis3_resolution not in valid_resolutions_um or axis4_resolution not in valid_resolutions_um:
            print("無効な分解能が指定されました。許可されている分解能は次の通りです[um]:", valid_resolutions_um)
            return
        self.axis1_resolution_um = axis1_resolution
        self.axis2_resolution_um = axis2_resolution
        self.axis3_resolution_um = axis3_resolution
        self.axis4_resolution_um = axis4_resolution
        self.stage.write(f"S:1{int(2/axis1_resolution)}")
        self.stage.write(f"S:2{int(2/axis2_resolution)}")
        self.stage.write(f"S:3{int(2/axis3_resolution)}")
        self.stage.write(f"S:4{int(2/axis4_resolution)}")
        print(f"S:1{int(2/axis1_resolution)}")
        print(f"S:2{int(2/axis2_resolution)}")
        print(f"S:3{int(2/axis3_resolution)}")
        print(f"S:4{int(2/axis4_resolution)}")
        print(f"Resolution set to Axis 1: {axis1_resolution}, Axis 2: {axis2_resolution}, Axis 3: {axis3_resolution}, Axis 4: {axis4_resolution}")
        self.waitReady()
    
    # 絶対位置移動
    def moveAbs(self, axis, position_um, direction='+', wait_time_s=0.0):
        if not self.check_connection():
            return
        if axis == 1:
            num_pulse = int(position_um * 20 / (BASE_LATE1 * self.axis1_resolution_um))
        elif axis == 2:
            num_pulse = int(position_um * 20 / (BASE_LATE2 * self.axis2_resolution_um))
        elif axis == 3:
            num_pulse = int(position_um * 20 / (BASE_LATE3 * self.axis3_resolution_um))
        elif axis == 4:
            num_pulse = int(position_um * 20 / (BASE_LATE4 * self.axis4_resolution_um))
        else:
            raise ValueError(f"無効な軸番号が指定されました: {axis}")
        
        wdata = "A:" + str(axis) + direction + "P" + str(num_pulse)
        print(wdata)
        self.stage.write(wdata)
        self.waitReady() 
        self.stage.write("G:")
        self.waitReady() 
        if wait_time_s > 0.0:
            time.sleep(wait_time_s)
    
    # 相対位置移動
    def moveRel(self, axis, distance_um, direction='+', wait_time_s=0.0):
        if not self.check_connection():
            return
        if axis == 1:
            num_pulse = int(distance_um * 20 / (BASE_LATE1 * self.axis1_resolution_um))
        elif axis == 2:
            num_pulse = int(distance_um * 20 / (BASE_LATE2 * self.axis2_resolution_um))
        elif axis == 3:
            num_pulse = int(distance_um * 20 / (BASE_LATE3 * self.axis3_resolution_um))
        elif axis == 4:
            num_pulse = int(distance_um * 20 / (BASE_LATE4 * self.axis4_resolution_um))
        else:
            raise ValueError(f"無効な軸番号が指定されました: {axis}")
        
        wdata = "M:" + str(axis) + direction + "P" + str(num_pulse)
        print(wdata)
        self.stage.write(wdata)
        self.waitReady() 
        self.stage.write("G:")
        self.waitReady() 
        if wait_time_s > 0.0:
            time.sleep(wait_time_s)
    
    # ステージが動作可能な状態になるまで待機（レディーチェック）
    def waitReady(self):
        if not self.check_connection():
            return
        while(1):
            if(self.stage.query("!:") == 'R') : break
            time.sleep(READY_CHECK_PERIOD_S)
    
    # 機械原点復帰命令
    # 移動速度はメモリスイッチの ORG1 ～ 4 （S、F、R）で設定された値で動作します。
    def moveToHomePosition(self, axis):
        if not self.check_connection():
            return
        self.stage.write(f"H:{axis}")  
        self.waitReady()
        

if __name__ == '__main__':
    # ステージコントローラの初期化
    stage_controller = StageController()
    
    # 原点に戻る
    stage_controller.moveToHomePosition(1)
    time.sleep(1)
    
    # 速度を設定
    stage_controller.setSpeed(2000, 3000, 100, 2000, 3000, 100, 2000, 3000, 100, 2000, 3000, 100)
    
    # 分解能を設定
    stage_controller.setResolution(1, 1, 1, 1)
    
    # 10000 um 移動
    stage_controller.moveAbs(1, 10000)