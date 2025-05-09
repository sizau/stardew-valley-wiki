import os
import json
import math
from PIL import Image, ImageDraw

PICS = os.listdir("pic")


def pngs2gif() -> None:
    """
    遍历 pic 文件夹内的所有图片，生成 gif 动图。
    """
    frames = []
    for frame in PICS:
        frame = Image.open(f"pic/{frame}")
        frames.append(frame)
        frames[0].save("pic/output.gif", save_all=True, append_images=frames[1:], loop=0, disposal=2,
                       transparency=0, duration=300, )


def resize_pic(scale: float = 3.0) -> None:
    """
    :param scale: 缩放比例
    遍历 pic 文件夹内的所有图片，使用硬边缘缩放图片尺寸，使像素图片更适合用于显示，默认缩放比例为 3.0
    """
    for pic in PICS:
        image = Image.open(f"pic/{pic}")
        original_size = image.size
        new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
        resized_image = image.resize(new_size, Image.NEAREST)
        resized_image.save(f"pic/{pic}")


def divide_pic():
    for pic in PICS:
        img = Image.open(f"pic/{pic}")
        roi = img.crop((0, 48, 48, 96))
        roi.save(f"pic/{pic}")


def add_mask(path, regions, name):
    for i in range(len(regions)):
        regions[i][0] = regions[i][0] * 16 + 1
        regions[i][1] = regions[i][1] * 16 + 1
        regions[i][2] = (regions[i][2] + 1) * 16
        regions[i][3] = (regions[i][3] + 1) * 16
        regions[i] = tuple(regions[i])
    size = Image.open(path).size
    image = Image.new("RGB", size)
    draw = ImageDraw.Draw(image)
    for reg in regions:
        print(reg)
        draw.rectangle(reg, fill=(255, 255, 255))
    image.save(name)


def get_ingredients(ing: str) -> None:
    with open("itemID.json") as o:
        o = json.load(o)
        if o.get(ing) is not None:
            print(o.get(ing))


def text_replace(file):
    with open("replace.json") as r:
        rep = json.load(r)
        with open(file) as f:
            file_mod = file.split(".")[0]
            with open(f"{file_mod}_mod.txt", "w") as mf:
                f = f.read()
                rep_key = list(rep.keys())
                for key in rep_key:
                    f = f.replace(key, rep.get(key))
                mf.write(f)
                mf.close()


def get_more_data(item_name, attr, json_file='metadata.json'):
    with open(json_file) as f:
        data = json.load(f)
        if item_name in data:
            return data[item_name].get(attr)
        else:
            return "-2147483648"


def xp(sprice):
    sprice = int(sprice)
    exp = 16 * math.log(0.018 * sprice + 1)
    exp = round(exp, 0)
    return int(exp)


def load_edibility():
    with open("Objects.json") as f:
        data = json.load(f)
        data_keys = list(data.keys())
    for item in data_keys:
        edibility = get_more_data(item, "Edibility", "Objects.json")
        if 70 <= edibility < 75:
            get_ingredients(item)
            print(f',{edibility}')


if __name__ == "__main__":
    # region = [[177,67,181,70], [192,30,196,34], [219,44,223,48], [134,128,140,134], [143,83,149,88], [164,40,169,45], [101,100,112,107], [112,146,121,154], [114,56,119,61], [214,120,218,123], [198,50,201,52], [73,72,79,77], [190,97,193,99], [44,85,49,91], [77,118,86,125], [25,66,30,69], [89,21,97,26], [124,32,127,35], [61,106,65,110], [89,141,92,146], [65,132,68,135], [36,107,40,112]]
    # add_mask(r"Locations\Crimson Badlands\Crimson Badlands.png", region, "Scrop Spawn 1.png")

    for i in [403,395,253,227,194,195,229,216,211,244,196,265,728,210,730]:
        i = str(i)
        get_ingredients(i)

    # load_edibility()

    # print(xp(120))
