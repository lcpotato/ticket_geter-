import uiautomator2 as u2
import datetime  
import time
import random
import os
import base64
import requests
import numpy as np
import subprocess
from pywinauto.application import Application
import tkinter as tk
from tkinter import messagebox
class BadmintonCourtSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("羽毛球场地选择")

        self.choices = [
            "兴庆校区文体中心三楼羽毛球场地",
            "兴庆校区文体中心壁球馆",
            "兴庆校区文体中心一楼羽毛球馆"
        ]

        self.selected_choice = tk.StringVar()
        self.selected_choice.set(self.choices[0])

        for choice in self.choices:
            tk.Radiobutton(root, text=choice, variable=self.selected_choice, value=choice).pack()

        tk.Button(root, text="确认选择", command=self.get_selected_choice).pack()

    def get_selected_choice(self):
        global a
        a = self.selected_choice.get()
        print(f"你选择的场地是: {a}")
        self.show_time_skip_dialog()

    def show_time_skip_dialog(self):
        global user_input
        result = messagebox.askyesno("时间跳过", "是否要跳过时间？")
        if result:
            user_input = 0
        else:
            user_input = 1
        print(f"时间跳过选择结果: {user_input}")
        self.root.destroy()  # 关闭主窗口，从而关闭所有 UI 窗

    

os.makedirs('debug', exist_ok=True)
log_file = open('debug/verification_log.txt', 'a')


def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    log_file.write(log_entry)
    print(log_entry.strip())


def improved_swipe(d, start_x, start_y, end_x, end_y):
    """改进的滑动算法：包含加速度和随机抖动"""
    control1 = (random.randint(20, 40), random.randint(-10, 10))
    control2 = (random.randint(60, 80), random.randint(-10, 10))

    points = []
    for t in np.linspace(0, 1, 40):
        x = (1 - t) ** 3 * start_x + 3 * (1 - t) ** 2 * t * (start_x + control1[0]) + 3 * (1 - t) * t ** 2 * (
                end_x - control2[0]) + t ** 3 * end_x
        y = (1 - t) ** 3 * start_y + 3 * (1 - t) ** 2 * t * (start_y + control1[1]) + 3 * (1 - t) * t ** 2 * (
                end_y - control2[1]) + t ** 3 * end_y
        points.append((int(x), int(y)))

    d.touch.down(start_x, start_y)

    last_point = points[0]
    for point in points[1:]:
        offset_x = random.randint(-2, 2)
        offset_y = random.randint(-2, 2)
        current_x = point[0] + offset_x
        current_y = point[1] + offset_y

        distance = np.sqrt((current_x - last_point[0]) ** 2 + (current_y - last_point[1]) ** 2)
        interval = max(0.01, min(0.1, distance / 500))

        d.touch.move(current_x, current_y)
        time.sleep(interval)
        last_point = point

    for _ in range(3):
        d.touch.move(end_x + random.randint(-2, 2), end_y + random.randint(-2, 2))
        time.sleep(0.02)

    d.touch.up(end_x, end_y)
    log(f"滑动完成：从 ({start_x},{start_y}) 到 ({end_x},{end_y})")
def improved_swipe_2_quicker_(d, start_x, start_y, end_x, end_y):
    """改进的滑动算法：包含加速度和随机抖动"""
    control1 = (random.randint(20, 40), random.randint(-10, 10))
    control2 = (random.randint(60, 80), random.randint(-10, 10))

    points = []
    for t in np.linspace(0, 1, 9):  # 减少点数
        x = (1 - t) ** 3 * start_x + 3 * (1 - t) ** 2 * t * (start_x + control1[0]) + 3 * (1 - t) * t ** 2 * (
                end_x - control2[0]) + t ** 3 * end_x
        y = (1 - t) ** 3 * start_y + 3 * (1 - t) ** 2 * t * (start_y + control1[1]) + 3 * (1 - t) * t ** 2 * (
                end_y - control2[1]) + t ** 3 * end_y
        points.append((int(x), int(y)))

    d.touch.down(start_x, start_y)

    last_point = points[0]
    for point in points[1:]:
        # 减少随机抖动
        offset_x = 0
        offset_y = 0
        current_x = point[0] + offset_x
        current_y = point[1] + offset_y

        # 简化时间间隔计算
        interval = 0.02

        d.touch.move(current_x, current_y)
        time.sleep(interval)
        last_point = point

    for _ in range(1):  # 减少结尾的随机抖动次数
        d.touch.move(end_x, end_y)
        time.sleep(0.02)

    d.touch.up(end_x, end_y)
    log(f"滑动完成：从 ({start_x},{start_y}) 到 ({end_x},{end_y})")

def get_element_shot(d, element, name):
    """获取指定元素的截图"""
    rect = element.info['bounds']
    d.screenshot(f"debug/{name}_full.png")
    return rect


def handle_slider_verification_v2(d):
    log("开始处理滑块验证")

    try:
        bg_element = d.xpath('//android.widget.Image[@resource-id="bg-img"]')
        slider_element = d.xpath('//android.view.View[@resource-id="slider-move-btn"]')
        slider_img_element = d.xpath('//android.widget.Image[@resource-id="slider-img"]')

        if not all([bg_element.wait(timeout=30), slider_element.wait(timeout=30), slider_img_element.wait(timeout=30)]):
            log("错误：缺少必要的验证元素")
            return False

        # 获取背景和滑块按钮的实际位置
        bg_rect = get_element_shot(d, bg_element, "background")
        slider_btn_rect = get_element_shot(d, slider_element, "slider_button")

        # 调用第三方打码平台获取需要移动的像素值
        bg_image_path = 'debug/background_full.png'
        with open(bg_image_path, 'rb') as f:
            b = base64.b64encode(f.read()).decode()

        def verify():
            url = "http://api.jfbym.com/api/YmServer/customApi"
            data = {
                "token": "En2fY1xu9wy4OHl8joGPk1m7PbF0rLziM1AIUdk3X8c",
                "type": "22222",
                "image": b,
            }
            _headers = {"Content-Type": "application/json"}
            return requests.post(url, headers=_headers, json=data).json()

        result = verify()
        if result.get('code') != 10000 or result.get('data', {}).get('code') != 0:
            log(f"第三方打码平台返回错误：{result}")
            return False

        # 直接获取第三方返回的需要移动的像素值
        move_distance = int(result['data']['data']) - random.randint(2, 5)

        # 计算滑块按钮中心坐标
        slider_start_x = (slider_btn_rect['left'] + slider_btn_rect['right']) // 2
        slider_start_y = (slider_btn_rect['top'] + slider_btn_rect['bottom']) // 2

        log(f"计算滑动距离：实际移动{move_distance}像素")

        # 执行滑动（横向移动，y轴保持不变）
        improved_swipe_2_quicker_(d, slider_start_x, slider_start_y, slider_start_x + move_distance, slider_start_y)

    except Exception as e:
        log(f"发生异常：{str(e)}")
        return False


def wait_until_target_time(target_time, skip_wait):
    if not skip_wait:
        now = datetime.datetime.now()
        wait_time = (target_time - now).total_seconds()
        if wait_time > 0:
            time.sleep(wait_time)
def check_page_loading(d, stadium_booking_icon, badminton_court_icon):
    max_attempts = 3
    attempts = 0
    while attempts < max_attempts:
        if badminton_court_icon.wait(timeout=5):
            print("页面正常加载，找到球馆图标")
            return True
        else:
            print("页面未正常加载，未找到球馆图标，尝试返回上一页面并重新点击")
            d.press("back")
            time.sleep(2)
            stadium_booking_icon.click()
            time.sleep(3)
            attempts += 1
    print("尝试多次后仍未正常加载页面")
    return False
def start_adb_and_simulator():
    # 打开 ADB 服务
    try:
        subprocess.run(['adb', 'start-server'], check=True)
        print("ADB 服务已启动")
    except subprocess.CalledProcessError as e:
        print(f"启动 ADB 服务时出错: {e}")

    # 打开雷神模拟器（假设模拟器可执行文件的路径已知，这里只是示例，你可能需要根据实际情况修改）
    simulator_path = r'D:\模拟器\LSPlayer\lsplayer.exe'  # 请替换为实际路径
    try:
        subprocess.Popen(simulator_path)
        print("雷神模拟器已启动")
    except FileNotFoundError:
        print("未找到雷神模拟器的可执行文件，请检查路径是否正确")

    time.sleep(20)

    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, check=True)
        devices_list = result.stdout.strip().split('\n')[1:]  # 跳过第一行标题 "List of devices attached"
        devices_list = [device for device in devices_list if device]  # 去除空行
        if devices_list:
            print("当前连接的 ADB 设备：")
            for device in devices_list:
                print(device)
        else:
            print("没有设备连接到 ADB")
    except subprocess.CalledProcessError as e:
        print(f"获取 ADB 设备列表时出错: {e}")
#前置准备工作


def start_wechat(wechat_path):
    # 检查微信程序是否存在
    if not os.path.isfile(wechat_path):
        print("微信安装路径不正确，请检查路径。")
        return

    # 启动微信
    app = Application(backend="uia").start(wechat_path)

    # 等待微信窗口出现
    wechat_window = app.window(title_re="微信")
    time.sleep(5)
    wechat_window.type_keys("{ENTER}")
    print("微信启动并登录成功！")


start_adb_and_simulator()

wechat_path = r"C:\Program Files (x86)\Tencent\Tencent\WeChat\WeChat.exe"

#start_wechat(wechat_path)

# 创建日志和输出目录
# 获取当前日期
current_date = datetime.datetime.now()
# 将日期中的 day 加上 4 天
new_date = current_date + datetime.timedelta(days=4)
# 以 year - month - day 的格式输出新日期
formatted_date = new_date.strftime('%Y-%m-%d')
print(f"当前日期加 4 天后的日期是: {formatted_date}")


if __name__ == "__main__":
    root = tk.Tk()
    selector = BadmintonCourtSelector(root)
    root.mainloop()


  
# 获取用户输入
#user_input = input("请输入（输入 0 则跳过等待到两个特定时间，输入其他任意字符则正常运行代码）：")
skip_wait = user_input == '0'
#target_x_ratio=input("请输入坐标例如#(0.665, 0.566)  (0.55,0.26)")
#target_y_ratio=input()
try:
    d = u2.connect('127.0.0.1:5555')
    print("成功连接模拟器")

    # 提前定位元素
    app_icon = d(text="移动交通大学")
    stadium_booking_icon = d(text="体育场馆预约")
    badminton_court_icon = d(text=a)#兴庆校区文体中心三楼羽毛球场地#兴庆校区文体中心壁球馆 #兴庆校区文体中心一楼羽毛球馆
    book_now_button = d(text="立即预订")
    date_element = d(textContains=formatted_date)
    
    # 获取当前时间
    now = datetime.datetime.now()
    # 设置目标时间 1（8:38:00）
    target_time_1 = now.replace(hour=8, minute=38, second=0, microsecond=0)#(hour=8, minute=38, second=0, microsecond=0)
    # 设置目标时间 2（8:40:02）
    target_time_2 = now.replace(hour=8, minute=40, second=2, microsecond=0)#(hour=8, minute=40, second=2, microsecond=0)

    # 等待到目标时间 1
    wait_until_target_time(target_time_1, skip_wait)

    if app_icon.wait(timeout=30):
        app_icon.click()
        print("成功点击移动交通大学应用图标")
        time.sleep(3)

        # 获取屏幕的宽度和高度
        width, height = d.window_size()

        # 等待体育场馆预约图标出现，最多等待 30 秒
        if stadium_booking_icon.wait(timeout=5):
            # 点击体育场馆预约图标
            stadium_booking_icon.click()
            print("成功点击体育场馆预约图标")
            #判断是否正常加载页面
            if check_page_loading(d, stadium_booking_icon, badminton_court_icon):
                # 等待到目标时间 2
                wait_until_target_time(target_time_2, skip_wait)

            # 点击特定球场
            if badminton_court_icon.wait(timeout=30):
                badminton_court_icon.click()
                print(f"成功点击{badminton_court_icon}")
                # 等待立即预定按钮出现，最多等待 30 秒
                if book_now_button.wait(timeout=30):
                    book_now_button.click()
                    print("成功点击立即预订按钮")

                    # 等待包含日期的元素出现，最多等待 30 秒
                    if date_element.wait(timeout=30):
                        date_element.click()
                        print(f"成功点击包含日期{formatted_date}的元素")

                        # 点击具体场次
                        target_x_ratio = 0.665
                        target_y_ratio = 0.566
                        target_x = width * target_x_ratio
                        target_y = height * target_y_ratio
                        print(f"计算得到的点击坐标为({target_x}, {target_y})")
                        d.click(target_x, target_y)
                        print(f"成功点击坐标({target_x}, {target_y})")#(0.665, 0.566)  (0.55,0.26)

                        # 点击我要下单
                        new_target_x_ratio = 0.542
                        new_target_y_ratio = 0.966
                        new_target_x = width * new_target_x_ratio
                        new_target_y = height * new_target_y_ratio
                        print(f"计算得到的新点击坐标为({new_target_x}, {new_target_y})")
                        d.click(new_target_x, new_target_y)
                        print(f"成功点击坐标({new_target_x}, {new_target_y})")
                        time.sleep(0.5)
                        # 处理滑块式人机验证
                        handle_slider_verification_v2(d)
                        print("处理滑块验证")

                                # 查找名为支付的元素
                        pay_element = d(text="支付")
                        if pay_element.wait(timeout=30):
                                    pay_element.click()
                                    print("成功点击名为支付的元素")
                                    time.sleep(0.5)

                                    # 查找包含选择支付方式的元素
                                    payment_method_element = d(textContains="选择支付方式")

                                    # 等待元素出现，最多等待 30 秒
                                    if payment_method_element.wait(timeout=30):
                                        # 如果元素存在，则点击该元素
                                        payment_method_element.click()
                                        print("成功点击包含选择支付方式的元素")
                                        time.sleep(0.5)
                                        # 查找文本为 ecard 的元素
                                        ecard_element = d(text="ecard")
                                        if ecard_element.wait(timeout=30):
                                            ecard_element.click()
                                            print("成功点击 ecard 元素")
                                            # 查找 id 为 btnqr 的元素
                                            time.sleep(2)
                                            btnqr_element = d(resourceId="btnqr")
                                            if btnqr_element.wait(timeout=30):
                                                btnqr_element.click()
                                                print("成功点击 id 为 btnqr 的元素")
                                            else:
                                                print("未找到 id 为 btnqr 的元素")
                                        else:
                                            print("未找到 ecard 元素")
                                    else:
                                        print("未找到包含选择支付方式的元素")
                        else:
                            print("在 30 秒内未找到名为支付的元素")
                            
                        
                    else:
                        print(f"在 30 秒内未找到包含日期{formatted_date}的元素")
                else:
                    print("在 30 秒内未找到立即预订按钮")
            else:
                print("在 30 秒内未找到球馆图标")
        else:
            print("在 30 秒内未找到体育场馆预约图标")
    else:
        print("未找到移动交通大学应用图标")

except Exception as e:
    print(f"出现错误: {e}")

finally:
    log_file.close()