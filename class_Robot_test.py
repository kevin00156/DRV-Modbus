
from robot.Class_Robot import Robot
from pymodbus.client import ModbusTcpClient
from robot.enumRobotCommand import eRobotCommand

if __name__   == "__main__":
    
    host = "192.168.1.1"
    modbusTCPClient = ModbusTcpClient(host= host)
    
    
    robotDRV = Robot(modbusTCPClient)
    
    robotDRV.Send_Motion_Command(robotCommand=eRobotCommand.Robot_All_Joints_Homing_To_Origin)#測試回home功能

    while True:
        print(robotDRV.Get_TCP_Pose)
        if robotDRV.isRobotReachTargetPosition :
            break
    #這邊在測試branch的commit是否正常運作
