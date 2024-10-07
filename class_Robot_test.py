from robot.Class_Robot import Robot
from pymodbus.client import ModbusTcpClient
from robot.enumRobotCommand import eRobotCommand
import time
import drv_modbus.send as send

if __name__   == "__main__":
    
    host = "192.168.1.1"
    modbusTCPClient = ModbusTcpClient(host= host)
    
    
    robotDRV = Robot(modbusTCPClient)
    
    robotDRV.sendMotionCommand(
        robotCommand=eRobotCommand.Robot_All_Joints_Homing_To_Origin,
        speed=100,acceleration=100,deceleration=100)#測試回home功能

    while True:
        print(robotDRV.getTCPPose())
        if robotDRV.isRobotReachTargetPosition :
            break
    

    home = [424.863, 0.328, 663.11, 178.333, -0.679, -111.784]

    robotDRV.sendMotionCommand(home,speed=50,acceleration=100,deceleration=100,
                               robotCommand=eRobotCommand.Robot_Go_MovP)

    #send.Go_Position(modbusTCPClient,home,20)
    while True:
        print(robotDRV.getTCPPose())
        if robotDRV.isRobotReachTargetPosition :
            break
    
    robotDRV.suctionON()
    time.sleep(2)
    robotDRV.suctionOFF()
    time.sleep(2)
    robotDRV.setIO(int(0b10010101))#設定io(以2進制輸入)
    time.sleep(2)
    robotDRV.setIO(10,True)#設定特定bit
    time.sleep(2)
    robotDRV.setIO(10,False)#設定特定bit
    time.sleep(2)
    robotDRV.setIO(0)#設定所有bit為0

