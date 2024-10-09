from pynput import keyboard
from pymodbus.client import ModbusTcpClient
from functions.R_TRIG import R_TRIG
from robot.classRobot import Robot
from robot.enumRobotCommand import eRobotCommand

# 初始化 Modbus TCP 連接
host = "192.168.1.1"
port = 502
c=ModbusTcpClient(host=host, port=port)
if not c.connect():
    print(f"cannot connect to {host}:{port}")
    exit(1)
else:
    print(f"Connected to {host}:{port}")
robotDRV = Robot(c)
# 讀取當前的手臂位姿
x, y, z, rx, ry, rz = robotDRV.getTCPPose()

#定義全局變數 用以處理Tab切換xyz<->rxyz的問題
isTabbed=False
R_TRIG_tab = R_TRIG()

# 定義鍵盤按下事件
def on_press(key):
    global isTabbed#宣告有使用到全局變數
    print(f"{key} pressed")
    try:
        print(robotDRV.getTCPPose())
        if R_TRIG_tab(key == keyboard.Key.tab)  :  # 按tab 切換isTabbed
            isTabbed = not isTabbed 
            print (f"isTabbed is {isTabbed}")
        if not isTabbed :   
            if key == keyboard.Key.up:  # 按上箭頭，向-x方向移動
                robotDRV.sendMotionCommand(robotCommand=eRobotCommand.Continue_JOG_X_Negative)
            if key == keyboard.Key.down:  # 按下箭頭，向+x方向移動
                robotDRV.sendMotionCommand(robotCommand=eRobotCommand.Continue_JOG_X_Positive)
            if key == keyboard.Key.left:  # 按左箭頭，向-y方向移動
                robotDRV.sendMotionCommand(robotCommand=eRobotCommand.Continue_JOG_Y_Negative)
            if key == keyboard.Key.right:  # 按右箭頭，向+y方向移動
                robotDRV.sendMotionCommand(robotCommand=eRobotCommand.Continue_JOG_Y_Positive)
            if key == keyboard.Key.ctrl_l:  # 按Ctrl，向-z方向移動
                robotDRV.sendMotionCommand(robotCommand=eRobotCommand.Continue_JOG_Z_Negative)
            if key == keyboard.Key.shift_l:  # 按Shift，向+z方向移動
                robotDRV.sendMotionCommand(robotCommand=eRobotCommand.Continue_JOG_Z_Positive)
        else :
            if key == keyboard.Key.up:  # 按上箭頭，向-x方向移動
                robotDRV.sendMotionCommand(robotCommand=eRobotCommand.Continue_JOG_RX_Negative)
            if key == keyboard.Key.down:  # 按下箭頭，向+x方向移動
                robotDRV.sendMotionCommand(robotCommand=eRobotCommand.Continue_JOG_RX_Positive)
            if key == keyboard.Key.left:  # 按左箭頭，向-y方向移動
                robotDRV.sendMotionCommand(robotCommand=eRobotCommand.Continue_JOG_RY_Negative)
            if key == keyboard.Key.right:  # 按右箭頭，向+y方向移動
                robotDRV.sendMotionCommand(robotCommand=eRobotCommand.Continue_JOG_RY_Positive)
            if key == keyboard.Key.ctrl_l:  # 按Ctrl，向-z方向移動
                robotDRV.sendMotionCommand(robotCommand=eRobotCommand.Continue_JOG_RZ_Negative)
            if key == keyboard.Key.shift_l:  # 按Shift，向+z方向移動
                robotDRV.sendMotionCommand(robotCommand=eRobotCommand.Continue_JOG_RZ_Positive)

    except AttributeError:
        print(f"undefinded {key} has been pressed")

# 定義鍵盤釋放事件
def on_release(key):    
    print(f"{key} released")
    R_TRIG_tab(key == keyboard.Key.tab)
    robotDRV.motionStop()
    if key == keyboard.Key.esc:  # 按下 ESC 鍵退出
        return False

# 啟動鍵盤監聽器，持續監聽鍵盤事件
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
