from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.constants import Endian
from pymodbus.client import ModbusTcpClient
import time
from robot.enumRobotCommand import eRobotCommand 
# 自訂例外
class RequestErrorExpection(Exception):
    def __init__(self, message=f"Request error.", error_code=1):
        super().__init__(message)
        self.error_code = error_code
class Robot:
    def __init__(self, modbusTCPClient=None, host=None, motionBlock=False, motionBlockTime = 0.1, suction_DO_Number = 0b0000000000000001):
        """
        Robot 類別的建構函數
        - 如果提供 modbusTCPClient，則使用該連接
        - 如果提供 host，則會自動建立連接
        - 如果兩者都未提供，則不會自動連接
        """
        if modbusTCPClient:
            self.modbusTCPClient = modbusTCPClient
            if not self.modbusTCPClient.is_socket_open():
                self.modbusTCPClient.connect()
        elif host:
            self.modbusTCPClient = ModbusTcpClient(host)
            self.modbusTCPClient.connect()
        else:
            self.modbusTCPClient = None

        #定義屬性：
        self.__block = motionBlock                                              #定義所有的動作函式是否需要做block
        self.__blockTime = motionBlockTime                                      #定義在block的時候要等多久
        self.__suction_DO_Number = suction_DO_Number                            #定義吸盤的位置(預設在DO_0)
        

    def __del__(self):
        """
        解構函數，在物件銷毀時自動斷開 Modbus 連接
        """
        if self.modbusTCPClient:
            self.modbusTCPClient.close()

    ########################################################################
    @property
    def isRobotReachTargetPosition(self):
        """
        定義屬性getter：檢查Robot是否到達位置
        """
        return self.Get_Pose_Flag() == 1
    
    ########################################################################
    def Get_TCP_Pose(self):
        """
        從機械手臂讀取 TCP 位姿 (X, Y, Z, Rx, Ry, Rz)
        """
        request = self.modbusTCPClient.read_holding_registers(0x00F0, 12, 2)
        if request.isError():
            raise RequestErrorExpection("Request error.")

        # 解碼 X, Y, Z, Rx, Ry, Rz# 解碼 X, Y, Z, Rx, Ry, Rz，使用迴圈來簡化
        positions = []
        for i in range(0, 12, 2):
            decoder = BinaryPayloadDecoder.fromRegisters(request.registers[i:i+2], Endian.BIG, wordorder=Endian.LITTLE)
            positions.append(decoder.decode_32bit_int() * 0.001)

        # 將解碼後的值分別賦值給 x, y, z, rx, ry, rz
        x, y, z, rx, ry, rz = positions


        return x, y, z, rx, ry, rz

    def Get_Pose_Flag(self):
        """
        獲取當前機械手臂的位姿狀態標誌
        """

        request = self.modbusTCPClient.read_holding_registers(0x031F, 1, 2)
        if request.isError():
            raise RequestErrorExpection("Request error.")
        return request.registers[0]


    def waitRobotReachTargetPosition(self):
        """
        等待機械手臂運動完成
        """
        while not self.isRobotReachTargetPosition:
            time.sleep(self.__blockTime)


    def Send_Motion_Command(self, *args, speed=10, acceleration=10, deceleration=10, robotCommand=eRobotCommand.Motion_Stop):
        """
        發送機械手臂運動命令。
        
        參數:
            args: 可以是6個獨立的座標值(x, y, z, rx, ry, rz)或一個包含6個值的list。
            speed: 移動速度 (預設為10)。
            acceleration: 加速度 (預設為10)。
            deceleration: 減速度 (預設為10)。
            robotCommand: 機器人指令，預設為停止命令。
        """
        # 處理 args 輸入的不同狀況
        if len(args) == 1 and isinstance(args[0], list) and len(args[0]) == 6:
            # 當 args 傳入一個含有6個int的list
            x, y, z, rx, ry, rz = args[0]
        elif len(args) == 6:
            # 當 args 傳入6個獨立的座標值
            x, y, z, rx, ry, rz = args
        elif len(args) == 0:
            # 當 args 為 None，不做特別處理
            x, y, z, rx, ry, rz = None, None, None, None, None, None
        else:
            raise ValueError("參數錯誤，應傳入6個座標值或一個包含6個值的list")

        # 檢查 robotCommand 是否是 301~307 (動作命令)
        if robotCommand not in (eRobotCommand.Robot_Go_MovP, eRobotCommand.Robot_Go_MovL, 
                                eRobotCommand.Robot_Go_MultiMoveJ, eRobotCommand.Robot_Go_MArchP, 
                                eRobotCommand.Robot_Go_MArchL, eRobotCommand.Robot_All_Joints_Homing_To_Origin):
            # 如果 robotCommand 不是 301~307，且 args 為 None，則拋出例外
            if x is None:
                raise AssertionError("動作命令不正確且未提供座標")
        else:
            # 如果 robotCommand 是 301~307，且有座標數據，則發送命令
            if x is not None:
                # 構建 Payload
                builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
                builder.add_32bit_int(int(x * 1000))
                builder.add_32bit_int(int(y * 1000))
                builder.add_32bit_int(int(z * 1000))
                builder.add_32bit_int(int(rx * 1000))
                builder.add_32bit_int(int(ry * 1000))
                builder.add_32bit_int(int(rz * 1000))
                payload = builder.to_registers()

                # 設定速度、加速度、減速度
                self.modbusTCPClient.write_register(0x0324, speed, 2)  # 設定速度
                self.modbusTCPClient.write_register(0x030A, acceleration, 2)  # 設定加速度
                self.modbusTCPClient.write_register(0x030C, deceleration, 2)  # 設定減速度

                # 發送位姿命令到 0x0330 地址
                self.modbusTCPClient.write_registers(0x0330, payload, 2)

        # 發送 robotCommand 到 0x0300 地址
        self.modbusTCPClient.write_register(0x0300, robotCommand.value, 2)


    def Go_Position(self, *args, speed=20, robotCommand = eRobotCommand.Motion_Stop):
        """
        讓機械手臂移動到指定的位置 (X, Y, Z, Rx, Ry, Rz)
        """
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)

        # 根據參數將位置數據加入到 payload 中
        if len(args) == 6:
            for value in args:
                builder.add_32bit_int(int(value * 1000))
        elif len(args) == 1 and isinstance(args[0], list) and len(args[0]) == 6:
            for value in args[0]:
                builder.add_32bit_int(int(value * 1000))
        else:
            raise ValueError("參數錯誤，應傳入 6 個座標值或一個包含 6 個值的 list")

        payload = builder.to_registers()

        # 設置移動速度和目標位姿
        self.modbusTCPClient.write_register(0x0324, speed, 2)
        self.modbusTCPClient.write_registers(0x0330, payload, 2)

        #執行命令
        self.modbusTCPClient.write_register(0x0300, robotCommand, 2)

        print("Start moving...")

        # 如果 block 為 True，等待運動完成
        if self.__block:
            self.waitRobotReachTargetPosition()
        print("Move done!")

    def Suction_ON(self):
        """
        打開吸盤
        """
        self.modbusTCPClient.write_register(0x02FE, self.__suction_DO_Number, 2)

    def Suction_OFF(self):
        """
        關閉吸盤
        """
        self.modbusTCPClient.write_register(0x02FE, 0, 2)

    def Jog_Position(self, *args):
        """
        手動模式移動機械手臂
        """
        if len(args) == 1 and isinstance(args[0], list) and len(args[0]) == 6:
            x, y, z, rx, ry, rz = args[0]
        elif len(args) == 6:
            x, y, z, rx, ry, rz = args
        else:
            raise ValueError("必須傳入6個數值或一個包含6個數值的list")

        # 根據方向參數控制 Jog 移動
        if x > 0:
            self.modbusTCPClient.write_registers(0x0300, eRobotCommand.Continue_JOG_X_Positive, 2)
        elif x < 0:
            self.modbusTCPClient.write_registers(0x0300, eRobotCommand.Continue_JOG_X_Negative, 2)
        if y > 0:
            self.modbusTCPClient.write_registers(0x0300, eRobotCommand.Continue_JOG_Y_Positive, 2)
        elif y < 0:
            self.modbusTCPClient.write_registers(0x0300, eRobotCommand.Continue_JOG_Y_Negative, 2)
        if z > 0:
            self.modbusTCPClient.write_registers(0x0300, eRobotCommand.Continue_JOG_Z_Positive, 2)
        elif z < 0:
            self.modbusTCPClient.write_registers(0x0300, eRobotCommand.Continue_JOG_Z_Negative, 2)
        if rx > 0:
            self.modbusTCPClient.write_registers(0x0300, eRobotCommand.Continue_JOG_RX_Positive, 2)
        elif rx < 0:
            self.modbusTCPClient.write_registers(0x0300, eRobotCommand.Continue_JOG_RX_Negative, 2)
        if ry > 0:
            self.modbusTCPClient.write_registers(0x0300, eRobotCommand.Continue_JOG_RY_Positive, 2)
        elif ry < 0:
            self.modbusTCPClient.write_registers(0x0300, eRobotCommand.Continue_JOG_RY_Negative, 2)
        if rz > 0:
            self.modbusTCPClient.write_registers(0x0300, eRobotCommand.Continue_JOG_RZ_Positive, 2)
        elif rz < 0:
            self.modbusTCPClient.write_registers(0x0300, eRobotCommand.Continue_JOG_RZ_Negative, 2)

    def Jog_Stop(self):
        """
        停止機械手臂的 Jog 模式運動
        """
        self.modbusTCPClient.write_registers(0x0300, 0, 2)

    def Motion_Stop(self):
        """
        停止所有運動
        """
        self.modbusTCPClient.write_registers(0x0300, 1000, 2)
        if self.__block:
            self.waitRobotReachTargetPosition()
