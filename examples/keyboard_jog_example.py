import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from pynput import keyboard
import threading
import time

from robot.classRobot import Robot
from robot.enumRobotCommand import eRobotCommand
from pymodbus.client import ModbusTcpClient
import utils

#定義全局變數 用以處理Tab切換xyz<->rxyz的問題
isTabbed=False
R_TRIG_tab = utils.R_TRIG()
robotCommand:eRobotCommand = None
stop_event = threading.Event()  # 使用 Event 來控制線程停止

def sendMotionCommand(robotDRV:Robot, stop_event:threading.Event):
    while not stop_event.is_set():  # 檢查 Event 是否被設置
        if robotCommand is not None:
            robotDRV.sendMotionCommand(robotCommand=robotCommand)
        time.sleep(0.1)

# 定義鍵盤按下事件
def on_press(key):
    global isTabbed,robotCommand#宣告有使用到全局變數
    print(f"{key} pressed")
    try:
        print(robotDRV.getTCPPose())
        if R_TRIG_tab(key == keyboard.Key.tab)  :  # 按tab 切換isTabbed
            isTabbed = not isTabbed 
            print (f"isTabbed is {isTabbed}")
        if not isTabbed :   
            if key == keyboard.Key.up:  # 按上箭頭，向-x方向移動
                robotCommand = eRobotCommand.Continue_JOG_X_Negative
            if key == keyboard.Key.down:  # 按下箭頭，向+x方向移動
                robotCommand = eRobotCommand.Continue_JOG_X_Positive
            if key == keyboard.Key.left:  # 按左箭頭，向-y方向移動
                robotCommand = eRobotCommand.Continue_JOG_Y_Negative
            if key == keyboard.Key.right:  # 按右箭頭，向+y方向移動
                robotCommand = eRobotCommand.Continue_JOG_Y_Positive
            if key == keyboard.Key.ctrl_l:  # 按Ctrl，向-z方向移動
                robotCommand = eRobotCommand.Continue_JOG_Z_Negative
            if key == keyboard.Key.shift_l:  # 按Shift，向+z方向移動
                robotCommand = eRobotCommand.Continue_JOG_Z_Positive
        else :
            if key == keyboard.Key.up:  # 按上箭頭，向-x方向移動
                robotCommand = eRobotCommand.Continue_JOG_RX_Negative
            if key == keyboard.Key.down:  # 按下箭頭，向+x方向移動
                robotCommand = eRobotCommand.Continue_JOG_RX_Positive
            if key == keyboard.Key.left:  # 按左箭頭，向-y方向移動
                robotCommand = eRobotCommand.Continue_JOG_RY_Negative
            if key == keyboard.Key.right:  # 按右箭頭，向+y方向移動
                robotCommand = eRobotCommand.Continue_JOG_RY_Positive
            if key == keyboard.Key.ctrl_l:  # 按Ctrl，向-z方向移動
                robotCommand = eRobotCommand.Continue_JOG_RZ_Negative
            if key == keyboard.Key.shift_l:  # 按Shift，向+z方向移動
                robotCommand = eRobotCommand.Continue_JOG_RZ_Positive

    except AttributeError:
        print(f"undefinded {key} has been pressed")

# 定義鍵盤釋放事件
def on_release(key):    
    print(f"{key} released")
    R_TRIG_tab(key == keyboard.Key.tab)
    global robotCommand
    robotCommand = eRobotCommand.Motion_Stop
    if key == keyboard.Key.esc:  # 按下 ESC 鍵退出
        stop_event.set()  # 設置 Event，停止線程
        return False


if __name__ == "__main__":
    
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
        
    threading.Thread(target=sendMotionCommand, args=(robotDRV, stop_event)).start()

    # 啟動鍵盤監聽器，持續監聽鍵盤事件
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()