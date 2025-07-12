import uiautomator2 as u2
from PIL import Image

# 连接到安卓模拟器，这里假设模拟器 IP 为 127.0.0.1，端口为 5555
d = u2.connect('127.0.0.1:5555')

# 查找元素
slider_img = d.xpath('//android.widget.Image[@resource-id="slider-img"]')
slider_move_btn = d.xpath('//android.view.View[@resource-id="slider-move-btn"]')
bg_img = d.xpath('//android.widget.Image[@resource-id="bg-img"]')


def save_element_image(element, element_name):
    if element.exists:
        # 获取元素的边界信息
        bounds = element.info['bounds']
        # 截取当前屏幕，默认返回 PIL 图像对象
        img = d.screenshot()
        # 裁剪出元素对应的区域
        cropped_img = img.crop((bounds['left'], bounds['top'], bounds['right'], bounds['bottom']))
        # 保存裁剪后的图片
        cropped_img.save(f'{element_name}.png')
        print(f"成功保存 '{element_name}' 元素的图片")
    else:
        print(f"未找到 '{element_name}' 元素，无法保存图片")


# 保存各元素对应的图片
save_element_image(slider_img, 'slider-img')
save_element_image(slider_move_btn, 'slider-move-btn')
save_element_image(bg_img, 'bg-img')

# 尝试移动滑块按钮
if slider_move_btn.exists:
    # 获取滑块按钮的中心位置
    bounds = slider_move_btn.info['bounds']
    center_x = (bounds['left'] + bounds['right']) // 2
    center_y = (bounds['top'] + bounds['bottom']) // 2

    # 定义滑动的目标位置（横向移动 20 个像素）
    target_x = center_x + 20
    target_y = center_y

    # 执行滑动操作
    d.swipe(center_x, center_y, target_x, target_y, duration=0.5)
    print("成功滑动滑块按钮 20 个像素")
else:
    print("未找到 'slider-move-btn' 元素，无法进行滑动操作")