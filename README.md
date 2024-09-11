DRV Modbus
==========
*生成自ChatGPT，內容可能有誤*

概述
--

DRV Modbus 是一個基於 `pymodbus` 的 Python 庫，用於控制台達 DRV 系列機械手臂。此庫提供了一系列功能，包括讀取機械手臂的 TCP 位姿、執行移動命令、控制吸盤以及透過 ArUco 標記進行機械手臂校正。

目錄結構
----


```bash
DRV-Modbus/
├── aruco_spawn_example.py       # ArUco 標記生成範例
├── drv_modbus/                  # Modbus 相關模組
├── drv_modbus_example.py        # Modbus 控制範例
├── find_aruco_example.py        # ArUco 標記檢測範例
├── keyboard_jog_example.py      # 鍵盤控制機械手臂移動的範例
├── realsense_RGB_example.py     # RealSense 相機範例
├── warp_suction_example.py      # 吸盤控制範例
├── README.md                    # 本說明文件
└── ...
```

主要功能
----

### 1\. 機械手臂控制

透過 Modbus 協議控制台達 DRV 機械手臂的運動。

-   **TCP 位姿讀取**: 讀取機械手臂末端執行器的位姿。
-   **移動控制**: 透過 `Go_Position` 函數實現機械手臂的精確移動。
-   **吸盤控制**: 控制吸盤的啟動與停止。

### 2\. ArUco 標記

透過 ArUco 標記進行機械手臂的校正與標定。

-   **標記生成**: 利用 `aruco_spawn_example.py` 生成 ArUco 標記圖像。
-   **標記檢測**: 使用 `find_aruco_example.py` 檢測攝像頭中的 ArUco 標記。

### 3\. RealSense 支持

使用 Intel RealSense 相機進行影像處理與 3D 檢測。

安裝指南
----

1.  確保已安裝 Python 3 及 `pip`，然後安裝所需依賴庫：
    
`pip install -r requirements.txt` 
    
2.  確保你的環境支持 Modbus TCP 通訊並連接到台達機械手臂。
    

使用方法
----

### 1\. 運行 `drv_modbus_example.py`

此範例展示了如何連接到台達 DRV 機械手臂並讀取其 TCP 位姿。

`python drv_modbus_example.py` 

### 2\. 使用鍵盤控制機械手臂

運行 `keyboard_jog_example.py`，可以透過鍵盤方向鍵來控制機械手臂的移動：

`python keyboard_jog_example.py` 

### 3\. 生成 ArUco 標記

運行 `aruco_spawn_example.py` 生成指定 ID 和分辨率的 ArUco 標記：

`python aruco_spawn_example.py` 

### 4\. 檢測 ArUco 標記

運行 `find_aruco_example.py` 檢測攝像頭中的 ArUco 標記並顯示其位置：

`python find_aruco_example.py` 

### 5\. 控制吸盤

運行 `warp_suction_example.py` 控制機械手臂的吸盤動作：

`python warp_suction_example.py` 

貢獻
--

歡迎任何形式的貢獻！請通過 `pull request` 提交。

授權
--

此專案根據 [BSD-3-Clause](LICENSE) 授權。
