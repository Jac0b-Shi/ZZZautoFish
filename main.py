##########################################################################################################
#   Description: 钓鱼主程序
#   Authors:     BaiYuan <395642104@qq.com>
#   Modifier:    Jac0b_Shi <shitian_xiang@shu.edu.cn>
##########################################################################################################

import ctypes
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

FISH_DELAY_TIME = 0.5 # 等待上鱼的wait时间
ACCURATE_DELAY_TIME = 0.2 # 准确点击F的延时

class FishBot:
    """基于OCR实现的ZZZ钓鱼机器人
    """    
    def __init__(self):
        """初始化基础参数
        """        
        self.running = True
        self.fishNum = 0
        self.last_action_time = 0
        self.struggle_start = 0
        self.debug_counter = 0

        self.lastState = None
        self.newState = None
        
        # OCR初始化
        try:
            self.ocr = PaddleOCR(det_model_dir = str(paddleOCRModlePath / "whl" / "det"/ "ch"/ "ch_PP-OCRv4_det_infer"), 
                        rec_model_dir = str(paddleOCRModlePath / "whl" / "rec" / "ch" / "ch_PP-OCRv4_rec_infer"), 
                        cls_model_dir = str(paddleOCRModlePath / "whl" / "cls" / "ch_ppocr_mobile_v2.0_cls_infer"),
                        lang = 'ch', show_log = False, use_angle_cls=False)

        except Exception as e:
            print(f"ocr模型初始化失败:{str(e)}")
            raise e
        
        # 窗口控制参数
        # 先尝试查找国服窗口，若未找到则查找国际服窗口
        self.hwnd = win32gui.FindWindow(None, "绝区零")
        if not self.hwnd:
            self.hwnd = win32gui.FindWindow(None, "ZenlessZoneZero")
            if not self.hwnd:
                raise Exception("游戏窗口未找到，请先启动国服或国际服客户端")

    def captureWinodow(self):
        """捕获图像
        """

        # 获取窗口坐标
        rect = win32gui.GetWindowRect(self.hwnd)
        self.window = {
            'left': rect[0],
            'top': rect[1],
            'width': rect[2] - rect[0],
            'height': rect[3] - rect[1]
        } 

        try:
            # 计算截取区域（left, top, right, bottom）
            region = (
                self.window['left'],
                self.window['top'],
                self.window['left'] + self.window['width'],
                self.window['top'] + self.window['height']
            )
            
            # 带重试机制的截图（最多尝试3次）
            for attempt in range(3):
                try:
                    screenshot = ImageGrab.grab(bbox=region, all_screens=True)
                    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                        
                    return frame
                except Exception as e:
                    if attempt == 2:
                        raise
                    print(f"截图失败第{attempt+1}次尝试...")
                    time.sleep(0.05)
                    
        except Exception as e:
            print(f"最终截图失败：{str(e)}")
            return None
        
    def ocrHandle(self, frame: cv2.typing.MatLike):
        """获得的frame进行ocr处理

        :param frame: 截图帧
        """        
        if frame is None:
            return []
        
        try:
            result = self.ocr.ocr(frame, cls=True)[0]

            # print(result)
            if not result:
                return []
            
            # 拼接获得的str组成的列表
            ocrList =  [line[1][0].lower().strip() for line in result if line[1] and line[1][0]]
            if "长按" in ocrList and "a" in ocrList:
                ocrList.append("长按a")
            elif "长按" in ocrList and "d" in ocrList:
                ocrList.append("长按d")
            elif "连点" in ocrList and "a" in ocrList:
                ocrList.append("连点a")
            elif "连点" in ocrList and "d" in ocrList:
                ocrList.append("连点d")
            elif "长按" in ocrList and "f" in ocrList:
                ocrList.append("长按f")
            elif "准确点击" in ocrList and "f" in ocrList:
                ocrList.append("准确点击f")

            return ocrList

        except Exception as e:
            print(f"OCR异常：{str(e)}")
            return []
        
    # =============== 基本操作函数 =============== #
    def holdKey(self, key: str, duration: float):
        """稳定长按

        :param key: 按键名称
        :param duration: 持续时间(s)
        """
        keyboard.press(key)
        time.sleep(duration)
        keyboard.release(key)
        time.sleep(0.3)  # 操作后冷却
    
    def spamKey(self, key: str, times: int):
        """随机间隔连击

        :param key: 按键名称
        :param times: 连续点按次数
        """        
        for _ in range(times):
            keyboard.press(key)
            time.sleep(0.01 + random.random()*0.01)
            keyboard.release(key)
            time.sleep(0.02 + random.random()*0.01)

    def tabKey(self, key: str):
        """点击按键一次

        :param key: 按键名称
        """        
        keyboard.press(key)
        time.sleep(0.05)
        keyboard.release(key)

    def stateManager(self, ocrList: list[str]):
        """钓鱼状态机

        :param ocrList: 使用OCR获取的字符串列表
        """        

        # 获取状态
        stateMap = [
            ("点击按键抛竿", "idle"),
            ("点击f按键抛竿", "idle"),
            ("等待上鱼", "wait"),
            ("等待上", "wait"),
            ("正确时机点击f按键上鱼", "wait2"),
            ("正确时机点击·按键上鱼", "wait2"),
            ("正确时机点击", "wait2"),
            ("正确时机", "wait2"),
            ("点击空白处关闭", "restart"),
            ("鱼跑了！", "fail"),
            ("鱼跑了!", "fail"),
            ("连点a", "连点a"),
            ("连点d", "连点d"),
            ("长按a", "长按a"),
            ("长按d", "长按d"),
            ("拿下这条大鱼！", "连点f"),
            ("用技巧拿下它！", "连点f"),
            ("集中一处发力！", "连点f"),
            ("集中一处发", "连点f"),
            ("它变得乏力了！", "连点f"),
            ("时机已到！", "连点f"),
            ("做好准备！", "连点f"),
            ("长按f按钮", "长按f"),
            ("长按按钮", "长按f"),
            ("长按日按钮", "长按f"),
            ("准确点击f按钮", "准确点击f"),
        ]

        for prompt, state in reversed(stateMap):
            if prompt in ocrList:
                self.newState = state
                break
        else:
            self.newState = None

        # 状态处理
        if self.newState == self.lastState:
            print(f"STATE= \"{self.newState}\", 状态无变化")
            return
        
        else:
            self.lastState = self.newState # 状态更新
            if self.newState == "idle":
                print(f"STATE= \"{self.newState}\", 准备抛竿")
                self.tabKey(key = "f")

            elif self.newState == "wait":
                print(f"STATE= \"{self.newState}\", 正在等待上鱼")

            elif self.newState == "wait2":
                print(f"STATE= \"{self.newState}\", 准备在恰当时机点按F上鱼")
                time.sleep(FISH_DELAY_TIME)
                self.tabKey(key = "f")

            elif self.newState == "连点a":
                print(f"STATE= \"{self.newState}\", 进行连点A处理")
                self.spamKey(key = "a", times = 16)
                self.tabKey(key="space")

            elif self.newState == "连点d":
                print(f"STATE= \"{self.newState}\", 进行连点D处理")
                self.spamKey(key = "d", times = 16)
                self.tabKey(key="space")

            elif self.newState == "长按a":
                print(f"STATE= \"{self.newState}\", 进行长按A处理")
                self.holdKey(key = "a", duration = 2.4)
                self.tabKey(key="space")

            elif self.newState == "长按d":
                print(f"STATE= \"{self.newState}\", 进行长按D处理")
                self.holdKey(key = "d", duration = 2.4)
                self.tabKey(key="space")

            elif self.newState == "连点f":
                print(f"STATE= \"{self.newState}\", 进行连点F处理")
                time.sleep(0.8)
                self.spamKey(key="f", times=35)
                self.tabKey(key="space")

            elif self.newState == "长按f":
                print(f"STATE= \"{self.newState}\", 进行长按F处理")
                self.holdKey(key = "f", duration = 2.8)
                self.tabKey(key="space")

            elif self.newState == "准确点击f":
                print(f"STATE= \"{self.newState}\", 进行准确点击F处理")
                time.sleep(ACCURATE_DELAY_TIME)
                self.tabKey(key = "f")
                time.sleep(0.1)
                self.tabKey(key="space")

            elif self.newState == "restart":
                self.fishNum += 1
                print(f"STATE= \"{self.newState}\", 钓鱼成功, 当前已成功钓鱼 \"{self.fishNum}\" 次")

                for _ in range(4):
                    x = self.window['left'] + random.randint(100, self.window['width'] - 100)
                    y = self.window['top'] + random.randint(100, self.window['height'] - 100)
                    pyautogui.click(x, y)
                    time.sleep(random.uniform(0.1, 0.3))

            elif self.newState == "fail":
                print(f"STATE= \"{self.newState}\", 钓鱼失败")

                for _ in range(4):
                    x = self.window['left'] + random.randint(100, self.window['width'] - 100)
                    y = self.window['top'] + random.randint(100, self.window['height'] - 100)
                    pyautogui.click(x, y)
                    time.sleep(random.uniform(0.1, 0.3))

            else:
                print(f"UNKNOWEN_STATE= {self.newState}, continue")

    def mainLoop(self):
        """启动主循环
        """      

        keyboard.add_hotkey('f10', lambda: setattr(self, 'running', False))
        print("自动钓鱼启动成功, F10停止")
        
        while self.running:
            try:
                
                # 获取游戏画面
                print("\n")
                frame = self.captureWinodow()
                if frame is None:
                    time.sleep(1)
                    continue

                # 进行OCR处理
                ocrList = self.ocrHandle(frame = frame)
                print(f"ocrList= {ocrList}")

                # 进行状态管理
                self.stateManager(ocrList = ocrList)
                
                time.sleep(0.15)
            except Exception as e:
                print(f"运行时异常: {str(e)}")
                self.running = False
        
        print("自动钓鱼已停止")

    @staticmethod
    def is_admin():
        """检查当前是否以管理员权限运行"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception as e:
            print(f"权限检查失败: {str(e)}")
            return False


if __name__ == "__main__":

    bot = FishBot()
    if not bot.is_admin():
        print("程序需要管理员权限运行, 请以管理员权限重启终端")
    else:
        bot.mainLoop()