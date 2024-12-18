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
from realsense import realsense
import cv2
import glob

#定義全局變數 用以處理Tab切換xyz<->rxyz的問題
isTabbed=False
R_TRIG_tab = utils.R_TRIG()
robotCommand:eRobotCommand = None
stop_event = threading.Event()  # 使用 Event 來控制線程停止
img = None

def save_image(image_folder, image, namespace):
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)
    
    # 找到images資料夾中最大的號碼
    existing_images = glob.glob(os.path.join(image_folder, f'{namespace}_*.jpg'))
    if existing_images:
        latest_image = max(existing_images, key=os.path.getctime)
        latest_image_number = int(os.path.basename(latest_image).split('_')[-1].split('.')[0])
    else:
        latest_image_number = 0
    
    # 將圖像寫入到images資料夾中，命名是namespace_{i}.jpg
    image_path = os.path.join(image_folder, f'{namespace}_{latest_image_number + 1}.jpg')
    cv2.imwrite(image_path, image)
    
def sendMotionCommand(robotDRV:Robot, stop_event:threading.Event):
    while not stop_event.is_set():  # 檢查 Event 是否被設置
        if robotCommand is not None:
            robotDRV.sendMotionCommand(robotCommand=robotCommand)
        time.sleep(0.1)

def realsense_thread(stop_event:threading.Event):
    global img
    while not stop_event.is_set():
        img = realsense.Get_RGB_Frame()
        cv2.imshow("RGB",img)
        cv2.waitKey(1)

# 定義鍵盤按下事件
def on_press(key):
    global isTabbed,robotCommand,img#宣告有使用到全局變數
    print(f"{key} pressed")
    try:
        print(robotDRV.getTCPPose())
        if R_TRIG_tab(key == keyboard.Key.tab)  :  # 按tab 切換isTabbed
            isTabbed = not isTabbed 
            print (f"isTabbed is {isTabbed}")
        if key == keyboard.Key.f1:
            save_image("images_test",img,"img")
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
    threading.Thread(target=realsense_thread, args=(stop_event,)).start()
    
    # 啟動鍵盤監聽器，持續監聽鍵盤事件
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()