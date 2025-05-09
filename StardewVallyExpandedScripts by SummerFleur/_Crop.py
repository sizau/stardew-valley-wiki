from Utilities import *


def category(name: str):
    ctg = get_more_data(name, "Category")
    if ctg == -75:
        return "Crop", "蔬菜"
    elif ctg == -79:
        return "Fruit", "水果"
    else:
        return "-2147483648"


def divide_pic():
    for pic in PICS:
        img = Image.open(f"pic/{pic}")
        width = img.size[0]
        for t in range(int(width/16)):
            x = 16 * t
            roi = img.crop((x, 0, x + 16, 32))
            roi.save(f"pic/{pic[:-4]} Phase {t}.png")


def get_season(seasons: list):
    desc = ""
    for s in seasons:
        desc = desc + "{{Season|" + s + "}} • "
    return desc[:-3]


def crop_info(info):
    info = info.split(",")
    with open("Crop/Crop.json") as f:
        f = json.load(f)
    data = f.get(info[0])
    ctg = category(info[1])
    price = get_more_data(info[1], "Price")
    print(f"""
{{{{Item {ctg[0]}
|eng        = {info[1]}
|seed       = {{{{name|{info[0]}}}}}
|growth     = {sum(data.get("DaysInPhase"))} 天
|season     = {get_season(data.get("Seasons"))}
|sellprice  = {price}
|edibility  = {get_more_data(info[1], "Edibility")}
|color      = {get_more_data(info[1], "ContextTags")[0].split(" ")[1]}
|xp         = {xp(price)} [[耕种#经验值|耕种经验值]]
}}}}

'''{info[2]}'''是一种{ctg[1]}，由[[SVE:{info[3]}|{info[3]}]]生长 {sum(data.get("DaysInPhase"))} 天后成熟。""", end="")
    if data.get("RegrowDays") > 0:
        print(f"""成熟后，每 {data.get('RegrowDays')} 天可以收获一次。
        
== 生长阶段 ==

收获时，每株{info[2]}每 {data.get('RegrowDays')} 天可以收获 2 个{info[2]}，有 {data.get('ExtraHarvestChance'):.0%} 的机会额外收获 1 个{info[2]}。""")
    else:
        print("\n\n== 生长阶段 ==")

    return info[0]


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


def crop_info_foot():
    print("""
==导航==

{{NavBoxObj}}

[[Category:SVE 农作物]]
""")


if __name__ == "__main__":
    # divide_pic()
    with open("Crop/crop.txt") as file:
        for obj_crop in file:
            sd = crop_info(obj_crop)
            calendar(sd)
            crop_info_foot()
