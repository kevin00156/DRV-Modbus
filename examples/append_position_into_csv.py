import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from robot.classRobot import Robot
from pymodbus.client import ModbusTcpClient

import utils

appendDataName = "positionName"#這行記得改，或自己到csv檔案裡面改

if __name__ == "__main__":
    robotDRV = Robot(host="192.168.1.1", port=502)
    
    
    host = "192.168.1.1"
    port = 502
    modbusTCPClient = ModbusTcpClient(host= host,port=port)
    
    robotDRV = Robot(modbusTCPClient)
    
    ret = robotDRV.prepareRobotForMotion()
    if ret == False:
        print("機器人無法進入準備狀態")
        exit()
        
    position = robotDRV.getTCPPose()
    
    appendData = (appendDataName, list(position))

    utils.appendListToCsv(appendData, "examples/datas/positions.csv")