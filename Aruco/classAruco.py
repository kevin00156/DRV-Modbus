import numpy as np
import cv2
from Aruco.functions import *

class Aruco():
    """
    定義一個類來生成和操作 ArUco 標記
    """
    def __init__(self, arucoDict = cv2.aruco.DICT_5X5_100, id = 0, resolution = 300, arucoParams = cv2.aruco.DetectorParameters()):
        """
        初始化 ArUco 標記的參數
        arucoDict: ArUco 標記的字典類型(預設為DICT_5X5_100)
        id: ArUco 標記的 ID(預設為0)
        resolution: ArUco 標記的解析度(預設為300)
        arucoParams: ArUco 標記的參數(預設為cv2.aruco.DetectorParameters())
        """
        self._arucoDictionary = cv2.aruco.getPredefinedDictionary(arucoDict)
        self._id = id
        self._resolution = resolution
        self._tag = self.spawnAruco()
        self._arucoParams = arucoParams

    def spawnAruco(self):
        """
        生成一個指定 ID 的 ArUco 標記圖像(根據_id, resolution, arucoParams)
        """
        tag = np.zeros((self._resolution, self._resolution, 1), dtype="uint8")
        cv2.aruco.generateImageMarker(self._arucoDictionary, self._id, self._resolution, tag, 1)
        return tag

    def detectAruco(self, frame, cameraMatrix, distCoeffs, arucoLength, isDrawAruco=False):
        """
        偵測 ArUco 標記並估算其位姿
        frame: 輸入的影像
        cameraMatrix: 相機內部參數矩陣
        distCoeffs: 相機畸變係數
        arucoLength: ArUco 標記的長度(Meter)
        isDrawAruco: 是否在影像上繪製 ArUco 標記(預設為False)

        return:
        ret: 是否偵測到 ArUco 標記
        transformMatrixCamToArucoResult: 相機到 ArUco 的轉換矩陣
        transformMatrixArucoToCamResult: ArUco 到相機的轉換矩陣
        idResult: ArUco 標記的 ID
        cornerResult: ArUco 標記的角點
        """
        corners, ids, rejected = cv2.aruco.detectMarkers(frame, self._arucoDictionary, parameters=self._arucoParams)

        if len(corners) == 0:
            return False, [], [], [], []
        
        rotationVectors, translationVectors, markerPoints = cv2.aruco.estimatePoseSingleMarkers(corners, arucoLength, cameraMatrix, distCoeffs)

        transformMatrixCamToArucoResult = []
        transformMatrixArucoToCamResult = []
        idResult = []
        cornerResult = []

        for corner, id, translationVector, rotationVector in zip(corners, ids, translationVectors, rotationVectors):
            id = id[0]
            corner = corner[0]

            rotationVectorCamToAruco = cv2.Rodrigues(rotationVector[0])[0]
            translationVectorCamToAruco = translationVector[0].reshape(-1, 1)

            # 計算相機到 ArUco 的轉換矩陣
            translationVectorCamToAruco = combineRotationAndTranslationToHomogeneousMatrix
            (rotationVectorCamToAruco, translationVectorCamToAruco)
            
            # 計算 ArUco 到相機的轉換矩陣
            translationVectorArucoToCam = np.linalg.inv(translationVectorCamToAruco)

            # 將計算結果存入結果列表
            transformMatrixCamToArucoResult.append(translationVectorCamToAruco)
            transformMatrixArucoToCamResult.append(translationVectorArucoToCam)
            idResult.append(id)
            cornerResult.append(corner)
            
        # 如果指定要繪製 ArUco 標記，則將標記在影像上繪出來
        if isDrawAruco:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        # 返回偵測結果
        return True, transformMatrixCamToArucoResult, transformMatrixArucoToCamResult, idResult, cornerResult

    def cornersCenter(self, corners):
        """
        計算 ArUco 標記角點的中心點
        """ 
        return np.mean(corners, axis=0)
    def cornersCenter(self, corners):
        """
        計算 ArUco 標記角點的中心點
        """ 
        return np.mean(corners, axis=0)