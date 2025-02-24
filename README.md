# ZZZ自动化钓鱼工具

## 1 项目简介

使用paddleocr实现的zzz自动化钓鱼工具, 能够在钓鱼界面实现自动化的状态识别, 并持续钓鱼, 直到用户停止



## 2 运行环境

1. 项目使用python3.12.3开发, 其他版本python可能也可, 可以尝试

2. 项目依赖部分三方库, 如果是conda环境, 使用下面命令安装:

   ```
   conda install keyboard
   conda install numpy
   conda install opencv
   conda install pillow
   conda install pyautogui
   conda install pywin32
   ```

   paddleocr经过验证无法用conda安装, 改用pip安装也能用

   ```
   pip install paddlepaddle
   pip install paddleocr==2.7.3
   ```

    如果是pip环境, 把上面的conda install改成pip install即可

   ```
   pip install keyboard
   pip install numpy
   pip install opencv
   pip install pillow
   pip install pyautogui
   pip install pywin32
   ```

   关于conda和pip的使用方法请百度搜索

   另外, paddleocr安装时可能会覆盖numpy版本, 你可能需要先安装paddleocr再安装numpy
   
   如果出现numpy的import错误, 可以尝试更新numpy
   
   ```
   conda update numpy
   ```

## 3 运行代码

​	配好环境后, 按下面步骤运行代码即可

1. 打开"绝区零.exe", 推荐将分辨率调整到1280*720窗口, 其他分辨率应该也可以运行

2. 将场景移动到钓鱼界面, 石礁钓点和近海钓点均可

3. 直接运行本项目的main.py文件

   ```
   python main.py
   ```

   需要以**管理员权限**打开终端才能运行, 否则出现下面错误:

   ```
   (base) PS C:\Users\风白> python D:\Tool\Admin\ZZZautoPara\fish\main.py
   程序需要管理员权限运行, 请以管理员权限重启终端
   ```

   出现类似于下面的输出代表代码正常运行:

   ```
   [2025/02/22 14:03:38] ppocr WARNING: Since the angle classifier is not initialized, it will not be used during the forward process
   ocrList= ['绝区零', 'x', 'level12', 'uid:14344493 -1']
   UNKNOWEN_STATE= None, continue
   
   
   [2025/02/22 14:03:39] ppocr WARNING: Since the angle classifier is not initialized, it will not be used during the forward process
   ocrList= ['绝区零', 'x', 'level12', 'uid:14344493 -1']
   STATE= "None", 状态无变化
   
   [2025/02/22 14:03:39] ppocr WARNING: Since the angle classifier is not initialized, it will not be used during the forward process
   ocrList= ['绝区零', 'x', 'level12', 'uid:14344493 -1']
   STATE= "None", 状态无变化
   ```

4. 再点击一下绝区零窗口, 确保是zzz程序处在最前端并被操作, 代码运行期间不能移动窗口

5. 如需停止, **按F10即可**

## 4 注意事项

1. 程序长时间运行可能出现窗口不响应脚本输入的情况, 这时候推荐重启zzz和脚本
2. 脚本使用paddleocr作为ocr模型, 因为模型限制, 请将本脚本移动到 **全英文目录** 下执行, 否则报错
3. 由于不同电脑的响应速度不同, 可能会出现上鱼操作失败的情况(等待紫色圈圈合拢点F的操作), 如果这种操作总是失败, 你可以尝试修改源码的**FISH_DELAY_TIME**

```
import cv2
import keyboard
import time
import win32gui
import random
import pyautogui

from PIL import ImageGrab
from paddleocr import PaddleOCR
from pathlib import Path

import numpy as np

rootDir = Path(__file__).parent.resolve()
paddleOCRModlePath = rootDir / ".paddleocr"

FISH_DELAY_TIME = 1.3 # 等待上鱼的wait时间, 修改这个值

class FishBot:

  """基于OCR实现的ZZZ钓鱼机器人
```

