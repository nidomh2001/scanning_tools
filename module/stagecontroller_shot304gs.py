from setuptools import errors
import pyvisa
import time

READY_CHECK_PERIOD_S = 1/1000

# 1umステージを動かすのに何パルス必要か
#   stage.write(M:1+P1000)を実行したときに
#   1000 /「移動した距離(um)」を求めて代入すればよい
AXIS1_PULSE_PER_UM = 1000 / 1000
AXIS2_PULSE_PER_UM = 1000 / 1000
AXIS3_PULSE_PER_UM = 1000 / 1000
AXIS4_PULSE_PER_UM = 1000 / 1000

#P1000で2mm 2000um

class StageController:
    
    def __init__(self):
        try:
            rm = pyvisa.ResourceManager()
            # GPIB0の番号は使用するステージコントローラに合わせて変更
            self.stage = rm.open_resource('GPIB0::8::INSTR')
            self.waitReady()
            self.setSpeed()
            self.waitReady()
        except ValueError as e:
            print(f"無効なパラメータが指定されました: {e}")
        except OSError as e:
            print(f"OSレベルでエラーが発生しました: {e}")
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e}")
        pass
    
    def setSpeed(self):
        # 使用するステージに応じて数値を変更。どう変更するかは試して探せ
        self.stage.query("D:WS2500F50000R100S2500F50000R100S2500F50000R100S2500F50000R100")
        self.waitReady()
    
    def moveBasePosition(self):
        self.moveAbs(1, 0)
        self.moveAbs(2, 0)
        self.moveAbs(3, 0)
        self.moveAbs(4, 0)
    
    def moveAbs(self, axis, position_um, direction='+', wait_time_s=0.0):
        if axis == 1:
            num_pulse = int(position_um * AXIS1_PULSE_PER_UM)
        elif axis == 2:
            num_pulse = int(position_um * AXIS2_PULSE_PER_UM)
        elif axis == 3:
            num_pulse = int(position_um * AXIS3_PULSE_PER_UM)
        elif axis == 4:
            num_pulse = int(position_um * AXIS4_PULSE_PER_UM)
        else:
            raise ValueError(f"無効な軸番号が指定されました: {axis}")
        
        wdata = "A:" + str(axis) + direction + "P" + str(num_pulse)
        # print(wdata)
        self.stage.write(wdata)
        self.waitReady() 
        self.stage.write("G:")
        self.waitReady() 
        if wait_time_s > 0.0:
            time.sleep(wait_time_s)
    
    def waitReady(self):
        while(1):
            if(self.stage.query("!:") == 'R') : break
            time.sleep(READY_CHECK_PERIOD_S)
            
    def forceMoveZeroPosition(self):
        self.stage.write("J:W----")
        self.stage.write("G:")
        self.waitReady()
        self.stage.write("R:W")
        

if __name__ == '__main__':
    stage_controller = StageController()

    print("0位置に強制移動")
    stage_controller.forceMoveZeroPosition()
    
    # 1000パルス分移動（ここを利用してAXIS1_PULSE_PER_UM, AXIS2_PULSE_PER_UMを求める）
    print("1000パルス分移動")
    stage_controller.stage.write("M:4+P1000")
    stage_controller.stage.write("G:")
    stage_controller.waitReady()
    time.sleep(5)   # 5秒待つ
    
    # 初期位置に戻す
    print("初期位置に戻す")
    stage_controller.moveBasePosition()
    stage_controller.waitReady()
    
    # 試しに10000um移動し、1秒待って初期位置に戻す
    stage_controller.moveAbs(4, 10000)
    time.sleep(1)
    stage_controller.moveBasePosition()
    