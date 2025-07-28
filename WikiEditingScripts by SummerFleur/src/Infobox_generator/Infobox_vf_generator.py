from src.ItemService import *


def generate_infobox(d: GameData, category: str) -> None:
    """生成 Infobox vegetable/fruit 并打印"""
    objects = d.objects_data

    for object_id, object_data in objects.items():
        item = Item(object_data)

        match item.get_field("Category"):
            case -75 if category == "vegetable":
                _category = "vegetable"
            case -79 if category == "fruit":
                _category = "fruit"
            case -80 if category == "flower":
                _category = "flower"
            case -81 if category == "forage":
                _category = "forage"
            case _:
                continue

        eng = item.name
        name = ""
        match d.namespace:
            case "SVE":
                name = Item.get_display_name_sve(object_id, d)
                _category += "/SVE"
            case "Vanilla":
                name = Item.get_display_name(object_id, d)
        sellprice = item.sellprice
        edibility = item.edibility
        color = item.color
        xp = Crop.get_xp(sellprice)

        source, seed, growth, season, tag = _search_crop(d, category, object_id, item, name)

        infobox = f"""{name}：\n
<onlyinclude>{{{{{{{{{{1|Infobox {_category}}}}}}}
|name        = {name}
|eng         = {eng}
|source      = {source}
|seed        = {seed}
|growth      = {growth}
|season      = {season}"""

        if tag == "":
            infobox = infobox + f"""
|xp          = {{{{Xp|{xp}|farm}}}}"""
        elif tag == "Forage":
            if len(season) > 1 and season[1] == '季':
                infobox = infobox + f"""
|xp          = <nowiki />
*{season}种子：{{Xp|3|采集}}与 {{Xp|2|耕种}}
*采集：{{Xp|7|采集}}"""
            else:
                infobox = infobox + f"""
|xp          = {{{{Xp|7|forage}}}}"""

        infobox = infobox + f"""
|sellprice   = {sellprice}
|edibility   = {edibility}
|color       = {color}
|tag         = {tag}
}}}}</onlyinclude>\n\n"""

        if category == "forage":
            infobox.replace("|seed        = \n|growth      = {growth}\n", "")

        print(infobox)


def _search_crop(d: GameData, category: str, object_id: str, item: Item, name: str) -> tuple[str, str, str, str, str]:
    """
    :return: source, seed, growth, season, tag
    """
    crops = d.crops_data
    trees = d.fruit_trees_data

    # 先检查作物列表
    if category != "forage":
        for seed_id, crop_data in crops.items():
            crop = Crop(crop_data)
            if crop.harvest == object_id and seed_id not in ["495", "496", "497", "498"]:
                seed = Item.get_name(seed_id, d)
                seed = f"{{{{Name|{seed}}}}}"
                growth = str(crop.growth) + " 天"
                season = crop.seasons
                source = "[[耕种]]"
                return source, seed, growth, season, ""

    # 然后检查果树列表
    if category == "fruit":
        for seed_id, tree_data in trees.items():
            tree = FruitTree(tree_data)
            if tree.harvest == object_id or tree.harvest == "(O)" + object_id:
                seed = Item.get_name(seed_id, d)
                seed = f"{{{{Name|{seed}}}}}"
                growth = "28 天"
                season = tree.seasons
                source = f"[[{name}树]]"
                if object_id not in ["91", "834"]:
                    source += " • [[山洞#果蝠|山洞（果蝠）]]"
                return source, seed, growth, season, "Tree"

    # 再检查野生种子
    if category != "vegetable":
        match object_id:
            case "16" | "20" | "22":
                return "[[采集]] • [[春季种子]]", "", "", "春季", "Vegetable"
            case "18":
                return "[[采集]] • [[春季种子]]", "", "", "春季", ""
            case "396" | "402":
                return "[[采集]] • [[夏季种子]]", "", "", "夏季", "Forage"
            case "404":
                return "[[采集]] • [[秋季种子]]", "", "", "秋季", "Mushroom"
            case "408":
                return "[[采集]] • [[秋季种子]]", "", "", "秋季", "Vegetable"
            case "406" | "410":
                return "[[采集]] • [[秋季种子]]", "", "", "秋季", "Forage"
            case "412" | "416":
                return "[[采集]] • [[冬季种子]]", "", "", "冬季", "Vegetable"
            case "414" | "418":
                return "[[采集]] • [[冬季种子]]", "", "", "冬季", "Forage"

    tag = "Forage"
    if category == "forage":
        if "edible_mushroom" in item.get_field("ContextTags"):
            tag = "Mushroom"
        elif item.edibility > 0:
            tag = "Vegetable"
        else:
            tag = ""

    if category != "forage":
        print(f"未能找到 {name} 的种子！标记为采集品。")
    return "[[采集]]", "", "", "", tag


if __name__ == "__main__":
    data = GameData()
    match data.namespace:
        case "SVE":
            data.read_json_files_sve()
        case "Vanilla":
            data.read_json_files()
    if data.objects_data == {}:
        raise ValueError("不合法的命名空间！")

    print("-------------------- 蔬菜 --------------------\n")
    generate_infobox(data, category="vegetable")
    print("")
    print("-------------------- 水果 --------------------\n")
    generate_infobox(data, category="fruit")
    print("")
    print("-------------------- 花 --------------------\n")
    generate_infobox(data, category="flower")
    print("")
    print("-------------------- 采集品 --------------------\n")
    generate_infobox(data, category="forage")
