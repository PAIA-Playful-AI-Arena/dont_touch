# 不要碰碰車

![Dont_touch](https://img.shields.io/github/v/tag/PAIA-Playful-AI-Arena/Dont_touch)
[![Python 3.9](https://img.shields.io/badge/python->3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![MLGame](https://img.shields.io/badge/MLGame->10.4.6a2-<COLOR>.svg)](https://github.com/PAIA-Playful-AI-Arena/MLGame)

在茫茫的宇宙中，有許多的障礙物，要如何閃過障礙物，走到白洞前往新世界呢？本遊戲提供多元的關卡，隨著遊戲難度提升，考驗各位玩家如何在多變的環境下，依然能夠走到終點。小心，碰到牆壁可是會爆炸的！！

<img src="https://raw.githubusercontent.com/PAIA-Playful-AI-Arena/dont_touch/refs/heads/main/asset/banner.gif" height="500"/>

`遊戲目標`&nbsp;&nbsp;&nbsp; 在遊戲時間截止前到達迷宮的終點，並且盡可能減少碰撞牆壁的次數。

`排名方式`&nbsp;&nbsp;&nbsp; 分數高者獲勝
    - 分數＝ `檢查點數量`x10000 - `碰撞次數`x10 - `使用時間`x0.001


## 啟動方式

- 直接啟動 [main.py](https://github.com/PAIA-Playful-AI-Arena/dont_touch/blob/main/main.py) 即可執行

## 遊戲參數設定

```python
# main.py 
game = Dont_touch(user_num=1, map_num=1, time_to_play=450, sound="off", dark_mode='dark', map_file=None)
```

* `user_num`：使用者人數，最少1人，最多4人。
- `map_num`：選擇不同的迷宮，迷宮編號從1開始，預設為1號地圖。
- `map_file`：可自行匯入地圖
- `time_to_play`：限制遊戲總時間，單位為 frame，時間到了之後即使有玩家還沒走出迷宮，遊戲仍然會結束。
- `sound`：音效設定，可選擇"on"或"off"，預設為"off"
- `dark_mode`: 選擇是否開啟深色模式，可選擇"light"或"dark"，預設為"dark"

## 座標系統

- 使用 `Box2D` 的座標系統，長度單位為 `cm` 。
- `左下角`為原點 (0,0)，`Ｘ軸`向`右`為正，`Y軸`向`上`為正。
- 使用 Tiled 來繪製地圖，地圖一格為 `5cm`。
- 所有座標皆回傳物件`中心點`之座標。

### **玩法**

- 移動幽浮：上下左右方向鍵

<br />

### 幽浮

- 大小 10cm x 10cm
- 控制左右輪轉速，達到前進、後退、轉彎的目的。 左輪與右輪的轉速由玩家程式控制，範圍為 -255 ~ 255。 速度為 0 時相當於停在原地，速度為負值實則輪子向後轉，速度為正時輪子向前轉。

### 感測器

- 可透過感測器測量距離`車身`到`牆壁`的距離。
- 一台車有 6 個感測器。

### 檢查點

- 為一個線段，通過此線段，檢查點數量加1
  
### 終點

- 大小 15cm x 15cm
- 為一個白色蟲洞，象徵逃出迷宮，可以前往新世界。

<br />

---

## 進階說明

### 特殊功能

- 可以使用 `H` 按鍵，來開啟/關閉 遊戲補充資訊。

### ＡＩ範例

```python
class MLPlay:
    def __init__(self, ai_name,*args,**kwargs):
        self.player_no = ai_name
        self.r_sensor_value = 0
        self.l_sensor_value = 0
        self.f_sensor_value = 0
        self.control_list = {"left_PWM" : 0, "right_PWM" : 0}
        # print("Initial ml script")
        print(kwargs)

    def update(self, scene_info: dict, *args, **kwargs):
        """
        Generate the command according to the received scene information
        """
        if scene_info["status"] != "GAME_ALIVE":
            return "RESET"
        self.r_sensor_value = scene_info["R_sensor"]
        self.l_sensor_value = scene_info["L_sensor"]
        self.f_sensor_value = scene_info["F_sensor"]
        if self.f_sensor_value >15:
            self.control_list["left_PWM"] = 100
            self.control_list["right_PWM"] = 100
        else:
            self.control_list["left_PWM"] = 0
            self.control_list["right_PWM"] = 0
        return self.control_list

    def reset(self):
        """
        Reset the status
        """
        pass

```

### 遊戲資訊

- `scene_info` 的資料格式如下

```json
{
    "frame": 16,
    "status": "GAME_ALIVE", 
    "x": 107.506, 
    "y": -112.5, 
    "angle": 0.0, 
    "R_sensor": 5.6, 
    "L_sensor": 4.7, 
    "F_sensor": 87.6, 
    "B_sensor": 17.6, 
    "L_T_sensor": -1, 
    "R_T_sensor": -1, 
    "end_x": 12.5,
    "end_y": -12.5,
    "crash_count":1,
    "check_points": [(10, 50), (34, 20)]
}

```

- `frame`：遊戲畫面更新的編號
- `status`： 目前遊戲的狀態
  - `GAME_ALIVE`：遊戲進行中
  - `GAME_PASS`：遊戲通關
  - `GAME_OVER`：遊戲結束
- `x`：玩家自己車子的x座標，該座標系統原點位於迷宮`左下角`，`x軸`向`右`為正。
- `y`：玩家自己車子的y座標，該座標系統原點位於迷宮`左下角`，`y軸`向`上`為正。
- `angle`：玩家自己車子的朝向，車子向上為0度，數值逆時鐘遞增至360
- `R_sensor`：玩家自己車子右邊超聲波感測器的值，資料型態為數值
- `L_sensor`：玩家自己車子左邊超聲波感測器的值，資料型態為數值
- `F_sensor`：玩家自己車子前面超聲波感測器的值，資料型態為數值
- `L_T_sensor`：玩家自己車子左前超聲波感測器的值，資料型態為數值，單位是公分。
- `R_T_sensor`：玩家自己車子右前超聲波感測器的值，資料型態為數值
- `B_sensor`：玩家自己車子後面超聲波感測器的值，資料型態為數值
- `end_x`：終點x座標，該座標系統原點位於迷宮`左下角`，`x軸`向`右`為正。。
- `end_y`：終點y座標，該座標系統原點位於`左下角`，`y軸`向`上`為正。
- `crash_count`：玩家此局遊戲中碰撞牆壁的次數，資料型態為數值。
- `check_points`:遊戲在必經的地方設置數個檢查點，此資料包含所有檢查點的座標，資料型態為列表。

座標資訊請參考 `座標系統` 章節

### 動作指令

- 在 update() 最後要回傳一個字典，資料型態如下。

    ```python
    {
            'left_PWM': 0,
            'right_PWM': 0
    }
    ```

    其中`left_PWM`與`right_PWM`分別代表左輪與右輪的馬力，接受範圍為-255~255。

### 遊戲結果

- 最後結果會顯示在console介面中，若是PAIA伺服器上執行，會回傳下列資訊到平台上。

|player|rank|used_frame|
|-|-|-|
|1P|1|1136|

|total_checkpoints|check_points|crash_count|score|
|-|-|-|-|
|8|8|2|79978.864|

- `frame_used`：表示遊戲使用了多少個frame
- `status`：表示遊戲結束的狀態
  - `fail`:遊戲過程出現問題
  - `passed`:單人的情況下，成功走到終點，回傳通過
  - `un_passed`:沒有任何人走到終點，回傳不通過
  - `finish`:多人的情況下，任一人走到終點，回傳完成
- `attachment`：紀錄遊戲各個玩家的結果與分數等資訊
  - `player`：玩家編號
  - `rank`：排名
  - `used_frame`：個別玩家到達最後一個檢查點使用的frame數
  - `total_checkpoints`：該地圖的總檢查點數量
  - `check_points`：玩家通過的檢查點數量
  - `crash_count`：玩家車子碰撞牆壁的次數
  - `score`：系統依據排名規則所計算之分數，分數愈高者排名愈前
    - 分數計算規則：`check_points` *10000 - 10* `crash_count` - 0.001 * `used_frame`

###### tags: `PAIA GAME`
