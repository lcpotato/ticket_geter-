import uiautomator2 as u2
import xml.etree.ElementTree as ET


def get_xpath(element, root):
    """
    计算元素的 xpath
    :param element: 元素对象
    :param root: XML 根元素
    :return: 元素的 xpath 字符串
    """
    components = []
    current = element
    while current is not None and current is not root:
        index = 1
        parent = current.find('..')
        if parent is not None:
            for sibling in parent.findall(current.tag):
                if sibling is current:
                    break
                index += 1
        tag = current.tag
        if index > 1:
            tag += f"[{index}]"
        components.insert(0, tag)
        current = parent
    if current is root:
        components.insert(0, root.tag)
    return '/' + '/'.join(components)


# 连接到设备
try:
    d = u2.connect('127.0.0.1:5555')
    print("成功连接到设备")
except Exception as e:
    print(f"连接设备时出错: {e}")
    exit(1)

# 打开文件以写入信息
with open('element_info.txt', 'w', encoding='utf-8') as f:
    # 获取当前界面的 XML 层次结构
    xml_str = d.dump_hierarchy()
    # 解析 XML 字符串
    root = ET.fromstring(xml_str)
    # 获取所有元素
    elements = root.findall('.//*')

    for element in elements:
        # 获取元素的属性
        element_id = element.get('resource-id')
        element_text = element.get('text')
        element_class = element.get('class')
        element_xpath = get_xpath(element, root)

        # 写入元素信息到文件
        f.write("元素信息:\n")
        if element_id:
            f.write(f"  ID: {element_id}\n")
        if element_text:
            f.write(f"  文本: {element_text}\n")
        if element_class:
            f.write(f"  类名: {element_class}\n")
        if element_xpath:
            f.write(f"  XPath: {element_xpath}\n")
        f.write("\n")

print("元素信息已保存到 element_info.txt 文件中")