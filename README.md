DRV Modbus
==========
*生成自ChatGPT，內容可能有誤*

概述
--

DRV Modbus 是一個基於 `pymodbus` 的 Python 庫，用於控制台達 DRV 系列機械手臂。此庫提供了一系列功能，包括讀取機械手臂的 TCP 位姿、執行移動命令、控制吸盤以及透過 ArUco 標記進行機械手臂校正。

**注意：由於使用pyrealsense2庫，因此請使用Python 3.11版避免版本衝突，避免使用3.12以上版本**

主要功能
----

### 1\. 機械手臂控制(./robot)

透過 Modbus 協議控制台達 DRV 機械手臂的運動。

-   **robot控制**: 提供一個類別，方便控制機械手臂  
-   **warp_suction_example.py** : 子程學長最終寫的demo，用以判斷並吸取銀板，並根據銀板顏色放置在不同位置  

### 2\. ArUco 標記(./aruco)

透過 ArUco 標記進行機械手臂的校正與標定。

-   **標記生成**: 利用 `aruco_spawn_example.py` 生成 ArUco 標記圖像。  
-   **標記檢測**: 使用 `find_aruco_example.py` 檢測攝像頭中的 ArUco 標記。  

### 3\. RealSense 支持(./realsense)

使用 Intel RealSense 相機進行影像處理與 3D 檢測。

安裝指南
----

1.  確保已安裝 Python 3 及 `pip`，然後安裝所需依賴庫：


```
cd path/to/your/project/DRV-Modbus #請記得改成你專案的位置，或乾脆在你專案內開啟powershell
pip install -r requirements.txt #只要執行這個 就可以自動安裝所有所需依賴庫

``` 

另外提供了作者本人的vscode extensions，以便初學者使用

```

Get-Content vscode-extensions.txt | ForEach-Object { code --install-extension $_ } #只要執行這個，就會安裝一堆你可能不會用到的extension，謹慎操作

```

2.  確定你正確連接了台達機器手臂，並且能夠ping到，且台達機器手臂的ModbusTCP設定頁面正確
    

使用方法
----

### 1\. 執行 `drv_modbus_example.py`

此範例展示了如何連接到台達 DRV 機械手臂並讀取其 TCP Pose，並可根據使用者需要，在讀取Pose前先發送「移動到特定Pose」的命令。

**注意：如果連這個都無法正確執行，就表示環境設定錯誤，或根本沒有連線到，請把網路線插好，ping到後再檢查是否為環境設定問題**

`python examples/drv_modbus_example.py` 

### 2\. 使用鍵盤控制機械手臂

運行 `examples/keyboard_jog_example.py`，可以透過鍵盤方向鍵來控制機械手臂的移動：

`python examples/keyboard_jog_example.py` 

按上箭頭，向-x方向移動

按下箭頭，向+x方向移動

按左箭頭，向-y方向移動

按右箭頭，向+y方向移動

按L_Shift，向-z方向移動

按L_Ctrl，向+z方向移動


### 3\. 生成 ArUco 標記

運行 `examples/aruco_spawn_example.py` 生成指定 ID 和分辨率的 ArUco 標記：

`python examples/aruco_spawn_example.py` 

### 4\. 檢測 ArUco 標記

運行 `find_aruco_example.py` 檢測realsense攝影機中的 ArUco 標記  
並以ArUco位置建立相機坐標系  

`python find_aruco_example.py` 


### 5\. 控制吸盤

運行 `warp_suction_example.py` 控制機械手臂的吸盤動作：

`python examples/warp_suction_example.py`    

這個功能比較複雜，是檢測aruco位置後，還要命令機械手臂移動並控制吸盤的程式  
注意：此程式的機器人控制使用的是被棄用的request.py, send.py，後續開發請改用classRobot.py  
注意：在發送命令時請盡可能採用Robot_Go_MovL，而不是Robot_Go_MovP，避免機器人的運動速度過慢。

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
    
#Suction_OFF同理，或可以新增自己的函式，或可以寫為int(0b0000010000000000)
備註：舊版有關request.py, send.py已經棄用，請改用robot類別來處理
```

已知問題  
--  
在發送運動命令(Robot.sendMotionCommand)時，若使用Robot_Go_MovP作為eRobotCommand傳入，則機器人會以較慢的速度運動，請盡可能使用Robot_Go_MovL取代Robot_Go_MovP  


貢獻
--

歡迎任何形式的貢獻！請通過 `pull request` 提交。

授權
--

此專案根據 [BSD-3-Clause](LICENSE) 授權。
