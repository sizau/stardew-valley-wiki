from src.ItemService import *


def generate_infobox(d: GameData, category: str) -> None:
    """生成 Infobox vegetable/fruit 并打印"""
    d.read_json_files()
    objects = d.objects_data
    crops = d.crops_data

    for object_id, object_data in objects.items():
        item = Item(object_data)

        match item.get_field("Category"):
            case -75 if category == "vegetable":
                _category = "vegetable"
            case -79 if category == "fruit":
                _category = "fruit"
            case _:
                continue

        eng = item.name
        name = Item.get_display_name(object_id, d)
        sellprice = item.sellprice
        edibility = item.edibility
        color = item.color
        xp = Crop.get_xp(sellprice)
        source = ""

        found_seed = False
        seed, growth, season = "", "", ""

        for seed_id, crop_data in crops.items():
            crop = Crop(crop_data)
            if crop.harvest == object_id:
                found_seed = True
                seed = Item.get_name(seed_id, d)
                seed = f"{{{{Name|{seed}}}}}"
                growth = str(crop.growth) + " 天"
                season = crop.seasons
                source = "[[耕种]]"
                break

        if not found_seed:
            print(f"未能找到 {name} 的种子！")

        infobox = f"""{name}：\n
<onlyinclude>{{{{{{{{{{1|Infobox {_category}}}}}}}
|name        = {name}
|eng         = {eng}
|source      = {source}
|seed        = {seed}
|growth      = {growth}
|season      = {season}"""

        if found_seed:
            infobox = infobox + f"""
|xp          = {{{{Xp|{xp}|farm}}}}"""
        else:
            infobox = infobox + f"""
|xp          = {{{{Xp|7|forage}}}} <!-- 这里可能是错的，请仔细检查，编辑时记得把这段话删了 -->"""

        infobox = infobox + f"""
|sellprice   = {sellprice}
|edibility   = {edibility}
|color       = {color}
}}}}</onlyinclude>\n\n"""

        print(infobox)


if __name__ == "__main__":
    data = GameData()
    data.read_json_files()
    generate_infobox(data, category="vegetable")
