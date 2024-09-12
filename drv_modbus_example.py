from drv_modbus import send
from drv_modbus import request
from pymodbus.client import ModbusTcpClient
import time


if __name__ == "__main__":
    # 建立modbus客戶端並連接到指定IP的設備
    c = ModbusTcpClient(host="192.168.1.1", port=502)
    c.connect()
    print ("Connected to arm {c.address}:{port}")

    # 定義機械手臂的home點的姿態 (x, y, z, rx, ry, rz)
    home = [408.285, 0.0, 680.0120000000001, 178.969, -0.241, -103.145]

    # 移動到 home 姿態，且不等待完成
    send.Go_Position(c, home, block=False)
    print ("Go_Position send!")

    # 持續讀取和打印機械手臂的當前位姿，直到程式終止
    while True:
        x, y, z, rx, ry, rz = request.Get_TCP_Pose(c)

        print(f"x: {x}, y: {y}, z: {z}, rx: {rx}, ry: {ry}, rz: {rz}")

        # 每隔0.2秒打印一次手臂位置
        time.sleep(0.2)

    # 程式結束，關閉 modbus 連接
    c.close()
