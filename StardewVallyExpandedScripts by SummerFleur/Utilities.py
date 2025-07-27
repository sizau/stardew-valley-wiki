import os
import json
from PIL import Image

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


if __name__ == "__main__":
    ...
