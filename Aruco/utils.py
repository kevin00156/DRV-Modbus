import numpy as np
from scipy.spatial.transform import Rotation

def drawOrigin(rotationMatrix, translationVector, ax, scale = 1):
    """
    在 3D 空間中繪製原點座標系
    rotationMatrix: 旋轉矩陣
    translationVector: 平移向量
    ax: 3D 繪圖座標軸
    scale: 縮放比例
    """
    r0 = rotationMatrix[:, 0].reshape(3) * scale
    r1 = rotationMatrix[:, 1].reshape(3) * scale
    r2 = rotationMatrix[:, 2].reshape(3) * scale
    
    # 使用不同顏色繪製 X, Y, Z 軸
    ax.quiver(translationVector[0], translationVector[1], translationVector[2], r0[0], r0[1], r0[2], color='r')
    ax.quiver(translationVector[0], translationVector[1], translationVector[2], r1[0], r1[1], r1[2], color='g')
    ax.quiver(translationVector[0], translationVector[1], translationVector[2], r2[0], r2[1], r2[2], color='b')

def drawCamera(cameraMatrix, rotationMatrix, translationVector, camText, ax, focalLength=1):
    """
    在 3D 空間中繪製相機的坐標系
    cameraMatrix: 相機內部參數矩陣
    rotationMatrix: 旋轉矩陣
    translationVector: 平移向量
    camText: 相機標籤文字
    ax: 3D 繪圖座標軸
    focalLength: 焦距

    """
    ax.text(translationVector[0][0], translationVector[1][0], translationVector[2][0], camText) # 在相機位置標示文字

    # 繪製相機的 X, Y, Z 軸
    r0 = rotationMatrix[:, 0].reshape(3)
    r1 = rotationMatrix[:, 1].reshape(3)
    r2 = rotationMatrix[:, 2].reshape(3)
    ax.text(translationVector[0][0], translationVector[1][0], translationVector[2][0], camText)
    ax.quiver(translationVector[0], translationVector[1], translationVector[2], r0[0], r0[1], r0[2], color='r')
    ax.quiver(translationVector[0], translationVector[1], translationVector[2], r1[0], r1[1], r1[2], color='g')
    ax.quiver(translationVector[0], translationVector[1], translationVector[2], r2[0], r2[1], r2[2], color='b')

    # 計算相機視椎的四個角點
    vec = np.zeros(3)
    vec[0] = cameraMatrix[0][2] / cameraMatrix[0][0] * focalLength
    vec[1] = cameraMatrix[1][2] / cameraMatrix[1][1] * focalLength
    vec[2] = focalLength
    translationVectorT = translationVector.reshape(3)
    lt = (-vec[0]) * r0 + (-vec[1]) * r1 + vec[2] * r2 + translationVectorT    # 左上
    lb = (-vec[0]) * r0 + vec[1] * r1 + vec[2] * r2 + translationVectorT       # 左下
    rt = vec[0] * r0 + (-vec[1]) * r1 + vec[2] * r2 + translationVectorT       # 右上
    rb = vec[0] * r0 + vec[1] * r1 + vec[2] * r2 + translationVectorT          # 右下  

    # 繪製視椎的邊框
    ax.plot3D(xs=(translationVectorT[0], lt[0]),
              ys=(translationVectorT[1], lt[1]),
              zs=(translationVectorT[2], lt[2]), color='k')
    ax.plot3D(xs=(translationVectorT[0], rt[0]),
              ys=(translationVectorT[1], rt[1]),
              zs=(translationVectorT[2], rt[2]), color='k')
    ax.plot3D(xs=(translationVectorT[0], lb[0]),
              ys=(translationVectorT[1], lb[1]),
              zs=(translationVectorT[2], lb[2]), color='k')
    ax.plot3D(xs=(translationVectorT[0], rb[0]),
              ys=(translationVectorT[1], rb[1]),
              zs=(translationVectorT[2], rb[2]), color='k')

    ax.plot3D(xs=(lt[0], rt[0]),
              ys=(lt[1], rt[1]),
              zs=(lt[2], rt[2]), color='k')
    ax.plot3D(xs=(rt[0], rb[0]),
              ys=(rt[1], rb[1]),
              zs=(rt[2], rb[2]), color='k')
    ax.plot3D(xs=(rb[0], lb[0]),
              ys=(rb[1], lb[1]),
              zs=(rb[2], lb[2]), color='k')
    ax.plot3D(xs=(lb[0], lt[0]),
              ys=(lb[1], lt[1]),
              zs=(lb[2], lt[2]), color='k')

def combineRotationAndTranslationToHomogeneousMatrix(rotationMatrix, translationVector):
    """
    將旋轉矩陣和位移向量組合成 4x4 齊次變換矩陣
    rotationMatrix: 旋轉矩陣
    translationVector: 位移向量
    return: 4x4 齊次變換矩陣
    """
    transformationMatrix = np.hstack((rotationMatrix, translationVector)) # 將旋轉矩陣和位移向量水平拼接
    transformationMatrix = np.vstack((transformationMatrix, [0, 0, 0, 1])) # 將最後一行 [0, 0, 0, 1] 加入變換矩陣
    return transformationMatrix

def decomposeTransformationMatrix(transformationMatrix):
    """
    將 4x4 齊次變換矩陣轉換成旋轉矩陣和位移向量
    transformationMatrix: 4x4 齊次變換矩陣
    return: 旋轉矩陣, 位移向量
    """
    rotationAndTranslation = transformationMatrix[:3] # 提取旋轉和位移部分
    rotationMatrix = rotationAndTranslation[:, :3] # 提取旋轉矩陣
    translationVector = rotationAndTranslation[:, 3].reshape((-1, 1)) # 提取位移向量
    return rotationMatrix, translationVector

def rotationMatrixToQuaternion(rotationMatrix):
    """
    將旋轉矩陣轉換成四元數
    rotationMatrix: 旋轉矩陣
    return: 四元數
    """
    rotation = Rotation.from_matrix(rotationMatrix)
    return rotation.as_quat()

def quaternionToRotationMatrix(quaternion):
    """
    將四元數轉換成旋轉矩陣
    quaternion: 四元數
    return: 旋轉矩陣
    """
    rotation = Rotation.from_quat(quaternion) # 從四元數生成旋轉物件
    return rotation.as_matrix() # 返回旋轉矩陣

def rotationMatrixToRotationVector(rotationMatrix):
    """
    將旋轉矩陣轉換成旋轉向量
    rotationMatrix: 旋轉矩陣
    """
    rotation = Rotation.from_matrix(rotationMatrix) # 從旋轉矩陣生成旋轉物件
    return rotation.as_rotvec() # 返回旋轉向量

def rotationVectorToRotationMatrix(rotationVector):
    """
    將旋轉向量轉換成旋轉矩陣
    rotationVector: 旋轉向量
    """
    rotation = Rotation.from_rotvec(rotationVector) # 從旋轉向量生成旋轉物件
    return rotation.as_matrix() # 返回旋轉矩陣

def eulerAngleToRotationMatrix(eulerAngles):
    """
    將歐拉角轉換成旋轉矩陣
    eulerAngles: 歐拉角
    """
    rotation = Rotation.from_euler('xyz', eulerAngles, degrees=True) # 從歐拉角生成旋轉物件
    return rotation.as_matrix() # 返回旋轉矩陣

def techmanRobotFormatToTransformationMatrix(tmCoordinates):
    """
    將 TM(techman機器人) 座標格式轉換成 4x4 齊次變換矩陣
    techmanRobotCoordinates: 達明機器人的座標 (包括平移和歐拉角)
    """
    translationVector = tmCoordinates[:3] # 提取位移部分
    eulerAngles = tmCoordinates[3:] # 提取歐拉角部分
    rotationMatrix = Rotation.from_euler('xyz', eulerAngles, degrees=True).as_matrix() # 歐拉角轉旋轉矩陣
    translationVector = np.array(translationVector).reshape((-1, 1)) # 將平移向量轉換為適當形狀
    rotationAndTranslation = np.hstack((rotationMatrix, translationVector)) # 合併旋轉和位移
    transformationMatrix = np.vstack((rotationAndTranslation, [0, 0, 0, 1])) # 形成齊次變換矩陣
    return transformationMatrix

def drawAruco(ax, arucoLength):
    """
    在 3D 空間中繪製 ArUco 標記
    ax: 3D 繪圖座標軸, arucoLength: ArUco 標記邊長
    """
    # 繪製 ArUco 標記的四條邊
    ax.plot3D(xs=(arucoLength / 2, -arucoLength / 2),
                ys=(arucoLength / 2, arucoLength / 2),
                zs=(0, 0), color='k')
    ax.plot3D(xs=(-arucoLength / 2, -arucoLength / 2),
            ys=(arucoLength / 2, -arucoLength / 2),
            zs=(0, 0), color='k')
    ax.plot3D(xs=(-arucoLength / 2, arucoLength / 2),
            ys=(-arucoLength / 2, -arucoLength / 2),
            zs=(0, 0), color='k')
    ax.plot3D(xs=(arucoLength / 2, arucoLength / 2),
            ys=(-arucoLength / 2, arucoLength / 2),
            zs=(0, 0), color='k')

def tRxAdvence(transformationMatrix, rxOffset):
    """
    沿著 X 軸推進變換矩陣 T
    transformationMatrix: 齊次變換矩陣, rxOffset: 沿 X 軸的位移
    註：底下tRyAdvence與tRzAdvence邏輯完全相同，不再註解
    我猜這應該是學長一開始寫還不熟，才搞出三個功能相同但名稱不同的function
    """
    resultTransformationMatrix = transformationMatrix # 複製 T 避免修改原始矩陣
    rotationMatrix = resultTransformationMatrix[:3, :3] # 提取旋轉矩陣
    rotationMatrixZ = rotationMatrix[:, 2] # 提取 X 軸方向
    resultTransformationMatrix[:3, 3] += rotationMatrixZ * rxOffset # 沿 X 軸方向進行位移
    return resultTransformationMatrix

def tRyAdvence(transformationMatrix, ryOffset):
    """
    沿著 Y 軸推進變換矩陣 T
    transformationMatrix: 齊次變換矩陣
    ryOffset: 沿 Y 軸的位移
    """
    resultTransformationMatrix = transformationMatrix
    rotationMatrix = resultTransformationMatrix[:3, :3]
    rotationMatrixZ = rotationMatrix[:, 2]
    resultTransformationMatrix[:3, 3] += rotationMatrixZ * ryOffset
    return resultTransformationMatrix

def tRzAdvence(transformationMatrix, rzOffset):
    """
    沿著 Z 軸推進變換矩陣 T
    transformationMatrix: 齊次變換矩陣
    rzOffset: 沿 Z 軸的位移
    """
    resultTransformationMatrix = transformationMatrix.copy()
    rotationMatrix = resultTransformationMatrix[:3, :3]
    rotationMatrixZ = rotationMatrix[:, 2]
    resultTransformationMatrix[:3, 3] += rotationMatrixZ * rzOffset
    return resultTransformationMatrix


def rotationMatrix(x, y, z):
    """
    根據x,y,z歐拉角計算旋轉矩陣
    """
    c1 = np.cos(x * np.pi / 180)
    s1 = np.sin(x * np.pi / 180)
    c2 = np.cos(y * np.pi / 180)
    s2 = np.sin(y * np.pi / 180)
    c3 = np.cos(z * np.pi / 180)
    s3 = np.sin(z * np.pi / 180)
    matrix=np.array([[c2*c3, -c2*s3, s2],
                     [c1*s3+c3*s1*s2, c1*c3-s1*s2*s3, -c2*s1],
                     [s1*s3-c1*c3*s2, c3*s1+c1*s2*s3, c1*c2]])
    matrix[:, 0] = matrix[:, 0] / np.linalg.norm(matrix[:, 0])
    matrix[:, 1] = matrix[:, 1] / np.linalg.norm(matrix[:, 1])
    matrix[:, 2] = matrix[:, 2] / np.linalg.norm(matrix[:, 2])
    return matrix

def depthToPointCloud(cameraMatrix, depthImg, minDist = 0, maxDist = 2):
    """
    將深度圖轉換成點雲數據
    cameraMatrix: 相機內部參數矩陣
    depthImg: 深度圖
    minDist: 最小距離閾值
    maxDist: 最大距離閾值
    """
    cameraMatrixInv = np.linalg.inv(cameraMatrix) # 計算相機內部參數矩陣的逆矩陣
    pointCloud = [] # 用於存儲點雲的空列表
    #percent = 0

    # 遍歷深度圖中的每個像素
    for v in range(depthImg.shape[0]): # 行 (高度)
        for u in range(depthImg.shape[1]): # 列 (寬度)
            s = depthImg[v][u] / 1000 #z-distance(depth) in meter  # 將深度值從毫米轉換成米 (z 距離)

            # 檢查深度值是否在允許的範圍內
            if s <= minDist or s >= maxDist:
                continue

            # 創建該像素點的齊次座標 (u, v, 1)
            w = np.array([u, v, 1]).reshape(3, 1)

            # 使用內部參數矩陣逆變換和深度值計算該點的 3D 座標
            W = s * np.dot(cameraMatrixInv, w)

            # 將計算出的 3D 點加入點雲列表
            pointCloud.append(W)

        #顯示進度百分比用的，可以註解掉    
        percentTemp = int(v / depthImg.shape[0] * 100) + 1
        #if percentTemp != percent:
        #    percent = percentTemp
        #    print(percent, "%")
    pointCloud = np.array(pointCloud) # 將列表轉換為 NumPy 數組
    return pointCloud.reshape((len(pointCloud), 3)) # 將點雲數據轉換成 (N, 3) 的形狀