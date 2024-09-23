import numpy as np
import cv2
from landmark import util

# 定義一個類來封裝 OpenCV 提供的各種 ArUco 字典
class ARUCO_DICT():
    def __init__(self):
        # OpenCV 支援的多種不同大小的 ArUco 標記字典，這些字典定義了不同類型的標記
        self.DICT_4X4_50 = cv2.aruco.DICT_4X4_50
        self.DICT_4X4_100 = cv2.aruco.DICT_4X4_100
        self.DICT_4X4_250 = cv2.aruco.DICT_4X4_250
        self.DICT_4X4_1000 = cv2.aruco.DICT_4X4_1000
        self.DICT_5X5_50 = cv2.aruco.DICT_5X5_50
        self.DICT_5X5_100 = cv2.aruco.DICT_5X5_100
        self.DICT_5X5_250 = cv2.aruco.DICT_5X5_250
        self.DICT_5X5_1000 = cv2.aruco.DICT_5X5_1000
        self.DICT_6X6_50 = cv2.aruco.DICT_6X6_50
        self.DICT_6X6_100 = cv2.aruco.DICT_6X6_100
        self.DICT_6X6_250 = cv2.aruco.DICT_6X6_250
        self.DICT_6X6_1000 = cv2.aruco.DICT_6X6_1000
        self.DICT_7X7_50 = cv2.aruco.DICT_7X7_50
        self.DICT_7X7_100 = cv2.aruco.DICT_7X7_100
        self.DICT_7X7_250 = cv2.aruco.DICT_7X7_250
        self.DICT_7X7_1000 = cv2.aruco.DICT_7X7_1000

        # 原始 ArUco 字典
        self.DICT_ARUCO_ORIGINAL = cv2.aruco.DICT_ARUCO_ORIGINAL

        # 支援 AprilTag 的標記字典
        self.DICT_APRILTAG_16h5 = cv2.aruco.DICT_APRILTAG_16h5
        self.DICT_APRILTAG_25h9 = cv2.aruco.DICT_APRILTAG_25h9
        self.DICT_APRILTAG_36h10 = cv2.aruco.DICT_APRILTAG_36h10
        self.DICT_APRILTAG_36h11 = cv2.aruco.DICT_APRILTAG_36h11

# 定義一個類來生成和操作 ArUco 標記
class Aruco():
    def __init__(self, aruco_dict, id, resolution = 300, aruco_params = None):
        # 使用 OpenCV 的方法來選擇指定的 ArUco 字典
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(aruco_dict)
        self.id = id # 標記的 ID
        self.resolution = resolution  # 標記影像的解析度
        self.tag = self.Spawn_Aruco()  # 生成 ArUco 標記

        # 如果沒有指定偵測參數，則使用 OpenCV 預設的 DetectorParameters
        if aruco_params == None:
            self.aruco_params = cv2.aruco.DetectorParameters()
        else:
            self.aruco_params = aruco_params

    # 生成一個指定 ID 的 ArUco 標記圖像
    def Spawn_Aruco(self):
        # 建立一個黑色的影像作為標記圖像的基礎
        tag = np.zeros((self.resolution, self.resolution, 1), dtype="uint8")
        # 使用 OpenCV 的方法在這個影像上畫出指定 ID 的 ArUco 標記
        cv2.aruco.generateImageMarker(self.aruco_dict, self.id, self.resolution, tag, 1)
        return tag

# 偵測 ArUco 標記並估算其位姿
def Detect_Aruco(frame, K, D, aruco_length, aruco_dict, aruco_params, is_draw_aruco = False, is_millimeter = False):
    # 使用 OpenCV 偵測影像中的 ArUco 標記
    corners, ids, rejected = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=aruco_params)

    # 如果沒有偵測到任何標記，返回失敗訊息
    if len(corners) == 0:
        return False, [], [], [], []
    
    # 估算標記的姿態，返回旋轉向量（rvec）和位移向量（tvec）
    rvec, tvec, markerPoints = cv2.aruco.estimatePoseSingleMarkers(corners, aruco_length, K, D)

    T_cam_to_aruco_result = [] # 相機到 ArUco 的轉換矩陣
    T_aruco_to_cam_result = [] # ArUco 到相機的轉換矩陣
    id_result = [] # 偵測到的標記 ID
    corner_result = [] # 偵測到的標記角點

    # 迭代每個偵測到的標記，進行處理
    for c, id, t, r in zip(corners, ids, tvec, rvec):
        #cv2.drawFrameAxes (frame, K, D, r, t, 0.08)
        id = id[0] # 取得標記的 ID
        c = c[0] # 取得標記的角點坐標

        # 將旋轉向量轉換為旋轉矩陣
        R_cam_to_aruco = cv2.Rodrigues(r[0])[0]
        t_cam_to_aruco = t[0].reshape(-1, 1)

        # 如果選擇了毫米單位，則將位移轉換為毫米
        if is_millimeter:
            t_cam_to_aruco *= 1000

        # 計算相機到 ArUco 的轉換矩陣
        T_cam_to_aruco = util.R_and_t_to_T(R_cam_to_aruco, t_cam_to_aruco)
        # 計算 ArUco 到相機的轉換矩陣
        T_aruco_to_cam = np.linalg.inv(T_cam_to_aruco)

        # 將計算結果存入結果列表
        T_cam_to_aruco_result.append(T_cam_to_aruco)
        T_aruco_to_cam_result.append(T_aruco_to_cam)
        id_result.append(id)
        corner_result.append(c)
        
    # 如果指定要繪製 ArUco 標記，則將標記在影像上繪出來
    if is_draw_aruco:
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)
    # 返回偵測結果
    return True, T_cam_to_aruco_result, T_aruco_to_cam_result, id_result, corner_result

# 計算 ArUco 標記角點的中心點
def Corners_Center(corners):
    return np.mean(corners, axis=0)
        

        