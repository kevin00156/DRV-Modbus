
import time

from drv_modbus import send
from drv_modbus import request
from pymodbus.client import ModbusTcpClient

import utils

if __name__ == "__main__":
    # 建立modbus客戶端並連接到指定IP的設備
    host = "192.168.1.1"
    port = 502
    c = ModbusTcpClient(host=host, port=port)

    
    if not c.connect():
        print(f"cannot connect to {host}:{port}")
        exit(1)
    else:
        print(f"Connected to {host}:{port}")

    # 定義機械手臂的home點的姿態 (x, y, z, rx, ry, rz)
    # 可以直接定義一個list 如[424.863, 0.328, 663.11, 178.333, -0.679, -111.784]，也可以像我這樣從csv讀取
    home = utils.readPositionsFromCsv("examples/datas/positions.csv")["home"]
    #home = [424.863, 0.328, 663.11, 178.333, -0.679, -111.784]
    
    # 移動到 home 姿態，且不等待完成
    send.Go_Position(c, home, block=False)
    print ("Go_Position send!")

    # 持續讀取和打印機械手臂的當前位姿，直到程式終止
    while True:
        x, y, z, rx, ry, rz = request.Get_TCP_Pose(c)

        print(f"x: {x}, y: {y}, z: {z}, rx: {rx}, ry: {ry}, rz: {rz}")

        if request.isRobotReachTargetPosition(c):#檢查位置是否到達
            print ("position arrived!")
            break
        # 每隔0.2秒打印一次手臂位置
        time.sleep(0.2)
    # 程式結束，關閉 modbus 連接
    c.close()
