import json

from Utilities import *


def sort_pics():
    files = os.listdir("pic")
    fish_name = []
    with open("data.txt") as f:
        for zh in f:
            fish_name.append(zh.split("/")[0] + ".png")
    for pic in files:
        if pic not in fish_name:
            os.remove(f"pic/{pic}")


def get_clock(timerange: str):
    if timerange == "600 2600":
        return "全天"
    time = []
    timerange = timerange.split(" ")
    for t in timerange:
        t = int(int(t) / 100)
        if t < 12:
            time.append(f"上午 {t}:00")
        elif t == 12:
            time.append("中午 12:00")
        elif 12 < t < 20:
            time.append(f"下午 {t%12}:00")
        elif 20 <= t < 26:
            time.append(f"晚上 {t%12}:00")
        else:
            time.append("凌晨 2:00")
    return f"{time[0]} 至{time[1]}"


def get_off_dur(timerange: str):
    if timerange == "600 2600":
        return 0, 20
    timerange = timerange.split(" ")
    offset = int(int(timerange[0]) / 100) - 6
    duration = int(int(timerange[1]) / 100) - int(int(timerange[0]) / 100)
    return offset, duration


def get_season(seasons: str):
    if seasons == "spring summer fall winter":
        return "all"
    seasons = seasons.split(" ")
    desc = ""
    for s in seasons:
        desc = desc + "{{Season|" + s + "}} • "
    return desc[:-3]
            
            
def fl(value):
    if value != "0":
        return value
    else:
        return ' '
    
    
def fish_xp(value):
    return int(value/3) + 3


def bhv(value):
    if value == "floater":
        return "漂浮型"
    elif value == "sinker":
        return "下坠型"
    elif value == "mixed":
        return "混合型"
    elif value == "dart":
        return "猛冲型"


def fish_info(eng):
    with open("Fish/fish.json") as f:
        f = json.load(f)
    info = f.get(eng).split("/")
    print(f"""
{{{{Item fish
|name       = {info[-2]}
|eng        = {info[0]}
|location   = 
|time       = {get_clock(info[5])}
|season     = {get_season(info[6])}
|weather    = {info[7]}
|difficulty = {info[1]}
|behavior   = {info[2]}
|size       = {info[3]}-{int(info[4])+1}
|price      = {get_more_data(info[0], "Price")}
|fl         = {fl(info[-4])}
|edibility  = {get_more_data(info[0], "Edibility")}
|roe        = {info[-1]}
}}}}

{info[-2]}是一种[[SVE:鱼|鱼]]，when，where。
""")
    return info[-2]


def fish_info_foot():
    print("""
==鱼塘==
{{SVE 鱼塘}}

==导航==

{{NavBoxObj}}

[[Category:SVE:鱼]]
""")
    
    
def fish_table_head():
    print("""
{|class="wikitable sortable roundedborder"
! class="unsortable" |  图片
! 名称
! style="min-width: 70px;"|描述
! 价格
! [[File:Fisher.png|24px|link=]]渔夫职业（+25%）
! [[File:Angler Icon.png|24px|link=]]垂钓者职业（+50%）
! style="min-width: 70px;"|位置
! 时间
! 季节
! 天气
! 尺寸（厘米）
! 难度和行为
! 基础经验
! 用途
""")
    
    
def fish_table(eng):
    with open("Fish/fish.json") as f:
        f = json.load(f)
    info = f.get(eng).split("/")
    print(f"""|-
<section begin="{info[0]}" />
| [[File:{info[0]}.png|center|48px|]]
| [[SVE:{info[-2]}|{info[-2]}]]
| {{{{Description|{info[0]}}}}}
| {{{{Qualityprice|{info[0]}|200}}}}
| {{{{Qualityprice|{info[0]}|200|pm=1.25}}}}
| {{{{Qualityprice|{info[0]}|200|pm=1.5}}}}
| location
| {get_clock(info[5])}
| class="no-wrap"| Season
| class="no-wrap"|{{{{Weather inline|{info[7]}}}}}
| {int(round(int(info[3])*2.54, 0))}~{int(round((int(info[4])+1)*2.54, 0))}
| class="no-wrap"|{info[1]} {bhv(info[2])}
| {fish_xp(int(info[1]))}
|  <section end="{info[0]}" />""")


def fish_location_table(location_name, fish_name, areas=None):
    with open(f"Locations/{location_name}/fish.json") as l:
        l = json.load(l)
    with open("Fish/fish.json") as f:
        f = json.load(f)
    for season in ["Spring", "Summer", "Fall", "Winter"]:
        print(f"{{{{FishLocationHeader|{season}}}}}")
        if areas is None:
            for eng in fish_name:
                fld = l.get(eng)
                info = f.get(eng).split("/")
                if season in fld[1]:
                    print(f"""{{{{FishLocationEntry
|      fish = {eng}
|    season = {season}
|   weather = {info[7]}
|    offset = {get_off_dur(info[5])[0]}
|    length = {get_off_dur(info[5])[1]}
| timeofday = 
}}}}""")
        else:
            for area in areas:
                print(f"=== {area} ===")
                for eng in fish_name:
                    fld = l.get(eng)
                    info = f.get(eng).split("/")
                    if season in fld[1] and area in fld[0]:
                        print(f"""{{{{FishLocationEntry
|      fish = {eng}
|    season = {season}
|   weather = {info[7]}
|    offset = {get_off_dur(info[5])[0]}
|    length = {get_off_dur(info[5])[1]}
| timeofday = 
}}}}""")
    
    
if __name__ == "__main__":
    # with open("Fish/fish.txt") as file:
    #     for obj_fish in file:
    #         fish = obj_fish.split(",")
    #         fs = fish_info(fish[0])
    #         get_gift_tastes("Fish", fs)
    #         fish_info_foot()

    # with open("Fish/fish.txt") as file:
    #     fish_table_head()
    #     for obj_fish in file:
    #         fish = obj_fish.split(",")
    #         fish_table(fish[0])

    fish_location_table("highlands", ["Bull Trout", "Highlands Bass", "Fiber Goby", "Largemouth Bass", "Rainbow Trout", "Walleye", "Perch", "Carp", "Green Algae", "Midnight Carp", "Sturgeon", "Bullhead", "Chub", "Lingcod", "Goldfish"], ["River", "Pond"])
