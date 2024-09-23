from landmark import aruco
from landmark import util
import numpy as np
import cv2
import matplotlib.pyplot as plt

'''
這是用以啟動realsense，尋找畫面中指定號碼的aruco 並由aruco座標建立相機坐標系
'''


aruco_5x5_100_id_24 = aruco.Aruco(aruco.ARUCO_DICT().DICT_6X6_50, 2, 300)#這行請根據需要改用對應的aruco標記集

cap = cv2.VideoCapture(0)#請根據需要更改相機號碼，參照find_cameras.py
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
aruco_length = 0.08

K=np.array([[739.0986938476562,0.0,660.466777227186], [0.0,737.6295166015625,371.63861588193686], [0.0,0.0,1.0]])
D=np.array([0.0,0.0,0.0,0.0,0.0,])

Workspace = [-0.5, 0.5, -0.5, 0.5, -0.5, 0.5]
fig = plt.figure()
ax = fig.add_subplot(projection='3d')

while True:
    plt.cla()
    ret, frame = cap.read()
    ret, T_cam_to_aruco_result, T_aruco_to_cam_result, id_result, corner_result = aruco.Detect_Aruco(frame, K, D, aruco_length, aruco_5x5_100_id_24.aruco_dict, aruco_5x5_100_id_24.aruco_params, True)
    if ret:
        for id, T in zip(id_result, T_aruco_to_cam_result):
            R_aruco_to_cam, t_aruco_to_cam = util.T_to_R_and_t(T)
            cam_text = "X : {:.3f}, Y : {:.3f}, Z : {:.3f}".format(t_aruco_to_cam[0][0], t_aruco_to_cam[1][0], t_aruco_to_cam[2][0])
            if id == aruco_5x5_100_id_24.id:
                util.Draw_Camera(K, R_aruco_to_cam, t_aruco_to_cam, cam_text, ax, f=0.08)
    
    util.Draw_Aruco(ax, aruco_length)
    ax.set_xlim3d(Workspace[0], Workspace[1])
    ax.set_ylim3d(Workspace[2], Workspace[3])
    ax.set_zlim3d(Workspace[4], Workspace[5])
    ax.set_xlabel('x')
    ax.set_ylabel('y') 
    ax.set_zlabel('z')
    plt.show(block=False)
    plt.pause(0.001)
    cv2.imshow("s", frame)
    if cv2.waitKey(1) == ord('q'):
        break