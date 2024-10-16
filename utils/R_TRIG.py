class R_TRIG:
    def __init__(self):
        # 保存之前的布林值，用於檢測上升沿
        self.old_Input = False

    def __call__(self, Input: bool)->bool:
        # 如果上一次狀態是 False，且當前狀態是 True，表示上升沿
        if not self.old_Input and Input:
            self.old_Input = Input  # 更新狀態
            return True  # 偵測到上升沿
        else:
            # 如果沒有上升沿，僅更新狀態
            self.old_Input = Input
            return False  # 沒有偵測到上升沿