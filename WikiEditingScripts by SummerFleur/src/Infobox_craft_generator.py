from Infobox_helper import *


def generate_infobox(p: readRecipes.RecipeParser) -> None:
    """生成 Infobox craft 并打印"""
    p.parse_all_recipes()
    recipes = p.crafting_recipe_objects

    for recipe_name, recipe_info in recipes.items():
        eng = recipe_name
        name = recipe_info.product.displayName
        sellprice = get_specific_attribute(recipe_info.product.code, "Price")
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
        print(infobox)


if __name__ == "__main__":
    generate_infobox(parser)
