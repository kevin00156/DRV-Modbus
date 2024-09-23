from pynput import keyboard
from drv_modbus import send
from drv_modbus import request
from pymodbus.client import ModbusTcpClient
import time
from functions.R_TRIG import R_TRIG

# 初始化 Modbus TCP 連接
host = "192.168.1.1"
port = 502
c = ModbusTcpClient(host=host, port=port)
if not c.connect():
    print(f"cannot connect to {host}:{port}")
    exit(1)
else:
    print(f"Connected to {host}:{port}")
# 讀取當前的手臂位姿
x, y, z, rx, ry, rz = request.Get_TCP_Pose(c)

#定義全局變數 用以處理Tab切換xyz<->rxyz的問題
isTabbed=False
R_TRIG_tab = R_TRIG()

# 定義鍵盤按下事件
def on_press(key):
    global isTabbed#宣告有使用到全局變數
    try:
        print(request.Get_TCP_Pose(c))
        if R_TRIG_tab(key == keyboard.Key.tab)  :  # 按tab 切換isTabbed
            isTabbed = not isTabbed 
            print (f"isTabbed is {isTabbed}")
        if not isTabbed :   
            if key == keyboard.Key.up:  # 按上箭頭，向-x方向移動
                send.Jog_Position(c, -1, 0, 0, 0, 0, 0)
            if key == keyboard.Key.down:  # 按下箭頭，向+x方向移動
                send.Jog_Position(c, 1, 0, 0, 0, 0, 0)
            if key == keyboard.Key.left:  # 按左箭頭，向-y方向移動
                send.Jog_Position(c, 0, -1, 0, 0, 0, 0)
            if key == keyboard.Key.right:  # 按右箭頭，向+y方向移動
                send.Jog_Position(c, 0, 1, 0, 0, 0, 0)
            if key == keyboard.Key.ctrl_l:  # 按Ctrl，向-z方向移動
                send.Jog_Position(c, 0, 0, -1, 0, 0, 0)
            if key == keyboard.Key.shift_l:  # 按Shift，向+z方向移動
                send.Jog_Position(c, 0, 0, 1, 0, 0, 0)
        else :
            if key == keyboard.Key.up:  # 按上箭頭，向-rx方向移動
                send.Jog_Position(c, 0, 0, 0, -1, 0, 0)
            if key == keyboard.Key.down:  # 按下箭頭，向+rx方向移動
                send.Jog_Position(c, 0, 0, 0, 1, 0, 0)
            if key == keyboard.Key.left:  # 按左箭頭，向-ry方向移動
                send.Jog_Position(c, 0, 0, 0, 0, -1, 0)
            if key == keyboard.Key.right:  # 按右箭頭，向+ry方向移動
                send.Jog_Position(c, 0, 0, 0, 0, 1, 0)
            if key == keyboard.Key.ctrl_l:  # 按Ctrl，向-rz方向移動
                send.Jog_Position(c, 0, 0, 0, 0, 0, -1)
            if key == keyboard.Key.shift_l:  # 按Shift，向+rz方向移動
                send.Jog_Position(c, 0, 0, 0, 0, 0, 1)

    except AttributeError:
        print(f"undefinded {key} has been pressed")

# 定義鍵盤釋放事件
def on_release(key):
    if key in [keyboard.Key.up, keyboard.Key.down, keyboard.Key.left, keyboard.Key.right, keyboard.Key.ctrl_l, keyboard.Key.shift_l]:
        send.Jog_Stop(c)
    if key == keyboard.Key.esc:  # 按下 ESC 鍵退出
        return False

# 啟動鍵盤監聽器，持續監聽鍵盤事件
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
