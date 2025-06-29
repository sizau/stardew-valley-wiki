import src.readRecipes as readRecipes


def read_craft_recipes(p: readRecipes.RecipeParser) -> dict[str, dict[str, str]]:
    """读取配方文件，解析物品代码和数量，返回制造配方"""
    crafting_recipes = {}

    # 解析制造配方
    for recipe_name, recipe_string in p.crafting_recipes.items():
        parts = recipe_string.split("/")
        if len(parts) >= 4:
            materials = ""
            material_parts = parts[0].split()

            # 先解析制造原料及其数量
            for i in range(0, len(material_parts), 2):
                if i + 1 < len(material_parts):
                    code = material_parts[i]
                    item_name = get_specific_attribute(p, code, "Name")
                    quantity = int(material_parts[i + 1])
                    wiki_format = f"{{{{Name|{item_name}|{quantity}}}}}"
                    materials += wiki_format

            # 然后获取制造得到的物品数量
            product_parts = parts[2].split()
            product_code = product_parts[0]
            product_quantity = int(product_parts[1]) if len(product_parts) > 1 else 1

            crafting_recipes[recipe_name] = {
                "code": product_code,
                "materials": materials,
                "quantity": product_quantity,
            }

    print(f"成功解析 {len(crafting_recipes)} 个制造配方")
    return crafting_recipes


def get_specific_attribute(p: readRecipes.RecipeParser, code: str, attr: str) -> str | None:
    """使用物品 ID 名获取更多信息"""
    all_object_data = p.objects_data
    if code in all_object_data.keys():
        value = all_object_data[code].get(attr)
        return value

    return None


def eng_2_chn(p: readRecipes.RecipeParser, eng: str) -> str | None:
    """将英文名转化为中文名"""
    eng = eng.replace(" ", "") + "_Name"
    eng = eng.lower()
    for object_name, object_data in p.objects_zh_cn.items():
        if eng == object_name.lower():
            return object_data

    return None


def item_list_to_string(il: list[readRecipes.Item]) -> str:
    out_string = ""
    for item in il:
        out_string += f"{{{{Name|{item.name}|{item.count}}}}}"
    return out_string


def generate_infobox(p: readRecipes.RecipeParser) -> None:
    """生成 Infobox craft 并打印"""
    recipes = p.parse_all_recipes()

    for recipe_name, recipe_info in recipes.items():
        eng = recipe_name
        name = recipe_info.product.displayName
        sellprice = get_specific_attribute(p, recipe_info.product.code, "Price")
        produces = recipe_info.product.count if int(recipe_info.product.count) > 1 else ""
        ingredients = item_list_to_string(recipe_info.materials)

        infobox = f"""{name}：\n
<onlyinclude>{{{{{{{{{{1|Infobox craft}}}}}}
|name            = {name}
|eng             = {eng}
|description     = {{{{Description|{eng}}}}}
|source          = [[打造]]
|sellprice       = {sellprice}
|recipe          = 这里要自己填
|ingredients     = {ingredients}
|produces        = {produces}
}}}}</onlyinclude>
'''{name}'''是一种[[打造|打造物品]]，\n"""
        infobox = infobox.replace("|sellprice       = None\n", "")
        print(infobox)


if __name__ == "__main__":
    parser = readRecipes.RecipeParser()
    generate_infobox(parser)
