import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import time

from robot import Robot
from pymodbus.client import ModbusTcpClient
import robot
import utils

if __name__   == "__main__":
    
    parameters = utils.readListFromCsv("examples/datas/parameters.csv")
    
    host = parameters["host"]
    port = parameters["port"]
    modbusTCPClient = ModbusTcpClient(host= host,port=port)
    
    defaultSpeed = int(parameters["defaultSpeed"])
    defaultAcceleration = int(parameters["defaultAcceleration"])
    defaultDeceleration = int(parameters["defaultDeceleration"])
    
    
    robotDRV = Robot(modbusTCPClient,defaultSpeed=defaultSpeed,
                     defaultAcceleration=defaultAcceleration,
                     defaultDeceleration=defaultDeceleration)#可以在初始化的時候指定預設速度、加減速度
    #robotDRV.defaultSpeed = 100#也可以在初始化後再指定
    #robotDRV.defaultAcceleration = 80
    #robotDRV.defaultDeceleration = 80
    
    ret = robotDRV.prepareRobotForMotion()
    if ret == False:
        print("機器人無法進入準備狀態")
        exit()
    
    robotDRV.sendMotionCommand(
        robotCommand=robot.eRobotCommand.Robot_All_Joints_Homing_To_Origin)#測試回home功能
    while True:
        print(robotDRV.getTCPPose())
        if robotDRV.isRobotReachTargetPosition :
            break
        time.sleep(0.1)
        
    readyPosition = utils.readListFromCsv("examples/datas/parameters.csv")["readyPosition"]
    #home = [424.863, 0.328, 663.11, 178.333, -0.679, -111.784]

    robotDRV.sendMotionCommand(position=readyPosition,speed=100,acceleration=100,deceleration=100,#也可以在call函數的時候再指定速度
                               robotCommand=robot.eRobotCommand.Robot_Go_MovP)

    #send.Go_Position(modbusTCPClient,home,20)
    while True:
        print(robotDRV.getTCPPose())
        if robotDRV.isRobotReachTargetPosition :
            break
        time.sleep(0.1)
    
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