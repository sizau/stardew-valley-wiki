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


def get_ingredients(dish: str):
    ingredients = ''
    with open("itemID.json") as o:
        o = json.load(o)
        with open("Dish/dish.json") as f:
            data = json.load(f).get(dish)
            ings = data.split("/")[0].split(" ")
            ing_num = int(len(ings) / 2)
            for i in range(ing_num):
                if o.get(ings[2 * i]) is not None:
                    oo = o.get(ings[2 * i])
                else:
                    oo = ings[2 * i][37:].replace("_", " ")
                ing = f"{{{{Name|{oo}|{ings[2 * i + 1]}}}}}"
                ingredients = ingredients + ing
    return ingredients


def get_buff(buffs):
    if buffs is None:
        return
    buffs = buffs[0].get("CustomAttributes")
    custom_buff_order = ["FarmingLevel", "ForagingLevel", "FishingLevel", "MiningLevel", "LuckLevel",
                         "MaxStamina", "MagneticRadius", "Speed", "Defense", "Attack"]
    BUFFs = ''
    for buff in custom_buff_order:
        if buffs.get(buff) != 0:
            lv = buffs.get(buff)
            if "Level" in buff:
                buff = buff[:-5]
            BUFFs = BUFFs + f"{{{{Name|{buff}|+{lv}}}}}"
    return BUFFs


def dish_info(eng, zh):
    print(f"""
<onlyinclude>{{{{{{{{{{1|Item cooking}}}}}}
|name            = {zh}
|image           = {eng}.png
|description     = {{{{Description|{eng}}}}}
|buff            = get_buff(get_more_data(eng, "Buffs"))
|duration        = 
|dsvduration     = 
|sellprice       = get_more_data(eng, "Price")
|recipe          = 
|ingredients     = {get_ingredients(eng)}
|edibility       = get_more_data(eng, "Edibility")
}}}}</onlyinclude>

{{{{Quote|quote = “{{{{Description|{eng}}}}}”}}}}

'''{zh}'''是一道[[SVE:菜肴|菜肴]]，可通过升级后的[[农舍]]内的厨房或[[野炊工具]]制作。
""")


def calendar(seed):
    with open("Crop/Crop.json") as f:
        f = json.load(f)
    info = f.get(seed)
    day = len(info.get("DaysInPhase"))
    crop = seed.replace(" Seed", "")
    if info.get("RegrowDays") > 0:
        print('{|class="wikitable roundedborder" style="text-align: center;"')
        for i in range(day):
            print(f'!阶段 {i + 1}')
        print('!colspan="2"|收成\n|-')
        for i in range(day + 2):
            print(f'|[[File:{crop} Phase {i + 1}.png|center|link=]]')
        print('|-')
        for i in info.get("DaysInPhase"):
            print(f'|{i} 天')
        print(f'|共：{sum(info.get("DaysInPhase"))} 天')
        print(f'|每 {info.get("RegrowDays")} 天继续生产')
        print('|-\n|}')
    else:
        print('{|class="wikitable roundedborder" style="text-align: center;"')
        for i in range(day):
            print(f'!阶段 {i + 1}')
        print('!收成\n|-')
        for i in range(day + 1):
            print(f'|[[File:{crop} Phase {i + 1}.png|center|link=]]')
        print('|-')
        for i in info.get("DaysInPhase"):
            print(f'|{i} 天')
        print(f'|共：{sum(info.get("DaysInPhase"))} 天')
        print('|-\n|}')


def character_dialogue(name):
    with open(f"Characters/{name}/Dialogue.json") as f:
        f = json.load(f)
    with open("zh.json") as zh:
        zh = json.load(zh)
    with open("en.json") as en:
        en = json.load(en)

    f_keys = f.keys()
    for desc in f_keys:
        ID = f.get(desc)
        ID = ID.replace("{{", "").replace("}}", "").replace("i18n:", "")
        print(f"//{desc}")
        print(f'"{ID}": \n{en.get(ID)}\n')


if __name__ == "__main__":
    ...
