import uiautomator2 as u2
from datetime import datetime, timedelta
import time
import random
import os
import base64
import requests
import numpy as np

# 创建日志和输出目录
os.makedirs('debug', exist_ok=True)
log_file = open('debug/verification_log.txt', 'a')


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
    # 降低随机抖动频率，固定分割时间，提高运行效率
    """改进的滑动算法：包含加速度和随机抖动"""
    control1 = (random.randint(20, 40), random.randint(-10, 10))
    control2 = (random.randint(60, 80), random.randint(-10, 10))

    # 进一步减少点数
    points = []
    for t in np.linspace(0, 1, 9):
        x = (1 - t) ** 3 * start_x + 3 * (1 - t) ** 2 * t * (start_x + control1[0]) + 3 * (1 - t) * t ** 2 * (
                end_x - control2[0]) + t ** 3 * end_x
        y = (1 - t) ** 3 * start_y + 3 * (1 - t) ** 2 * t * (start_y + control1[1]) + 3 * (1 - t) * t ** 2 * (
                end_y - control2[1]) + t ** 3 * end_y
        points.append((int(x), int(y)))

    d.touch.down(start_x, start_y)

    last_point = points[0]
    # 进一步减小时间间隔以提高速度
    interval = 0.002
    for point in points[1:]:
        # 减少随机抖动
        offset_x = 0
        offset_y = 0
        current_x = point[0] + offset_x
        current_y = point[1] + offset_y

        d.touch.move(current_x, current_y)
        time.sleep(interval)
        last_point = point

    for _ in range(1):  # 减少结尾的随机抖动次数
        d.touch.move(end_x, end_y)
        time.sleep(interval)

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

        if not all([bg_element.exists, slider_element.exists, slider_img_element.exists]):
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


# 连接设备
d = u2.connect('127.0.0.1:5555')
log("成功连接模拟器")

# 处理验证
if handle_slider_verification_v2(d):
    log("成功通过滑块验证")
else:
    log("验证流程失败")

log_file.close()