import numpy as np
from scipy.spatial.transform import Rotation
import warnings
from deprecated import deprecated
warnings.warn(f"此庫{__name__} 已被棄用,請使用Aruco.functions", DeprecationWarning, stacklevel=2)

# 在 3D 空間中繪製原點座標系
# R: 旋轉矩陣, t: 平移向量, ax: 3D 繪圖座標軸, scale: 縮放比例
@deprecated(reason="此函數已被棄用，請使用Aruco.functions.Draw_Origin")
def Draw_Origin(R, t, ax, scale = 1):
    r0 = R[:, 0].reshape(3) * scale
    r1 = R[:, 1].reshape(3) * scale
    r2 = R[:, 2].reshape(3) * scale
    
    # 使用不同顏色繪製 X, Y, Z 軸
    ax.quiver(t[0], t[1], t[2], r0[0], r0[1], r0[2], color='r')
    ax.quiver(t[0], t[1], t[2], r1[0], r1[1], r1[2], color='g')
    ax.quiver(t[0], t[1], t[2], r2[0], r2[1], r2[2], color='b')

# 繪製相機的坐標系
# K: 相機內部參數矩陣, R: 旋轉矩陣, t: 平移向量, cam_text: 相機標籤文字, ax: 3D 繪圖座標軸, f: 焦距
def Draw_Camera(K, R, t, cam_text, ax, f=1):
    ax.text(t[0][0], t[1][0], t[2][0], cam_text) # 在相機位置標示文字

    # 繪製相機的 X, Y, Z 軸
    r0 = R[:, 0].reshape(3)
    r1 = R[:, 1].reshape(3)
    r2 = R[:, 2].reshape(3)
    ax.text(t[0][0], t[1][0], t[2][0], cam_text)
    ax.quiver(t[0], t[1], t[2], r0[0], r0[1], r0[2], color='r')
    ax.quiver(t[0], t[1], t[2], r1[0], r1[1], r1[2], color='g')
    ax.quiver(t[0], t[1], t[2], r2[0], r2[1], r2[2], color='b')

    # 計算相機視椎的四個角點
    vec = np.zeros(3)
    vec[0] = K[0][2] / K[0][0] * f
    vec[1] = K[1][2] / K[1][1] * f
    vec[2] = f
    t_T = t.reshape(3)
    lt = (-vec[0]) * r0 + (-vec[1]) * r1 + vec[2] * r2 + t_T    # 左上
    lb = (-vec[0]) * r0 + vec[1] * r1 + vec[2] * r2 + t_T       # 左下
    rt = vec[0] * r0 + (-vec[1]) * r1 + vec[2] * r2 + t_T       # 右上
    rb = vec[0] * r0 + vec[1] * r1 + vec[2] * r2 + t_T          # 右下  

    # 繪製視椎的邊框
    ax.plot3D(xs=(t_T[0], lt[0]),
              ys=(t_T[1], lt[1]),
              zs=(t_T[2], lt[2]), color='k')
    ax.plot3D(xs=(t_T[0], rt[0]),
              ys=(t_T[1], rt[1]),
              zs=(t_T[2], rt[2]), color='k')
    ax.plot3D(xs=(t_T[0], lb[0]),
              ys=(t_T[1], lb[1]),
              zs=(t_T[2], lb[2]), color='k')
    ax.plot3D(xs=(t_T[0], rb[0]),
              ys=(t_T[1], rb[1]),
              zs=(t_T[2], rb[2]), color='k')

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

# 將旋轉矩陣和位移向量組合成 4x4 齊次變換矩陣
# R: 旋轉矩陣, t: 位移向量
def R_and_t_to_T(R, t):
    T = np.hstack((R, t)) # 將旋轉矩陣和位移向量水平拼接
    T = np.vstack((T, [0, 0, 0, 1])) # 將最後一行 [0, 0, 0, 1] 加入變換矩陣
    return T

# 將 4x4 齊次變換矩陣轉換成旋轉矩陣和位移向量
# T: 4x4 齊次變換矩陣
def T_to_R_and_t(T):
    Rt = T[:3] # 提取旋轉和位移部分
    R = Rt[:, :3] # 提取旋轉矩陣
    t = Rt[:, 3].reshape((-1, 1)) # 提取位移向量
    return R, t

# 將旋轉矩陣轉換成四元數
# R: 旋轉矩陣
def Rotation_Matrix_to_Quaternion(R):
    r = Rotation.from_matrix(R)
    return r.as_quat()

# 將四元數轉換成旋轉矩陣
# q: 四元數
def Quaternion_to_Rotation_Matrix(q):
    r = Rotation.from_quat(q) # 從四元數生成旋轉物件
    return r.as_matrix() # 返回旋轉矩陣

# 將旋轉矩陣轉換成旋轉向量
# R: 旋轉矩陣
def Rotation_Matrix_to_Rotation_Vector(R):
    r = Rotation.from_matrix(R) # 從旋轉矩陣生成旋轉物件
    return r.as_rotvec() # 返回旋轉向量

# 將旋轉向量轉換成旋轉矩陣
# v: 旋轉向量
def Rotation_Vector_to_Rotation_Matrix(v):
    r = Rotation.from_rotvec(v) # 從旋轉向量生成旋轉物件
    return r.as_matrix() # 返回旋轉矩陣

# 將歐拉角轉換成旋轉矩陣
# e: 歐拉角
def Euler_Angle_to_Rotation_Matrix(e):
    r = Rotation.from_euler('xyz', e, degrees=True) # 從歐拉角生成旋轉物件
    return r.as_matrix() # 返回旋轉矩陣

# 將 TM 座標格式轉換成 4x4 齊次變換矩陣
# tm: 達明機器人的座標 (包括平移和歐拉角)
def TM_Format_to_T(tm):
    t = tm[:3] # 提取位移部分
    e = tm[3:] # 提取歐拉角部分
    R = Rotation.from_euler('xyz', e, degrees=True).as_matrix() # 歐拉角轉旋轉矩陣
    t = np.array(t).reshape((-1, 1)) # 將平移向量轉換為適當形狀
    Rt = np.hstack((R, t)) # 合併旋轉和位移
    T = np.vstack((Rt, [0, 0, 0, 1])) # 形成齊次變換矩陣
    return T

# 在 3D 空間中繪製 ArUco 標記
# ax: 3D 繪圖座標軸, aruco_length: ArUco 標記邊長
def Draw_Aruco(ax, aruco_length):
    # 繪製 ArUco 標記的四條邊
    ax.plot3D(xs=(aruco_length / 2, -aruco_length / 2),
                ys=(aruco_length / 2, aruco_length / 2),
                zs=(0, 0), color='k')
    ax.plot3D(xs=(-aruco_length / 2, -aruco_length / 2),
            ys=(aruco_length / 2, -aruco_length / 2),
            zs=(0, 0), color='k')
    ax.plot3D(xs=(-aruco_length / 2, aruco_length / 2),
            ys=(-aruco_length / 2, -aruco_length / 2),
            zs=(0, 0), color='k')
    ax.plot3D(xs=(aruco_length / 2, aruco_length / 2),
            ys=(-aruco_length / 2, aruco_length / 2),
            zs=(0, 0), color='k')

# 沿著 X 軸推進變換矩陣 T
# T: 齊次變換矩陣, rx_offset: 沿 X 軸的位移
# 註：底下T_Ry_Advence與T_Rz_Advence邏輯完全相同，不再註解
# 我猜這應該是學長一開始寫還不熟，才搞出三個功能相同但名稱不同的function
def T_Rx_Advence(T, rx_offset):
    result_T = T # 複製 T 避免修改原始矩陣
    R = result_T[:3, :3] # 提取旋轉矩陣
    R_z = R[:, 2] # 提取 X 軸方向
    result_T[:3, 3] += R_z * rx_offset # 沿 X 軸方向進行位移
    return result_T

def T_Ry_Advence(T, ry_offset):
    result_T = T
    R = result_T[:3, :3]
    R_z = R[:, 2]
    result_T[:3, 3] += R_z * ry_offset
    return result_T

def T_Rz_Advence(T, rz_offset):
    result_T = T.copy()
    R = result_T[:3, :3]
    R_z = R[:, 2]
    result_T[:3, 3] += R_z * rz_offset
    return result_T


def rotation_matrix(x, y, z):
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

# 將深度圖轉換成點雲數據
# K: 相機內部參數矩陣, depth_img: 深度圖, min_dist: 最小距離閾值, max_dist: 最大距離閾值
def Depth_to_PointCloud(K, depth_img, min_dist = 0, max_dist = 2):
    K_inv = np.linalg.inv(K) # 計算相機內部參數矩陣的逆矩陣
    point_cloud = [] # 用於存儲點雲的空列表
    #percent = 0

    # 遍歷深度圖中的每個像素
    for v in range(depth_img.shape[0]): # 行 (高度)
        for u in range(depth_img.shape[1]): # 列 (寬度)
            s = depth_img[v][u] / 1000 #z-distance(depth) in meter  # 將深度值從毫米轉換成米 (z 距離)

            # 檢查深度值是否在允許的範圍內
            if s <= min_dist or s >= max_dist:
                continue

            # 創建該像素點的齊次座標 (u, v, 1)
            w = np.array([u, v, 1]).reshape(3, 1)

            # 使用內部參數矩陣逆變換和深度值計算該點的 3D 座標
            W = s * np.dot(K_inv, w)

            # 將計算出的 3D 點加入點雲列表
            point_cloud.append(W)

        #顯示進度百分比用的，可以註解掉    
        percent_temp = int(v / depth_img.shape[0] * 100) + 1
        #if percent_temp != percent:
        #    percent = percent_temp
        #    print(percent, "%")
    point_cloud = np.array(point_cloud) # 將列表轉換為 NumPy 數組
    return point_cloud.reshape((len(point_cloud), 3)) # 將點雲數據轉換成 (N, 3) 的形狀