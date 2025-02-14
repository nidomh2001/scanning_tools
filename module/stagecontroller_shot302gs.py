from setuptools import errors
import pyvisa
import time

READY_CHECK_PERIOD_S = 1/1000

# ステージによって1umステージを動かすのに何パルス必要か変わるので、
# stage.write(M:1+P1000)を実行したときに何um動くかを調べておく
AXIS1_UM_PER_PULSE = 1000 / 1000
AXIS2_UM_PER_PULSE = 1000 / 1000

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
            self.waitReady()
            self.setSpeed()
            self.waitReady()
            self.connected = True
        except ValueError as e:
            print(f"無効なパラメータが指定されました: {e}")
        except OSError as e:
            print(f"OSレベルでエラーが発生しました: {e}")
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e}")
    
    def check_connection(self):
        if not self.connected:
            print("ステージコントローラに接続されていません。")
            return False
        return True
    
    def list_gpib_devices(self):
        if not self.check_connection():
            return
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()
        gpib_devices = [resource for resource in resources if 'GPIB' in resource]
        print("Connected GPIB devices:")
        for device in gpib_devices:
            print(device)
    
    def setSpeed(
        self, 
        ax1_min_speed=2000, ax1_max_speed=5000, ax1_acceleration=100,
        ax2_min_speed=2000, ax2_max_speed=5000, ax2_acceleration=100):
        if not self.check_connection():
            return
        # 使用するステージに応じて数値を変更。どう変更するかは試して探せ
        self.stage.query(f"D:WS{ax1_min_speed}F{ax1_max_speed}R{ax1_acceleration}S{ax2_min_speed}F{ax2_max_speed}R{ax2_acceleration}")
        self.waitReady()
    
    def moveBasePosition(self):
        if not self.check_connection():
            return
        self.moveAbs(1, 0)
        self.moveAbs(2, 0)
    
    def moveAbs(self, axis, position_um, direction='+', wait_time_s=0.0):
        if not self.check_connection():
            return
        if axis == 1:
            num_pulse = int(position_um / AXIS1_UM_PER_PULSE)
        elif axis == 2:
            num_pulse = int(position_um / AXIS2_UM_PER_PULSE)
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
    
    def waitReady(self):
        if not self.check_connection():
            return
        while(1):
            if(self.stage.query("!:") == 'R\r\n') : break
            time.sleep(READY_CHECK_PERIOD_S)
            
    def forceMoveZeroPosition(self):
        if not self.check_connection():
            return
        self.stage.write("J:W----")
        self.stage.write("G:")
        self.waitReady()
        self.stage.write("R:W")
    
    # 機械原点復帰命令
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
    
    # 10000 um 移動
    stage_controller.moveAbs(1, 10000)
    
    # 1000パルス分移動（ここを利用してAXIS_UM_PER_PULSEを求める）
    # print("1000パルス分移動")
    # stage_controller.stage.write("M:1+P1000")
    # stage_controller.stage.write("G:")
    # stage_controller.waitReady()
    # time.sleep(5)   # 5秒待つ
