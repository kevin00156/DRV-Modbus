from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
from drv_modbus import request

MovP = 0
MovL = 1

def Go_Position(c, x, y, z, rx, ry, rz, speed=20, mov=0, block=True):#多載1：分別指定x,y,z,rx,ry,rz
    """
    讓機械手臂移動到指定的位置 (X, Y, Z, Rx, Ry, Rz)

    參數:
        c: Modbus TCP 客戶端
        x, y, z: 移動到的目標座標 (米)
        rx, ry, rz: 旋轉角度 (弧度)
        speed: 移動速度 (預設為 20)
        mov: 移動方式 (MovP 或 MovL)
        block: 是否阻塞直到動作完成 (預設為 True)
    """
    # 將座標和旋轉角度轉換為寄存器數據格式
    builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
    builder.add_32bit_int(int(x * 1000))
    builder.add_32bit_int(int(y * 1000))
    builder.add_32bit_int(int(z * 1000))
    builder.add_32bit_int(int(rx * 1000))
    builder.add_32bit_int(int(ry * 1000))
    builder.add_32bit_int(int(rz * 1000))
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

    pos_flag = 2
    while pos_flag != 1:
        pos_flag = request.Get_Pose_Flag(c)
    print("Move done!")

def Go_Position(c, Pose, speed=20, mov=0, block=True):#多載2：直接以一個list將x,y,z,rx,ry,rz包起來
    """
    讓機械手臂移動到指定的位置 (X, Y, Z, Rx, Ry, Rz)

    參數:
        c: Modbus TCP 客戶端
        Pose : 包含x,y,z,rx,ry,rz的list(僅限6個，否則可能出問題)
        speed: 移動速度 (預設為 20)
        mov: 移動方式 (MovP 或 MovL)
        block: 是否阻塞直到動作完成 (預設為 True)
    """
    # 將座標和旋轉角度轉換為寄存器數據格式
    builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
    for element in Pose :
        builder.add_32bit_int(int(element * 1000))
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

    pos_flag = 2
    while pos_flag != 1:
        pos_flag = request.Get_Pose_Flag(c)
    print("Move done!")

def Suction_ON(c):
    """
    打開吸盤

    參數:
        c: Modbus TCP 客戶端
    """
    c.write_register(0x02FE, 1, 2)

def Suction_OFF(c):
    """
    關閉吸盤

    參數:
        c: Modbus TCP 客戶端
    """
    c.write_register(0x02FE, 0, 2)

def Jog_Position(c, x, y, z, rx, ry, rz):
    """
    通過手動模式 (Jog) 控制機械手臂的移動

    參數:
        c: Modbus TCP 客戶端
        x, y, z: 控制手臂在空間中的移動方向 (-1 或 1)
        rx, ry, rz: 控制手臂的旋轉方向
    """
    # 根據方向參數控制各個方向的 Jog 移動
    if x > 0:
        c.write_registers(0x0300, 601, 2)
    if x < 0:
        c.write_registers(0x0300, 602, 2)
    if y > 0:
        c.write_registers(0x0300, 603, 2)
    if y < 0:
        c.write_registers(0x0300, 604, 2)
    if z > 0:
        c.write_registers(0x0300, 605, 2)
    if z < 0:
        c.write_registers(0x0300, 606, 2)
    if rx > 0:
        c.write_registers(0x0300, 607, 2)
    if rx < 0:
        c.write_registers(0x0300, 608, 2)
    if ry > 0:
        c.write_registers(0x0300, 609, 2)
    if ry < 0:
        c.write_registers(0x0300, 610, 2)
    if rz > 0:
        c.write_registers(0x0300, 611, 2)
    if rz < 0:
        c.write_registers(0x0300, 612, 2)

def Jog_Stop(c):
    """
    停止機械手臂的 Jog 模式運動

    參數:
        c: Modbus TCP 客戶端
    """
    c.write_registers(0x0300, 0, 2)
