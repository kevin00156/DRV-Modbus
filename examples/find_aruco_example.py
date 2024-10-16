import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from landmark import aruco
from landmark import util
import numpy as np
import cv2
import matplotlib.pyplot as plt

'''
這是一個使用 RealSense 相機偵測 ArUco 標記的範例程式。
它會尋找指定Aruco標記集中所有的 ArUco 標記，並根據指定的Aruco標記的ID，以其座標建立相機的座標系。
'''


aruco_5x5_100_id_24 = aruco.Aruco(aruco.ARUCO_DICT().DICT_5X5_100, 2, 300)#這行請根據需要改用對應的aruco標記集

cap = cv2.VideoCapture(1)#請根據需要更改相機號碼，參照find_cameras.py
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # 設定相機解析度寬度為 1280
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # 設定相機解析度高度為 720
aruco_length = 0.053  # ArUco 標記的實際邊長（單位：米）

# 相機內參矩陣 K，定義相機的焦距和光軸中心點等信息
K=np.array(
    [[739.0986938476562,0.0,660.466777227186],
    [0.0,737.6295166015625,371.63861588193686],
    [0.0,0.0,1.0]])#相機內部參數，不用動

D=np.array([0.0,0.0,0.0,0.0,0.0,])#畸變函數，全部打0當作不畸變

# 定義工作區間，用於在 3D 圖中顯示座標系的範圍（x, y, z 軸的最大最小值）
Workspace = [-0.5, 0.5, -0.5, 0.5, -0.5, 0.5]

# 建立 3D 圖形窗口
fig = plt.figure()
ax = fig.add_subplot(projection='3d')

while True:
    # 每次迴圈時清空 3D 圖
    plt.cla()
    
    # 從相機中讀取一幀影像
    ret, frame = cap.read()
    
    # 使用 ArUco 偵測函數，來檢測影像中的 ArUco 標記
    # 返回值包括是否檢測成功 (ret)，相機到 ArUco 的轉換矩陣，ArUco 到相機的轉換矩陣，標記 ID 和角點坐標
    ret, T_cam_to_aruco_result, T_aruco_to_cam_result, id_result, corner_result = aruco.Detect_Aruco(
        frame, K, D, aruco_length, aruco_5x5_100_id_24.aruco_dict, aruco_5x5_100_id_24.aruco_params, True)
    
    if ret:  # 如果偵測成功
        for id, T in zip(id_result, T_aruco_to_cam_result):  # 迭代每個標記
            # 從轉換矩陣 T 中提取旋轉向量和位移向量
            R_aruco_to_cam, t_aruco_to_cam = util.T_to_R_and_t(T)
            
            # 格式化 ArUco 標記的座標並顯示
            cam_text = "X : {:.3f}, Y : {:.3f}, Z : {:.3f}".format(
                t_aruco_to_cam[0][0], t_aruco_to_cam[1][0], t_aruco_to_cam[2][0])
            
            # 如果這個標記的 ID 與我們定義的 ArUco ID 相同，則在 3D 圖形中繪製相機
            if id == aruco_5x5_100_id_24.id:
                util.Draw_Camera(K, R_aruco_to_cam, t_aruco_to_cam, cam_text, ax, f=0.08)
    
    # 在 3D 圖形中繪製 ArUco 標記
    util.Draw_Aruco(ax, aruco_length)
    
    # 設置 3D 坐標軸範圍
    ax.set_xlim3d(Workspace[0], Workspace[1])
    ax.set_ylim3d(Workspace[2], Workspace[3])
    ax.set_zlim3d(Workspace[4], Workspace[5])
    
    # 設置 3D 坐標軸標籤
    ax.set_xlabel('x')
    ax.set_ylabel('y') 
    ax.set_zlabel('z')
    
    # 更新 3D 圖形並立即顯示
    plt.show(block=False)
    plt.pause(0.001)
    
    # 顯示相機畫面
    cv2.imshow("s", frame)
    
    # 如果按下 'q' 鍵，退出迴圈
    if cv2.waitKey(1) == ord('q'):
        break