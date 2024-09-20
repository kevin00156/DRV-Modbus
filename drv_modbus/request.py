from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
import time

# 定義自訂例外
class RequestErrorExpection(Exception):
    def __init__(self, message="default message", error_code=0):
        super().__init__(message)  # 繼承 Exception 類的行為
        self.error_code = error_code  # 可以自訂屬性來保存錯誤碼或其他相關信息


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
        raise RequestErrorExpection("Request error.")

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
        根據台達文件說明，未到位是2，反之是1
        GO to target in position flag(Only for Go function);
        1:in position status;
        2:Robot didn't reach the target point that user set.
        Until robot reach the target point user set,
        it will become to 1. Or the value still is 2.
    """
    request = robot_client.read_holding_registers(0x031F, 1, 2)  # 讀取指定寄存器的pose狀態標誌
    if request.isError():
        raise RequestErrorExpection("Request error.")
    pose_flag = request.registers[0]
    return pose_flag

def isRobotReachTargetPosition(robot_client):
    return Get_Pose_Flag(robot_client) == 1

def waitRobotReachTargetPosition(robot_client):
    """
    以while迴圈 卡住執行緒，直到Robot運動完成的檢查功能
    """
    #卡住執行緒，直到stop動作完成
    while True :
        if isRobotReachTargetPosition(robot_client) :
            break
        time.sleep(0.1)#等待0.1秒避免cpu占用率過高