
import time
import threading
from typing import Union, Tuple, Optional


import time
import threading
from typing import Union, Tuple, Optional

from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.constants import Endian
from pymodbus.client import ModbusTcpClient


from robot.enumRobotCommand import eRobotCommand
# 自訂例外
class RequestErrorException(Exception):
    def __init__(self, message: str = "Request error.", errorCode: int = 1):
        super().__init__(message)
        self.errorCode = errorCode

class RobotErrorException(Exception):
    def __init__(self, message: str = "Robot error.", errorCode : int = 1):
        super().__init__(message)
        self.errorCode = errorCode

class RobotErrorException(Exception):
    def __init__(self, message: str = "Robot error.", errorCode : int = 1):
        super().__init__(message)
        self.errorCode = errorCode

###########################################################
def clearBit(num: int, *args: int) -> int:
    # 創建遮罩，將第 n 位設為 0，其他位設為 1
    operationBits = args
    for bit in operationBits:
        mask = ~(1 << bit)
    # 對 num 進行按位 AND 操作
    return num & mask

def setBit(num: int, *args: int) -> int:
    # 創建遮罩，將第 n 位設為 1，其他位保持不變
    operationBits = args
    for bit in operationBits:
        mask = 1 << bit
    # 對 num 進行按位 OR 操作
    return num | mask

class Robot:
    """
    Robot 類別

    這個類別提供了控制台達機器人的各種功能。

    主要功能:
    1. 移動控制: 可以控制機器人移動到指定位置或執行特定運動命令。
    2. 狀態查詢: 可以獲取機器人的當前位置、錯誤代碼、運動狀態等資訊。
    3. IO控制: 可以控制機器人的數位輸出，如吸盤的開關。
    4. 系統控制，如AllAxisEnable(),AllAxisDisable(), resetRobotError()等
    使用方法:
    1. 初始化: 創建 Robot 物件時，可以提供 ModbusTcpClient 或主機地址。
    2. 移動命令: 使用 sendMotionCommand() 方法發送移動指令。
    3. 狀態檢查: 使用 getTCPPose(), getRobotErrorCode() 等方法獲取機器人狀態。
    4. IO操作: 使用 suctionON(), suctionOFF(), setIO() 等方法控制輸出。
    5. 自動復歸: prepareRobotForMotion()，可自動做一次reset error->啟動所有伺服
    注意事項:
    - 使用前請確保已正確連接到機器人。
    - 操作時請注意安全，避免碰撞。
    """
    def __init__(self,
                 modbusTCPClient: Optional[ModbusTcpClient] = None,
                 host: Optional[str] = None, port: Optional[int] = None,
                 motionBlock: bool = False,
                 motionBlockTime: float = 0.1,
                 suctionDigitalOutputNumber: int = 0b0000000000000000,
                 defaultSpeed: int = 10,
                 defaultAcceleration: int = 10,
                 defaultDeceleration: int = 10,
                 errorMonitorThreadSleepTime: float = 0.5,
                 closeToTargetThreshold: float = 0.01
                 ):
        """
        Robot 類別的建構函數
        
        args:
        modbusTCPClient: ModbusTcpClient，如果提供，則使用該連接
        host: str，如果提供，則會自動建立連接
        port: int，如果提供，則會自動建立連接
        host與port需要同時提供才會自動建立連接，反之會錯誤
        
        motionBlock: bool，是否需要block動作
        motionBlockTime: float，block的時候要等多久
        suctionDigitalOutputNumber: int，吸盤的數位輸出位置
        defaultSpeed: int，預設速度
        defaultAcceleration: int，預設加速度
        defaultDeceleration: int，預設減速度
        errorMonitorThreadSleepTime: float，錯誤監控執行緒的睡眠時間
        closeToTargetThreshold: float，到達目標位置的閥值
        
        """
        
        #檢查input是否合法
        if modbusTCPClient:
            self.modbusTCPClient = modbusTCPClient
            if not self.modbusTCPClient.is_socket_open():
                self.modbusTCPClient.connect()
        elif host and port:
            self.modbusTCPClient = ModbusTcpClient(host, port)
            self.modbusTCPClient.connect()
        else:
            self.modbusTCPClient = None

        #定義屬性：
        self.__block = motionBlock                                              #定義所有的動作函式是否需要做block
        self.__blockTime = motionBlockTime                                      #定義在block的時候要等多久
        self.__suctionDigitalOutputNumber = suctionDigitalOutputNumber          #定義吸盤的位置(預設在DO_0)，請輸入0~15的值
        self.__latestMotionCommand: Tuple[Optional[float], Optional[float], Optional[float], Optional[float], Optional[float], Optional[float]] = None, None, None, None, None, None 
        self.__latestDigitalOutputCommand = 0
        self.speed = defaultSpeed
        self.acceleration = defaultAcceleration
        self.deceleration = defaultDeceleration
        
        self.errorMonitorThread = threading.Thread(target=self.__monitorErrors)
        self.errorMonitorThread.daemon = True  # 設置為守護執行緒
        self.errorMonitorThreadSleepTime = errorMonitorThreadSleepTime
        self._stopThread = threading.Event()
        self.closeToTargetThreshold = closeToTargetThreshold

    def __del__(self):
        """
        解構函數，在物件銷毀時自動斷開 Modbus 連接
        """
        if self.modbusTCPClient:
            self.modbusTCPClient.close()
        self.stopMonitorErrors
        self.stopMonitorErrors

    ########################################################################
    @property
    def isRobotReachTargetPosition(self) -> bool:
        """
        定義屬性getter：檢查Robot是否到達位置
        """

        return self.getRobotPoseFlag() == 1
     # 定義 block 的 getter 和 setter
    @property
    def block(self) -> bool:
        """返回 block 狀態 (是否需要 block 動作)"""
        return self.__block

    @block.setter
    def block(self, value: bool):
        """設置 block 狀態 (True 或 False)"""
        self.__block = value

    # 定義 blockTime 的 getter 和 setter
    @property
    def blockTime(self) -> float:
        """返回 blockTime 的值 (等待時間)"""
        return self.__blockTime

    @blockTime.setter
    def blockTime(self, value: float):
        """設置 blockTime 的值 (等待時間)"""
        if value >= 0:
            self.__blockTime = value
        else:
            raise ValueError("blockTime 屬性應設為非負數值")

    # 定義 suctionDigitalOutputNumber 的 getter 和 setter
    @property
    def suctionDigitalOutputNumber(self) -> int:
        """返回 suctionDigitalOutputNumber (吸盤 DO 編號)"""
        return self.__suctionDigitalOutputNumber

    @suctionDigitalOutputNumber.setter
    def suctionDigitalOutputNumber(self, value: int):
        """設置 suctionDigitalOutputNumber (吸盤 DO 編號)"""
        if 0 <= value <= 15:
            self.__suctionDigitalOutputNumber = value
        else:
            raise ValueError("suctionDigitalOutputNumber 應設為0到15之間的整數")
        
    @property
    def latestMotionCommand(self) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float], Optional[float], Optional[float]]:
        """
        讀取最近一次的運動命令，用以比較位置
        """
        return self.__latestMotionCommand

    @latestMotionCommand.setter
    def latestMotionCommand(self, position: Union[list[float], Tuple[float, float, float, float, float, float]]):
        """
        保存最近一次的運動命令，用以比較位置
        """
        # 處理 args 輸入的不同狀況
        if isinstance(position,list) and len(position) == 6:
            x, y, z, rx, ry, rz = position
        elif isinstance(position,tuple) and len(position) == 6:
            # 當 args 傳入6個獨立的座標值
            x, y, z, rx, ry, rz = position
        elif position is None:
            # 當 args 為 None，不做特別處理
            x, y, z, rx, ry, rz = None, None, None, None, None, None
        else:
            raise ValueError("參數錯誤，應傳入6個座標值或一個包含6個值的list")
        self.__latestMotionCommand = x, y, z, rx, ry, rz

    @property
    def latestDigitalOutputCommand(self) -> int:
        """
        獲取最近一次的數位輸出命令
        """
        return self.__latestDigitalOutputCommand
    
    @latestDigitalOutputCommand.setter
    def latestDigitalOutputCommand(self, value: int):
        """
        設置最近一次的數位輸出命令
        
        參數:
        value: 要設置的數位輸出命令值
        """
        self.__latestDigitalOutputCommand = value

    @property
    def isRobotError(self) -> bool:
        """
        檢查機器人是否處於錯誤狀態
        
        返回:
        bool: 如果機器人有錯誤則返回True，否則返回False
        """
        error_code = self.getRobotErrorCode()
        return error_code != (0,0,[0,0,0,0,0,0])  # 假設錯誤代碼為0表示沒有錯誤

    @property
    def isRobotReadyForMotion(self) -> bool:
        """
        檢查機器人是否處於可以運動的狀態
        
        返回:
        bool: 如果機器人可以運動則返回True，否則返回False
        """
        return (not self.isRobotError and #self.isRobotReachTargetPosition and 
                self.getTeachPanelState()==0  and
                self.getRobotSystemState()==0)
    @property
    def speed(self) -> int:
        """
        獲取機器人的預設速度
        """
        return self.__speed

    @speed.setter
    def speed(self, value: int):
        """
        設置機器人的預設速度
        
        參數:
        value: 要設置的預設速度值
        """
        if value < 0:
            raise ValueError("速度不能小於0")
        if value > 100:
            raise ValueError("速度不能大於100")
        self.__speed = value
        
        # 設定速度、加速度、減速度
        self.writeRegister(0x0324, value)  # 設定速度

    @property
    def acceleration(self) -> int:
        """
        獲取機器人的預設加速度
        """
        return self.__acceleration

    @acceleration.setter
    def acceleration(self, value: int):
        """
        設置機器人的預設加速度
        
        參數:
        value: 要設置的預設加速度值
        """
        if value < 0:
            raise ValueError("加速度不能小於0")
        if value > 100:
            raise ValueError("加速度不能大於100")
        self.__acceleration = value
        self.writeRegister(0x030A, value)  # 設定加速度

    @property
    def deceleration(self) -> int:
        """
        獲取機器人的預設減速度
        """
        return self.__deceleration

    @deceleration.setter
    def deceleration(self, value: int):
        """
        設置機器人的預設減速度
        
        參數:
        value: 要設置的預設減速度值
        """
        if value < 0:
            raise ValueError("減速度不能小於0")
        if value > 100:
            raise ValueError("減速度不能大於100")
        self.__deceleration = value
        self.writeRegister(0x030C, value)  # 設定減速度

    def getRobotNotReadyReason(self) -> str:
        """
        檢查機器人未準備運動的原因
        檢查項目：
        1. 機器人錯誤碼(包含controllerError, robotGroupError, jointsError)
        #2. 機器人未到達位置
        3. 教導盒未釋放控制權
        #4. 運行模式，非自動模式
        #5. 機器人系統狀態
        返回:
        string: 機器人未準備運動的原因
        """
        reason = ""
        controllerError,robotGroupError,jointsError = self.getRobotErrorCode()
        if controllerError != 0:
            reason += "控制器錯誤碼: " +str(controllerError) + "\n"
        if robotGroupError != 0:
            reason += "機器人組錯誤碼: " +str(robotGroupError) + "\n"
        if jointsError != [0,0,0,0,0,0]:
            reason += "軸錯誤碼: " +str(jointsError) + "\n"
        #if not self.isRobotReachTargetPosition:
        #    reason += "機器人未到達位置" + "\n"
        if self.getTeachPanelState() !=0 :
            reason += "教導盒未釋放控制權" + "\n"
        #if self.getRobotSystemState() != 0:
        #    reason += "機器人系統狀態: " + str(self.getRobotSystemState()) + "\n"
        return reason
    ########################################################################
    def getTCPPose(self) -> Tuple[float, float, float, float, float, float]:
        """
        從機械手臂讀取 TCP 位姿 (X, Y, Z, Rx, Ry, Rz)
        """
        request = self.modbusTCPClient.read_holding_registers(0x00F0, 12, 2)
        if request.isError():
            raise RequestErrorException("Request error.")

        # 解碼 X, Y, Z, Rx, Ry, Rz# 解碼 X, Y, Z, Rx, Ry, Rz，使用迴圈來簡化
        positions = []
        for i in range(0, 12, 2):
            decoder = BinaryPayloadDecoder.fromRegisters(request.registers[i:i+2], Endian.BIG, wordorder=Endian.LITTLE)
            positions.append(decoder.decode_32bit_int() * 0.001)

        # 將解碼後的值分別賦值給 x, y, z, rx, ry, rz
        x, y, z, rx, ry, rz = positions


        return x, y, z, rx, ry, rz

    def getRobotPoseFlag(self) -> int:
        """
        獲取當前機械手臂的位姿狀態標誌
        return 1 表示到達位置，2表示未到達位置
        """

        request = self.modbusTCPClient.read_holding_registers(0x031F, 1, 2)
        if request.isError():
            raise RequestErrorException("Request error.")
        return request.registers[0]


    def waitRobotReachTargetPosition(self):
        """
        等待機械手臂運動完成
        """
        while True:#檢查何時結束
            if self.isRobotReachTargetPosition :
                if self.latestMotionCommand is None :#若沒有提供座標 則只看isRobotReachTargetPosition是否到達
                    return
                if self.isCloseToTarget():#若提供座標 則檢查座標是否到達，到達才return
                    return
            time.sleep(self.__blockTime)

    def isCloseToTarget(self) -> bool:
        """
        檢查機械手臂是否接近目標位置
        :param threshold: 閥值，預設為0.01
        :return: 如果機械手臂到達目標位置，則返回True，否則返回False
        """
        if self.closeToTargetThreshold is None:
            self.closeToTargetThreshold = 0.01
        # 獲取機械手臂的當前位置
        current_pose = self.getTCPPose()
        # 獲取最新的運動命令
        latest_pose = self.__latestMotionCommand
        # 如果最新的運動命令為None，則返回False
        if latest_pose is None:
            return False
        # 計算兩個位置之間的歐幾里得距離
        import numpy as np
        distance = np.linalg.norm(np.array(current_pose) - np.array(latest_pose))
        # 如果距離小於閥值，則返回True，否則返回False
        return distance < self.closeToTargetThreshold

    def sendMotionCommand(
        self, 
        position: Optional[Union[list[float], tuple[float, float, float, float, float, float]]] = None,
        speed: Optional[int] = None,
        acceleration: Optional[int] = None,
        deceleration: Optional[int] = None,
        robotCommand: eRobotCommand = eRobotCommand.Motion_Stop,
        retry: bool = True,
        retryTimes: int = 3,
        retryDelay: int = 1
    ) -> None:
        """
        參數:
            position: 可以是6個獨立的座標值(x, y, z, rx, ry, rz)或一個包含6個值的list。
            speed: 移動速度 (預設為10)。
            acceleration: 加速度 (預設為10)。
            deceleration: 減速度 (預設為10)。
            robotCommand: 機器人指令，預設為停止命令。
            retry: 是否重試，預設為True。
            retryTimes: 重試次數，預設為3次。
            retryDelay: 重試延遲時間，預設為1秒。
        """
        
        if retry:
            for i in range(retryTimes):
                if self.isRobotReadyForMotion:
                    break
                time.sleep(retryDelay)
        
        if not self.isRobotReadyForMotion:
            print("機器人不允許運動")
            return

        if speed is not None:
            self.speed = speed
        if acceleration is not None:
            self.acceleration = acceleration
        if deceleration is not None:
            self.deceleration = deceleration
        #指定不需要提供座標的命令
        positionlessCommand = ( eRobotCommand.Robot_All_Joints_Homing_To_Origin,
                                eRobotCommand.Motion_Stop,
                                eRobotCommand.Continue_JOG_X_Positive, eRobotCommand.Continue_JOG_X_Negative,
                                eRobotCommand.Continue_JOG_Y_Positive, eRobotCommand.Continue_JOG_Y_Negative,
                                eRobotCommand.Continue_JOG_Z_Positive, eRobotCommand.Continue_JOG_Z_Negative,
                                eRobotCommand.Continue_JOG_RX_Positive, eRobotCommand.Continue_JOG_RX_Negative,
                                eRobotCommand.Continue_JOG_RY_Positive, eRobotCommand.Continue_JOG_RY_Negative,
                                eRobotCommand.Continue_JOG_RZ_Positive, eRobotCommand.Continue_JOG_RZ_Negative,
                                eRobotCommand.Continue_JOG_External_Axis_1_Negative, eRobotCommand.Continue_JOG_External_Axis_1_Positive,
                                eRobotCommand.Continue_JOG_External_Axis_2_Negative, eRobotCommand.Continue_JOG_External_Axis_2_Positive,
                                eRobotCommand.Continue_JOG_External_Axis_3_Negative, eRobotCommand.Continue_JOG_External_Axis_3_Positive)
        # 檢查 robotCommand 是否是 301~307 (動作命令)
        if robotCommand not in positionlessCommand:
            # 如果 robotCommand 需要提供座標，且 args 為 None，則拋出例外
            if position is None:
                raise AssertionError("動作命令不正確且未提供座標")
            else:
                # 如果 robotCommand 需要提供座標，且有座標數據，則發送命令
                self.latestMotionCommand = position#解析args為x,y,z,rx,ry,rz 順便紀錄
                x, y, z, rx, ry, rz = self.latestMotionCommand#解出剛紀錄的值
                # 構建 Payload
                builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
                builder.add_32bit_int(int(x * 1000))
                builder.add_32bit_int(int(y * 1000))
                builder.add_32bit_int(int(z * 1000))
                builder.add_32bit_int(int(rx * 1000))
                builder.add_32bit_int(int(ry * 1000))
                builder.add_32bit_int(int(rz * 1000))
                payload = builder.to_registers()

                # 發送位姿命令到 0x0330 地址
                self.writeRegisters(0x0330, payload)

        # 發送 robotCommand 到 0x0300 地址
        self.writeRegister(0x0300, robotCommand.value)
        if not self.__block :#若不等待結束，則retrun
            return
        self.waitRobotReachTargetPosition()#卡住執行緒，直到運動完成
        
    ##############################################################
    def suctionON(self):
        """
        打開吸盤
        """
        self.latestDigitalOutputCommand = setBit(self.latestDigitalOutputCommand,self.suctionDigitalOutputNumber)
        self.writeRegister(0x02FE, self.latestDigitalOutputCommand)

    def suctionOFF(self):
        """
        關閉吸盤
        """
        self.latestDigitalOutputCommand = clearBit(self.latestDigitalOutputCommand,self.suctionDigitalOutputNumber)
        self.writeRegister(0x02FE, 0)

    def setIO(self, *args):#設定數位輸出(以二進制設定)
        """
        設定數位輸出
        """
        if len(args) == 1 and isinstance(args[0], int):#若傳入一個值，則將該值設定為數位輸出(以二進制)
            data = args[0]
        elif len(args) == 2 and isinstance(args[0], int) and isinstance(args[1], bool):#若傳入兩個值，則將該值所指的bit做設定或清除
            if args[0] > 15 or args[0] < 0:
                raise ValueError("參數錯誤，應傳入一個數字或一個0~16的數字及True或False")
            if args[1] == True:
                data = setBit(self.latestDigitalOutputCommand,args[0])
            else:
                data = clearBit(self.latestDigitalOutputCommand,args[0])
        else:
            raise ValueError("參數錯誤，應傳入一個數字或一個0~16的數字及True或False")
        self.latestDigitalOutputCommand = data
        self.writeRegister(0x02FE, self.latestDigitalOutputCommand)
    ##############################################################

    def motionStop(self):
        """
        停止所有運動
        """
        self.writeRegisters(0x0300, [0])
        if self.__block:
            self.waitRobotReachTargetPosition()

    ##############################################################
    #系統層級工作

    def AllAxisEnable(self):
        """
        啟用所有伺服軸
        """
        self.writeRegister(0x0006, int(0x0101))  # 1,2軸
        self.writeRegister(0x0007, int(0x0101))  # 3,4軸
        self.writeRegister(0x0000, int(0x0101))  # 5,6軸
        time.sleep(2)#等待使能的時間
        
    def AllAxisDisable(self):
        """
        禁用所有伺服軸
        """
        self.writeRegister(0x0006, int(0x0000))  # 1,2軸
        self.writeRegister(0x0007, int(0x0000))  # 3,4軸
        self.writeRegister(0x0000, int(0x0000))  # 5,6軸

    def getRobotErrorCode(self):
        """
        獲取機器人錯誤碼
        return:
        tuple(int,int,list[int]): 控制器錯誤碼,機器人組錯誤碼,軸錯誤碼(J1~J6)
        """
        controllerError:int = self.readRegisters(0x01FF)
        robotGroupError:int = self.readRegisters(0x01E0)
        jointsError:list[int] = self.readRegisters(0x0140,16)
        #print(jointsError)
        jointsError = jointsError[-4:]+jointsError[:2]
        
        return controllerError,robotGroupError,jointsError
    
    def getRobotWarningCode(self):
        """
        獲取機器人警告碼
        return:
        
        """
        return self.readRegisters(0x020E)

    def getRobotMotionState(self):
        """
        獲取機器人運動狀態,0表示停止,1表示運動中
        """
        return self.readRegisters(0x00E0)

    def getRobotSystemState(self):
        """
        獲取機器人系統狀態,
        0表示一般狀態,
        2表示機器人停止，功能性暫停觸發,
        3表示機器人運動中，但功能性暫停觸發
        """
        return self.readRegisters(0x0138)

    def getOperationMode(self):
        """
        獲取操作模式狀態,
        0表示非有線,
        1表示T1(速度限制25%，可手自動),
        2表示T2(不限制速度，可手自動),
        3表示自動模式(不限制速度，不可手動)
        """
        return self.readRegisters(0x0139)

    def getTeachPanelState(self):
        """
        獲取TP教導盒啟用狀態,0表示未啟用,1表示啟用 (教導盒啟用時 遠端無法操作機器人)
        """
        return self.readRegisters(0x013B)

    def resetRobotError(self):
        """
        重設機器人錯誤碼
        """
        # 重設機器人錯誤碼
        registers = [257] * 8  # 創建一個包含8個257的列表
        self.writeRegisters(0x0020, registers)  # reset所有軸錯誤
        registers = [257] * 4  
        self.writeRegisters(0x0180, registers)  # reset系統錯誤(wireshark抓的 不知道為甚麼是4個)
        registers = [0] * 2 
        self.writeRegisters(0x0002, registers)  # wireshark抓的 不知道是甚麼東西
        
    #####################################################
    
    def prepareRobotForMotion(self, retryTimes: int = 5, retryDelay: float = 1) -> bool:
        """
        讓機器人自動進入準備狀態，包括reset軸錯誤，並開啟伺服
        
        參數:
        retryTimes: 重試次數，預設為5次
        retryDelay: 重試延遲時間，預設為1秒
        
        返回:
        bool: 如果機器人成功進入準備狀態則返回True，否則返回False
        """
        for _ in range(retryTimes):
            self.resetRobotError()
            self.AllAxisEnable()
            
            if self.isRobotReadyForMotion:
                print("機器人已準備運動")
                return True
            else:
                print(self.getRobotNotReadyReason())
                time.sleep(retryDelay)
        
        print("機器人無法進入準備狀態")
        return False
    ##################################################################
    def __monitorErrors(self):
        """
        定期檢查機器人是否有錯誤
        """
        while not self._stopThread.is_set():
            if self.isRobotError:
                self._stopThread.set()
                raise RobotErrorException (f"機器人發生錯誤，錯誤內容: {self.getRobotNotReadyReason()}")
            time.sleep(self.errorMonitorThreadSleepTime)
    
    def startMonitorErrors(self):
        """
        啟動錯誤檢查執行緒
        """
        self.errorMonitorThread.start()  # 啟動執行緒
        
    def stopMonitorErrors(self):
        """
        停止錯誤檢查執行緒
        """
        self._stopThread.set()
        self.errorMonitorThread.join()
    ##################################################################
    
    def writeRegister(self, address: int, value: int, unit: int = 2):
        """
        寫入單個寄存器並檢查錯誤的輔助方法。

        參數:
        address: 寄存器地址
        value: 要寫入的值
        unit: 單元標識符，預設為2

        返回:
        寫入操作的結果
        """
        result = self.modbusTCPClient.write_register(address, value, unit)
        if result.isError():
            raise RequestErrorException(f"寫入寄存器 {address} 失敗")
        return result

    def writeRegisters(self, address: int, values: list[int], unit: int = 2):
        """
        寫入多個寄存器並檢查錯誤的輔助方法。

        參數:
        address: 起始寄存器地址
        values: 要寫入的值列表
        unit: 單元標識符，預設為2

        返回:
        寫入操作的結果
        """
        result = self.modbusTCPClient.write_registers(address, values, unit)
        if result.isError():
            raise RequestErrorException(f"寫入寄存器 {address} 失敗")
        return result

    def readRegisters(self, address: int, count: int = 1) -> list[int] | int:
        """
        讀取寄存器並檢查錯誤的輔助方法。

        參數:
        address: 寄存器地址
        count: 讀取的寄存器數量

        返回:
        list[int]: 寄存器的值(當數量>1時)
        int: 寄存器的值(當數量=1時)
        """
        request = self.modbusTCPClient.read_holding_registers(address, count, 2)
        if request.isError():
            raise RequestErrorException(f"與modbus連接對象{self.modbusTCPClient.comm_params.host}:{self.modbusTCPClient.comm_params.port}無法通訊")
        return request.registers if count > 1 else request.registers[0]

    

    
