from realsense import realsense
import cv2

# 持續讀取 RealSense 相機的 RGB 畫面
while True:
    frame = realsense.Get_RGB_Frame()  # 獲取 RGB 畫面
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # 轉換顏色格式
    cv2.imshow("realsense", frame)  # 顯示畫面

    # 每一個畫面停留1毫秒，按下任意鍵可退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
