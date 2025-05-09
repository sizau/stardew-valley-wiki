from Utilities import *


def category(name: str):
    ctg = get_more_data(name, "Category")
    if ctg == -81 or -23:
        return "Forage", "采集品"
    elif ctg == -79:
        return "Fruit", "水果"
    elif ctg == -80:
        return "Flower"
    else:
        return "-2147483648"


def get_season(seasons: list):
    desc = ""
    for s in seasons:
        desc = desc + "{{Season|" + s + "}} • "
    return desc[:-3]


def forage_info(info):
    info = info.split(",")
    ctg = category(info[0])
    price = get_more_data(info[0], "Price")
    color = ""
    if get_more_data(info[0], "ContextTags") is not None:
        color = get_more_data(info[0], "ContextTags")[0].split(" ")[1]
    print(f"""
{{{{Item {ctg[0]}
|eng        = {info[0]}
|source     = [[采集]]
|location   = 
|season     = {{{{Season|}}}}
|sellprice  = {price}
|edibility  = {get_more_data(info[0], "Edibility")}
|color      = {color}
|tag        = forage
}}}}

'''{info[1]}'''是一种[[SVE:{ctg[1]}|{ctg[1]}]]，
""")


if __name__ == "__main__":
    with open("Forageable/forageable.txt") as file:
        for obj_forage in file:
            forage_info(obj_forage)
