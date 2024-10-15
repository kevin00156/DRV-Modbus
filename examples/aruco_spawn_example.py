import cv2
from landmark import aruco

# 設定 ArUco 標記的 ID 和解析度
id = 5
resolution = 200

# 創建一個 5x5 大小、ID 為4的 ArUco 標記
aruco_5x5_100 = aruco.Aruco(aruco.ARUCO_DICT().DICT_5X5_100, id, resolution)

# 將生成的 ArUco 標記保存為圖片
cv2.imwrite(str(id) + "_" + str(resolution) + ".png", aruco_5x5_100.tag)

#cv2.imshow("ArUCo Tag", aruco_5x5_100.tag)
#cv2.waitKey(0)