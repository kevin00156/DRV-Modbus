import pyrealsense2 as rs
import numpy as np

# 建立 RealSense 管線，這是一個封裝了相機流和處理功能的物件
pipeline = rs.pipeline()

# 配置管線 (可以用來設定流的參數，如解析度、幀率等)
config = rs.config()
#config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# 開始管線，啟動相機的數據流
pipeline.start(config)

# 在 pipeline 啟動後，設置相機的曝光參數
color_sensor = pipeline.get_active_profile().get_device().query_sensors()[1]  # 獲取彩色影像傳感器
#color_sensor.set_option(rs.option.enable_auto_exposure, 1)  # 禁用自動曝光
#color_sensor.set_option(rs.option.exposure, 100)  # 設置手動曝光值，根據需求調整曝光值

# 創建點雲物件，用於計算和處理點雲數據
pc = rs.pointcloud()


def Get_Depth_K():
    """
    取得深度相機的內部參數矩陣 K
    K 是 3x3 的相機內部參數矩陣，包含焦距和主點偏移
    """
    profile = pipeline.get_active_profile()# 獲取當前的相機配置
    depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth)) # 獲取深度流的配置
    depth_intrinsics = depth_profile.get_intrinsics() # 獲取深度相機的內部參數 (焦距、主點偏移等)
    
    # 構建 3x3 的相機內部參數矩陣
    K = np.zeros((3, 3))
    K[0][0] = depth_intrinsics.fx # x 軸的焦距
    K[0][2] = depth_intrinsics.ppx # 主點在 x 軸的偏移
    K[1][1] = depth_intrinsics.fy # y 軸的焦距
    K[1][2] = depth_intrinsics.ppy # 主點在 y 軸的偏移
    K[2][2] = 1 # 齊次坐標矩陣的最後一行固定為 [0, 0, 1]
    return K

def Get_Color_K():
    """
    取得彩色相機的內部參數矩陣 K
    K 是 3x3 的相機內部參數矩陣，包含焦距和主點偏移
    """
    profile = pipeline.get_active_profile() # 獲取當前的相機配置
    color_profile = rs.video_stream_profile(profile.get_stream(rs.stream.color)) # 獲取彩色流的配置
    color_intrinsics = color_profile.get_intrinsics() # 獲取彩色相機的內部參數 (焦距、主點偏移等)
    
    # 構建 3x3 的相機內部參數矩陣
    K = np.zeros((3, 3))
    K[0][0] = color_intrinsics.fx # x 軸的焦距
    K[0][2] = color_intrinsics.ppx # 主點在 x 軸的偏移
    K[1][1] = color_intrinsics.fy # y 軸的焦距
    K[1][2] = color_intrinsics.ppy # 主點在 y 軸的偏移
    K[2][2] = 1 # 齊次坐標矩陣的最後一行固定為 [0, 0, 1]
    return K

# 取得彩色影像幀，並將其轉換為 NumPy 陣列
def Get_RGB_Frame():
    frame = pipeline.wait_for_frames()  # 等待新的一組幀 (彩色和深度)
    color_frame = frame.get_color_frame()  # 從幀中提取彩色影像
    return np.asarray(color_frame.get_data())  # 將彩色影像數據轉換為 NumPy 陣列並返回


def Get_PointCloud(sample_length = 10, 
                   is_decimation_filter = False, 
                   is_spatial_filter = False, 
                   is_temporal_filter = False, 
                   is_hole_filling_filter = False,
                   is_depth_to_disparity = False,
                   is_disparity_to_depth = False):
    """
    
    取得點雲數據
    sample_length: 取樣的幀數, is_decimation_filter: 是否使用稀疏濾波, is_spatial_filter: 是否使用空間濾波
    is_temporal_filter: 是否使用時間濾波, is_hole_filling_filter: 是否使用洞填補濾波
    is_depth_to_disparity: 是否將深度轉換為視差, is_disparity_to_depth: 是否將視差轉換為深度
    """

    # 將 RealSense 點雲輸出為 np array (nx3)
    # 初始化濾波器對象 (這邊可以簡單理解為影像前置處理)
    #output realsense point cloud as a np array(nx3)
    #Effectively reduces the depth scene complexity
    decimation = rs.decimation_filter() # 稀疏濾波器，減少深度場景的複雜性
    #1D edge-preserving spatial filter using high-order domain transform
    spatial = rs.spatial_filter() # 空間濾波器，用於保留 1D 邊緣
    #The temporal filter is intended to improve the depth data persistency by manipulating per-pixel values based on previous frames
    temporal = rs.temporal_filter() # 時間濾波器，用於根據之前幀數平滑深度數據
    #The filter implements several methods to rectify missing data in the resulting image
    hole_filling = rs.hole_filling_filter() # 填補濾波器，用於修復深度影像中的缺失數據

    depth_to_disparity = rs.disparity_transform(True)  # 將深度轉換為視差
    disparity_to_depth = rs.disparity_transform(False)  # 將視差轉換為深度


    # 創建幀列表，並從相機讀取 sample_length 個深度幀
    frames_list = []
    for f in range(sample_length):
        frame = pipeline.wait_for_frames() # 等待新的幀
        frames_list.append(frame.get_depth_frame()) # 提取深度幀並加入列表
    
    
    # 開始處理點雲，從第一個幀開始
    processed_frame = frames_list[0]
    # 根據function輸入參數，決定是否啟用對應的濾波器
    for f in frames_list:
        if is_decimation_filter:
            processed_frame = decimation.process(f)
        if is_spatial_filter:
            processed_frame = spatial.process(f)
        if is_temporal_filter:
            processed_frame = temporal.process(f)
        if is_hole_filling_filter:
            processed_frame = hole_filling.process(f)
        if is_depth_to_disparity:
            processed_frame = depth_to_disparity.process(f)
        if is_disparity_to_depth:
            processed_frame = disparity_to_depth.process(f)

    # 計算點雲，並將頂點數據轉換為 NumPy 陣列
    points = pc.calculate(processed_frame) # 計算點雲
    verts = np.asanyarray(points.get_vertices()).view(np.float32).reshape(-1, 3) # 將頂點數據轉換為浮點數陣列
    return verts # 返回點雲數據 (nx3)
