from Utilities import *


def get_ingredients(dish: str):
    ingredients = ''
    with open("itemID.json") as o:
        o = json.load(o)
        with open("Dish/dish.json") as f:
            data = json.load(f).get(dish)
            ings = data.split("/")[0].split(" ")
            ing_num = int(len(ings) / 2)
            for i in range(ing_num):
                if o.get(ings[2*i]) is not None:
                    oo = o.get(ings[2*i])
                else:
                    oo = ings[2*i][37:].replace("_", " ")
                ing = f"{{{{Name|{oo}|{ings[2*i+1]}}}}}"
                ingredients = ingredients + ing
    return ingredients    


def get_buff(buffs):
    if buffs is None:
        return
    buffs = buffs[0].get("CustomAttributes")
    custom_buff_order = ["FarmingLevel", "ForagingLevel", "FishingLevel", "MiningLevel", "LuckLevel", 
                         "MaxStamina",  "MagneticRadius", "Speed", "Defense", "Attack"]
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
|buff            = {get_buff(get_more_data(eng, "Buffs"))}
|duration        = 
|dsvduration     = 
|sellprice       = {get_more_data(eng, "Price")}
|recipe          = 
|ingredients     = {get_ingredients(eng)}
|edibility       = {get_more_data(eng, "Edibility")}
}}}}</onlyinclude>

{{{{Quote|quote = “{{{{Description|{eng}}}}}”}}}}

'''{zh}'''是一道[[SVE:菜肴|菜肴]]，可通过升级后的[[农舍]]内的厨房或[[野炊工具]]制作。
""")
    
    
def dish_info_foot():
    print("""
==导航==

{{NavBoxObj}}
                  
[[Category:SVE 食物]]
""")
    
    
if __name__ == "__main__":
    with open("Dish/dish.txt") as file:
        for obj_dish in file:
            info = obj_dish.split(",")
            dish_info(info[0], info[1])
            dish_info_foot()
