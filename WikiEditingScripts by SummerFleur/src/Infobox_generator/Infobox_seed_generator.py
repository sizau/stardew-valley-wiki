from src.ShopService import *
from Recipes_helper import *


def generate_infobox() -> None:
    """生成 Infobox seed 并打印"""
    objects = game_data.objects_data
    shop_manager = ShopManager()

    parser.parse_all_recipes()
    recipes: list[readRecipes.Recipe] = parser.crafting_recipe_objects.values()

    for object_id, object_data in objects.items():
        item = Object(object_data)

        if item.get_field("Category") != -74:
            continue

        eng = item.name
        name = game_data.get_display_name(object_id)
        sellprice = item.sellprice

        crop, growth, season, xp = _search_crop(object_id)
        g_price, j_price, o_price, t_price, i_price, raccoon, nmday = _calc_price(object_id, shop_manager)
        artisan, source, recipe, ingredients, produces = _get_recipe_data(object_id, recipes)

        infobox = f"""{name}：\n
<onlyinclude>{{{{{{{{{{1|Infobox seed}}}}}}
|name           = {name}
|eng            = {eng}
|crop           = {crop}
|growth         = {growth}
|season         = {season}
|xp             = {xp}
|sellprice      = {sellprice}
|gPrice         = {g_price}
|jPrice         = {j_price}
|oPrice         = {o_price}
|tPrice         = {t_price}
|iPrice         = {i_price}
|nmday          = {nmday}
|raccoon        = {raccoon}
|otherprice     = ---------- 这里看情况要不要删除 ----------
|artisan        = {artisan}
|source         = {source}
|recipe         = {recipe}
|ingredients    = {ingredients}
|produces       = {produces}
}}}}</onlyinclude>
'''{name}'''是一种种子，播种并生长 {growth} 成熟后可以获得[[???]]。\n\n"""

        infobox = (infobox
                   .replace("|xp             = \n", "")
                   .replace("|oPrice         = \n", "")
                   .replace("|tPrice         = \n", "")
                   .replace("|iPrice         = \n", "")
                   .replace("|nmday          = \n", "")
                   .replace("|raccoon        = \n", "")
                   .replace("|artisan        = \n", "")
                   .replace("|source         = \n", "")
                   .replace("|recipe         = \n", "")
                   .replace("|ingredients    = \n", "")
                   .replace("|produces       = \n", ""))

        print(infobox)


def _search_crop(seed_id: str) -> tuple[str, str, str, str]:
    """
    检查游戏数据，尝试寻找该种子产出的物品、生长时间、生长季节、经验值
    :return: crop, growth, season, xp
    """
    crops = game_data.crops_data
    fruits = game_data.fruit_trees_data
    _tag = ""

    # 先判断作物列表中是否包含该种子
    if seed_id in crops.keys():
        crop = Crop(crops.get(seed_id))
        harvest_id = crop.harvest
        _tag = "c"
    # 再判断果树列表中是否包含该种子
    elif seed_id in fruits.keys():
        crop = FruitTree(fruits.get(seed_id))
        harvest_id = crop.harvest
        _tag = "f"
    # 这种情况对应混合种子等特殊的种子
    else:
        print("未找到当前种子对应的作物！")
        return "", "", "", ""

    # 作物的生长时间和经验
    if _tag == "c":
        harvest = game_data.try_get_object(harvest_id)
        growth = str(crop.growth) + " 天"
        sellprice = harvest.sellprice
        xp = f"{{{{Xp|{Crop.get_xp(sellprice)}|farm}}}}"
    # 果树的生长时间和经验（定死）
    elif _tag == "f":
        harvest = game_data.try_get_object(Object.trim(harvest_id))
        growth = "28 天"
        xp = ""
    # 好好反思你怎么触发这个的
    else:
        raise ValueError("unknown tag")

    harvest_crop = f"{{{{Name|{harvest.name}}}}}"
    season = crop.seasons

    return harvest_crop, growth, season, xp


def _calc_price(seed_id: str, shop_manager: ShopManager) -> tuple[str, str, str, str, str, str, str]:
    g_price, j_price, o_price, t_price, i_price, raccoon, nmday = "", "", "", "", "", "", ""

    # 尝试在皮埃尔杂货店寻找
    g_goods = shop_manager.seed_shop.try_get_goods(seed_id)
    if g_goods is not None:
        g_price = f"{{{{Price|{g_goods.price}}}}}"

    # 尝试在 Joja 超市寻找
    j_goods = shop_manager.joja_mart.try_get_goods(seed_id)
    if j_goods is not None:
        j_price = f"{{{{Price|{j_goods.price}}}}}"

    if game_data.namespace == "SVE":
        return g_price, j_price, o_price, t_price, i_price, raccoon, nmday

    # 尝试在绿洲商店寻找
    o_goods = shop_manager.oasis.try_get_goods(seed_id)
    if o_goods is not None:
        o_price = f"{{{{Price|{o_goods.price}}}}}"

    # 尝试在猪车寻找
    t_goods = shop_manager.traveler.try_get_goods(seed_id)
    if t_goods is not None:
        t_price = f"{{{{tprice|{t_goods.price}}}}}"

    # 尝试在姜岛商店寻找
    i_goods = shop_manager.island_trade.try_get_goods(seed_id)
    if i_goods is not None:
        item_name = game_data.get_name(Object.trim(i_goods.trade_item_id))
        i_price = f"{{{{Name|{item_name}|{i_goods.trade_item_amount}}}}}"

    # 尝试在浣熊商店寻找
    r_goods = shop_manager.raccoon_shop.try_get_goods(seed_id)
    if r_goods is not None:
        item_name = game_data.get_name(Object.trim(r_goods.trade_item_id))
        raccoon = f"{{{{Name|{item_name}|{r_goods.trade_item_amount}}}}}"

    # 尝试在夜市商店寻找
    day = 0
    n_goods1 = shop_manager.nmday1.try_get_goods(seed_id)
    n_goods2 = shop_manager.nmday2.try_get_goods(seed_id)
    n_goods3 = shop_manager.nmday3.try_get_goods(seed_id)
    for n_goods in (n_goods1, n_goods2, n_goods3):
        day = day + 1
        if n_goods is not None:
            if nmday == "":
                nmday += f"{day + 14}"
            else:
                nmday += f"和{day + 14}"

    return g_price, j_price, o_price, t_price, i_price, raccoon, nmday


def _get_recipe_data(seed_id: str, recipes: list[readRecipes.Recipe]) -> tuple[str, str, str, str, str]:
    artisan, source, recipe, ingredients, produces = "", "", "", "", ""
    if seed_id in ("431", "433"):
        artisan = "y"

    for craft_recipe in recipes:
        product: readRecipes.Item = craft_recipe.product
        if product.code == seed_id:
            source = "[[打造]]"
            recipe = "---------- 配方来源，这里要自己填 ----------"
            ingredients = item_list_to_string(craft_recipe.materials)
            produces = craft_recipe.product.count

    return artisan, source, recipe, ingredients, produces


if __name__ == "__main__":
    generate_infobox()
