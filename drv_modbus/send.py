from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
from drv_modbus import request
from pymodbus.client import ModbusTcpClient
from deprecated import deprecated
import warnings
MovP = 0
MovL = 1

"""
this library has been deprecated
"""

warnings.warn(f"此庫{__name__} 已被棄用，請使用robot.classRobot", DeprecationWarning, stacklevel=2)

@deprecated(reason="this function has been deprecated, please use robot.classRobot.sendMotionCommand() instead")
def Go_Position(c, *args, speed=20, mov=0, block=True):
    Warning("this function has been deprecated")
    """
    讓機械手臂移動到指定的位置 (X, Y, Z, Rx, Ry, Rz)

    參數:
        c: Modbus TCP 客戶端
        *args: x, y, z, rx, ry, rz 或一個包含x, y, z, rx, ry, rz的list
        speed: 移動速度 (預設為 20)
        mov: 移動方式 (MovP 或 MovL)
        block: 是否阻塞直到動作完成 (預設為 True)
    """
    
    builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
    
    # 如果傳入的是單獨的 x, y, z, rx, ry, rz
    if len(args) == 6:
        x, y, z, rx, ry, rz = args
        builder.add_32bit_int(int(x * 1000))
        builder.add_32bit_int(int(y * 1000))
        builder.add_32bit_int(int(z * 1000))
        builder.add_32bit_int(int(rx * 1000))
        builder.add_32bit_int(int(ry * 1000))
        builder.add_32bit_int(int(rz * 1000))
    # 如果傳入的是一個包含 x, y, z, rx, ry, rz 的 list
    elif len(args) == 1 and isinstance(args[0], list) and len(args[0]) == 6:
        Pose = args[0]
        for element in Pose:
            builder.add_32bit_int(int(element * 1000))
    else:
        raise ValueError("參數錯誤，應傳入 6 個座標值或一個包含 6 個值的 list")
    
    payload = builder.to_registers()

    # 設置移動速度和目標位姿
    c.write_register(0x0324, speed, 2)
    c.write_registers(0x0330, payload, 2)

    # 執行 MovP 或 MovL 動作
    if mov == MovP:
        print("MovP")
        c.write_register(0x0300, 301, 2)
    if mov == MovL:
        print("MovL")
        c.write_register(0x0300, 302, 2)

    print("Start moving...")

    # 若 block 為 True，等待移動完成
    if block == False:
        return

    request.waitRobotReachTargetPosition(c)#等待robot運動完成
    print("Move done!")


@deprecated(reason="this function has been deprecated, please use robot.classRobot.suctionON() instead")
def Suction_ON(c):
    Warning("this function has been deprecated")
    """
    打開吸盤

    參數:
        c: Modbus TCP 客戶端

    對指定地址寫入"1"，以啟用DO_1。
    注意：要更改輸出的DO目標，請根據二進制處理
    """
    c.write_register(0x02FE, 1, 2)
    #c.write_register(0x02FE, int(0b0000000000000001), 2) #如果需要使用二進制寫值 可以使用這行

@deprecated(reason="this function has been deprecated, please use robot.classRobot.suctionOFF() instead")
def Suction_OFF(c):
    Warning("this function has been deprecated")
    """
    關閉吸盤

    參數:
        c: Modbus TCP 客戶端
    """
    c.write_register(0x02FE, 0, 2)#將所有Output設為0
    #附註：如果你只想對某個output設為0，可以先讀取當前output的值，再將當前output的某個bit反轉，再傳送，就可以達到要求功能

@deprecated(reason="this function has been deprecated, please use robot.classRobot.sendMotionCommand() instead")
def Jog_Position(c, *args):
    Warning("this function has been deprecated")
    """
    通過手動模式 (Jog) 控制機械手臂的移動
    支援兩種呼叫方式:
      1. Jog_Position(c, x, y, z, rx, ry, rz)
      2. Jog_Position(c, [x, y, z, rx, ry, rz])

    參數:
        c: Modbus TCP 客戶端
        args: 可以是6個獨立的數值 x, y, z, rx, ry, rz 或一個長度為6的list
    """
    if len(args) == 1 and isinstance(args[0], list) and len(args[0]) == 6:
        # 如果傳入的是一個 list
        x, y, z, rx, ry, rz = args[0]
        print("send args with list")
        
    elif len(args) == 6:
        # 如果傳入的是 6 個獨立的數值
        x, y, z, rx, ry, rz = args
        print("send args respectively")
    else:
        raise ValueError("必須傳入6個數值，或一個包含6個數值的 list")
    


    print(f"{args}")
    print(f"{x, y, z, rx, ry, rz}")
    # 根據方向參數控制各個方向的 Jog 移動
    if x > 0:
        c.write_registers(0x0300, 601, 2)
    elif x < 0:
        c.write_registers(0x0300, 602, 2)
    
    if y > 0:
        c.write_registers(0x0300, 603, 2)
    elif y < 0:
        c.write_registers(0x0300, 604, 2)
    
    if z > 0:
        c.write_registers(0x0300, 605, 2)
    elif z < 0:
        c.write_registers(0x0300, 606, 2)
    
    if rx > 0:
        c.write_registers(0x0300, 607, 2)
    elif rx < 0:
        c.write_registers(0x0300, 608, 2)
    
    if ry > 0:
        c.write_registers(0x0300, 609, 2)
    elif ry < 0:
        c.write_registers(0x0300, 610, 2)
    
    if rz > 0:
        c.write_registers(0x0300, 611, 2)
    elif rz < 0:
        c.write_registers(0x0300, 612, 2)


@deprecated(reason="this function has been deprecated, please use robot.classRobot.motionStop() instead")
def Jog_Stop(c):
    Warning("this function has been deprecated")
    """
    停止機械手臂的 Jog 模式運動

    參數:
        c: Modbus TCP 客戶端
    """
    c.write_registers(0x0300, 0, 2)

@deprecated(reason="this function has been deprecated, please use robot.classRobot.motionStop() instead")
def Motion_Stop(c,block = False):
    Warning("this function has been deprecated")
    """
    停止所有運動(測試中)

    參數:
        c: Modbus TCP 客戶端

    利用0x0300地址的function code 1000 來停止運動功能，並根據需求堵塞流程，直到確定手臂已停下
    """
    c.write_registers(0x0300, 1000, 2)
    if block==False :#若不須堵塞，則直接Return
        return
    
    request.waitRobotReachTargetPosition(c)#等待robot運動完成
    