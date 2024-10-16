import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from drv_modbus import send
from drv_modbus import request
from landmark import aruco
from realsense import realsense
from pymodbus.client import ModbusTcpClient
import numpy as np
import cv2
import time

#############################

# 定義不同顏色物體的 HSV 範圍
yellow_brick_lower_hsv = np.array([20, 20, 200])   # 黃磚下限 HSV
yellow_brick_upper_hsv = np.array([50, 255, 255])  # 黃磚上限 HSV
silver_plane_lower_hsv = np.array([20, 5, 50])     # 銀平面下限 HSV
silver_plane_upper_hsv = np.array([255, 255, 255]) # 銀平面上限 HSV
copper_brick_lower_hsv = np.array([10, 100, 50])   # 銅磚下限 HSV
copper_brick_upper_hsv = np.array([50, 200, 255])  # 銅磚上限 HSV
        
# 初始化 ArUco 標記的類型與參數
aruco_5x5_100_id = aruco.Aruco(aruco.ARUCO_DICT().DICT_5X5_100, 1, 200)# ArUco 標記類型為 5x5，ID 為 1，解析度為 200
aruco_length = 0.0525# ArUco 標記的實際物理長度，單位為米

# 定義物體所在區域的起點和終點
# 這兩個點用於表示機械手臂操作的工作區域
# o_point 是區域的起點，e_point 是區域的終點
#x : 388.442, y : -73.33200000000001, z : 325.693, rx: 179.987, ry: -0.004, rz: -106.121 id 1 tcp
#x : 637.4350000000001, y : 221.607, z : 322.593, rx: 179.987, ry: -0.004, rz: -106.121 id 4 tcp
o_point = (-73.332, 388.442)
e_point = (221.607, 637.435)
# 定義物體的 Z 軸高度，用於定位吸附點的高度
z_height = 319.796

# 計算工作區域的寬度和高度，根據起點和終點計算
real_width = e_point[0] - o_point[0]
real_height = e_point[1] - o_point[1]

# 取得 RealSense 相機的內參數 K，用於影像校正與轉換
K = realsense.Get_Color_K()
# 相機畸變參數 D，這裡設定為無畸變
D = np.array([0.0,0.0,0.0,0.0,0.0,])

# 初始化 Modbus TCP 連接，用於控制機械手臂
c = ModbusTcpClient(host="192.168.1.1", port=502)
c.connect()

# 定義機械手臂的 home 點與放置點的位姿
# home: 機械手臂的初始位置，表示手臂在空間中的預設姿態
# drop: 機械手臂移動物體後，物體要放置的位置
#home = [353.208, -48.09, 680.0, 179.987, -0.004, -106.121] #old home
home = [379.870, -2.034, 680.0, 179.987, -0.004, -106.121]
drop =[479.442, 385.366, 521.66, 179.987, -0.004, -106.121]
#############################


# 用於定義目標區域的函數
def AOI(frame, lower_hsv = np.array([20, 20, 200]), upper_hsv = np.array([50, 255, 255]), min_area = 300, crop_size = 40):
     # 剪裁影像
    crop_frame = frame[crop_size:-crop_size, crop_size:-crop_size]              # 剪裁掉影像的邊界部分，避免邊界影像的干擾
    blur = cv2.GaussianBlur(crop_frame, (3, 3), cv2.BORDER_DEFAULT)             # 使用高斯模糊來平滑影像，降低雜訊
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)                                 # 將影像從 BGR 色彩空間轉換為 HSV 色彩空間，用於進行顏色篩選
    dst = cv2.inRange(hsv, lower_hsv,  upper_hsv)                               # 根據設定的 HSV 範圍過濾影像，生成二值影像，範圍內的部分為白色，其餘部分為黑色
    contours, _ = cv2.findContours(dst, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE) # 使用輪廓檢測來找到符合條件的區域
    AOI_points = []                                                             # 儲存檢測到的目標區域的中心點

    # 找出符合條件的輪廓
    for c in contours:
        area = cv2.contourArea(c)
        # 只保留大於指定最小面積的輪廓，過濾掉小區域
        if area < min_area:
            continue

        # 計算輪廓的重心（中心點）
        M = cv2.moments(c)
        if M['m00'] != 0:
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            # 把計算出的重心加上剪裁的邊界尺寸，得到原圖中的正確坐標
            AOI_points.append((cx + crop_size, cy + crop_size))
            # 在原影像上畫出輪廓和重心點，用於檢視結果
            cv2.drawContours(crop_frame,contours,-1,(0,0,255),1)  
            cv2.circle(crop_frame, (cx, cy), 3, (255, 255, 0), -1)
            
    # 顯示結果
    cv2.imshow("dst", dst)
    #cv2.imshow("crop_frame", crop_frame)
    #cv2.waitKey(1)

    # 返回檢測到的目標區域的中心點
    return AOI_points

# 將 AOI 中的像素坐標轉換為真實世界坐標
# 這裡使用的是簡單的平移計算方法
def AOIcoor_2_Realcoor(AOI_points, o_point):
    real_points = []
    # 遍歷所有 AOI 檢測到的點，並計算它們在真實世界中的對應位置
    for ap in AOI_points:
        real_points.append((ap[1] + o_point[1], ap[0] + o_point[0]))
    return real_points

# 定義 Warp 函數，使用透視變換將影像進行變形
# c_center_list 是 ArUco 標記的中心點，用於校正影像
def Warp(frame, c_center_list, width, height):
    # 定義四個角點的映射關係，將其變形為矩形
    p1 = np.float32(c_center_list)
    p2 = np.float32([[0,0],[width,0],[0,height],[width,height]])

    # 計算透視變換矩陣
    m = cv2.getPerspectiveTransform(p1,p2)

    # 應用透視變換，將影像變形
    output = cv2.warpPerspective(frame, m, (width, height))
    return output, m

# 使用 RealSense 相機來檢測吸盤目標區域
def Find_Suction_Object(lower_hsv, upper_hsv):
    # 獲取 RealSense 相機的 RGB 影像
    frame = realsense.Get_RGB_Frame()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # 轉換顏色格式

    # 檢測 ArUco 標記，確定相機到 ArUco 的位置
    ret, T_cam_to_aruco_result, T_aruco_to_cam_result, id_result, corner_result = aruco.Detect_Aruco(
                                                                                frame, 
                                                                                K, 
                                                                                D, 
                                                                                aruco_length, 
                                                                                aruco_5x5_100_id.aruco_dict, 
                                                                                aruco_5x5_100_id.aruco_params)
    
    # 如果檢測到 4 個 ArUco 標記，則進行下一步
    if len(id_result) == 4:
        # 初始化 4 個 ArUco 標記的中心點
        c_center_list = [(0, 0), (0, 0), (0, 0), (0, 0)]
        # 遍歷檢測到的標記，計算中心點位置
        for id, c in zip(id_result, corner_result):
            c_center = aruco.Corners_Center(c)
            c_center = (int(c_center[0]), int(c_center[1]))
            c_center_list[id - 1] = c_center
        #cv2.line(frame, c_center_list[0], c_center_list[1], (0, 0, 255), 2)
        #cv2.line(frame, c_center_list[1], c_center_list[3], (0, 0, 255), 2)
        #cv2.line(frame, c_center_list[2], c_center_list[0], (0, 0, 255), 2)
        #cv2.line(frame, c_center_list[3], c_center_list[2], (0, 0, 255), 2)
        
        # 使用透視變換來校正影像
        output, m = Warp(frame, c_center_list, int(real_width), int(real_height))
        # 檢測影像中的吸盤目標區域
        AOI_points = AOI(output, lower_hsv, upper_hsv)
        # 將影像中的坐標轉換為真實世界中的坐標
        real_points = AOIcoor_2_Realcoor(AOI_points, o_point)
        
        return output, real_points     
    return [], []

# 執行吸盤的動作，根據檢測到的目標區域，移動機械手臂並進行吸附
def Suction_Behave(real_points):
    if len(real_points) > 0:
        # 移動到吸附點的上方，然後下降進行吸附
        send.Go_Position(c, real_points[0][0], real_points[0][1], home[2], home[3], home[4], home[5],speed= 50)
        send.Go_Position(c, real_points[0][0], real_points[0][1], z_height, home[3], home[4], home[5],speed= 50)
        send.Suction_ON(c)
        send.Go_Position(c, real_points[0][0], real_points[0][1], home[2], home[3], home[4], home[5],speed= 50)

        # 移動到放置點，並釋放物品
        send.Go_Position(c, drop[0], drop[1], drop[2], home[3], home[4], home[5],speed= 50)
        send.Go_Position(c, drop[0], drop[1], z_height, home[3], home[4], home[5],speed= 50)
        send.Suction_OFF(c)
        send.Go_Position(c, drop[0], drop[1], drop[2], home[3], home[4], home[5],speed= 50)

        # 返回 home 點
        send.Go_Position(c, home[0], home[1], home[2], home[3], home[4], home[5],speed= 50)

def main():
    """
    主函數負責控制機械手臂的運行邏輯。
    首先將機械手臂移動到預設的 home 點，然後持續檢測目標物並執行吸附動作。
    """
    # 初始化機械手臂到 home 點
    # home 點是初始位置，保證手臂從固定位置開始執行任務
    send.Go_Position(c,home, block=True)
    # 讀取 RealSense 相機的初始畫面
    # 此處使用 50 次讀取來初始化相機，以避免相機啟動初期可能的延遲或不穩定
    for i in range(50):
        frame = realsense.Get_RGB_Frame()

    # 持續檢測目標區域，並執行吸附任務
    real_points = []
    while len(real_points) == 0:#直到找到目標點之前
    #while True:
        # 使用指定的 HSV 範圍來檢測銀色平面的目標區域，直到找到目標
        output, real_points = Find_Suction_Object(silver_plane_lower_hsv, silver_plane_upper_hsv)
        frame = realsense.Get_RGB_Frame()
        cv2.imshow("frame", frame)
        cv2.waitKey(1)
    #找到目標點後，show出圖像
    cv2.imshow("output", output)
    cv2.waitKey(1)
    #印出目標點的位置
    print(real_points)
    #執行吸取動作
    Suction_Behave(real_points)
    print("Job done!!!")


# 程式入口，主程式將執行三次 main 函數來測試多次吸附動作
if __name__ == "__main__":
    for i in range(3):
        main()
    