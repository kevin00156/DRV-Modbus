from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

def Get_TCP_Pose(robot_client):
    """
    從機械手臂讀取 TCP 位姿 (X, Y, Z, Rx, Ry, Rz)
    
    參數:
        robot_client: Modbus TCP 客戶端，用於與機械手臂通信
        
    返回:
        x, y, z: 機械手臂末端執行器的空間座標
        rx, ry, rz: 機械手臂末端的旋轉角度 (Rx, Ry, Rz)
    """
    request = robot_client.read_holding_registers(0x00F0, 12, 2)  # 讀取 12 個保持寄存器

    if request.isError():
        print("request error!")
        return

    # 從寄存器中解碼 X, Y, Z, Rx, Ry, Rz 的值
    decoder_x = BinaryPayloadDecoder.fromRegisters(request.registers[:2], Endian.BIG, wordorder=Endian.LITTLE)
    decoder_y = BinaryPayloadDecoder.fromRegisters(request.registers[2:4], Endian.BIG, wordorder=Endian.LITTLE)
    decoder_z = BinaryPayloadDecoder.fromRegisters(request.registers[4:6], Endian.BIG, wordorder=Endian.LITTLE)
    decoder_rx = BinaryPayloadDecoder.fromRegisters(request.registers[6:8], Endian.BIG, wordorder=Endian.LITTLE)
    decoder_ry = BinaryPayloadDecoder.fromRegisters(request.registers[8:10], Endian.BIG, wordorder=Endian.LITTLE)
    decoder_rz = BinaryPayloadDecoder.fromRegisters(request.registers[10:], Endian.BIG, wordorder=Endian.LITTLE)

    # 解析每個座標，並將其縮放到米
    x  = decoder_x.decode_32bit_int() * 0.001
    y  = decoder_y.decode_32bit_int() * 0.001
    z  = decoder_z.decode_32bit_int() * 0.001
    rx = decoder_rx.decode_32bit_int() * 0.001
    ry = decoder_ry.decode_32bit_int() * 0.001
    rz = decoder_rz.decode_32bit_int() * 0.001

    return x , y , z , rx, ry, rz

def Get_Pose_Flag(robot_client):
    """
    獲取當前機械手臂的位姿狀態標誌
    
    參數:
        robot_client: Modbus TCP 客戶端
    
    返回:
        pose_flag: 表示位姿的標誌
    """
    request = robot_client.read_holding_registers(0x031F, 1, 2)  # 讀取指定寄存器的位姿狀態標誌
    if request.isError():
        print("request error!")
        return
    pose_flag = request.registers[0]
    return pose_flag
