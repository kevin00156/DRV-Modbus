DRV Modbus
==========
*生成自ChatGPT，內容可能有誤*

概述
--

DRV Modbus 是一個基於 `pymodbus` 的 Python 庫，用於控制台達 DRV 系列機械手臂。此庫提供了一系列功能，包括讀取機械手臂的 TCP 位姿、執行移動命令、控制吸盤以及透過 ArUco 標記進行機械手臂校正。
**注意：由於使用pyrealsense2庫，因此請使用Python 3.11版避免版本衝突**

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

-   **TCP 姿態讀取**: 讀取機械手臂末端執行器的Pose。
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


```
cd path/to/your/project/DRV-Modbus #請記得改成你專案的位置，或乾脆在你專案內開啟powershell
pip install -r requirements.txt #只要執行這個 就可以自動安裝所有所需依賴庫

``` 

另外提供了作者本人的vscode環境，以便初學者使用

```

Get-Content vscode-extensions.txt | ForEach-Object { code --install-extension $_ } #只要執行這個，就會把你的vscode環境變得跟作者一樣，謹慎操作

```

2.  確保你的環境支持 Modbus TCP 通訊並連接到台達機械手臂。
    

使用方法
----

### 1\. 運行 `drv_modbus_example.py`

此範例展示了如何連接到台達 DRV 機械手臂並讀取其 TCP Pose，並可根據使用者需要，在讀取Pose前先發送「移動到特定Pose」的命令。

`python drv_modbus_example.py` 

### 2\. 使用鍵盤控制機械手臂

運行 `keyboard_jog_example.py`，可以透過鍵盤方向鍵來控制機械手臂的移動：

`python keyboard_jog_example.py` 
按上箭頭，向-x方向移動
按下箭頭，向+x方向移動
按左箭頭，向-y方向移動
按右箭頭，向+y方向移動
按L_Shift，向-z方向移動
按L_Ctrl，向+z方向移動

---

**以下仍未測試**

    ### 3\. 生成 ArUco 標記
    
    運行 `aruco_spawn_example.py` 生成指定 ID 和分辨率的 ArUco 標記：
    
    `python aruco_spawn_example.py` 
    
    ### 4\. 檢測 ArUco 標記
    
    運行 `find_aruco_example.py` 檢測攝像頭中的 ArUco 標記並顯示其位置：
    
    `python find_aruco_example.py` 


### 5\. 控制吸盤

運行 `warp_suction_example.py` 控制機械手臂的吸盤動作：

`python warp_suction_example.py` 

如果吸盤並不裝在DO_0，請嘗試更改發送的命令為你的DO

詳細方法請根據二進制決定發送的值，如DO_10，則請將輸入改為$`10^{10}=1024`$，如
```
def Suction_ON(c):
    """
    打開吸盤

    參數:
        c: Modbus TCP 客戶端
    """
    c.write_register(0x02FE, 1024, 2)#改這行的第二個arg
    
#Suction_OFF同理，或可以新增自己的函式
```
貢獻
--

歡迎任何形式的貢獻！請通過 `pull request` 提交。

授權
--

此專案根據 [BSD-3-Clause](LICENSE) 授權。
