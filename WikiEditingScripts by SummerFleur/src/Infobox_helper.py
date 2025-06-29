import readRecipes

parser = readRecipes.RecipeParser()


def item_list_to_string(il: list[readRecipes.Item]) -> str:
    out_string = ""
    for item in il:
        out_string += f"{{{{Name|{item.name}|{item.count}}}}}"
    return out_string


def get_specific_attribute(code: str, attr: str) -> str | None:
    """使用物品 ID 名获取更多信息"""
    all_object_data = parser.objects_data
    if code in all_object_data.keys():
        value = all_object_data[code].get(attr)
        return value

    return ""
