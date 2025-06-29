from pathlib import Path

from utils import FileUtils


def main() -> None:
  pending_json_path = Path(__file__).parent.parent / "json"
  output_path = Path(__file__).parent.parent / "output" / "json"
  pending_json_keywords: list[str] = [
    "Achievements",
    "Boots",
    "Bundles",
    "ChairTiles",
    "CookingRecipes",
    "CraftingRecipes",
    "Fish",
    "Furniture",
    "HairData",
    "hats",
    "Monsters",
    "NPCGiftTastes",
    "PaintData",
    "Quests",
  ]  # 需要解析的文件名称
  for json_path in pending_json_path.glob("*.json"):  # 读取项目目录下json文件夹中的所有json文件
    if any(keyword.lower() in json_path.name.lower() for keyword in pending_json_keywords):
      output_data: dict = {}  # 初始化输出文件
      data: dict = FileUtils.read_json(json_path)  # 符合关键词就读取
      print(f"正在解析{json_path.name}文件")

      # 开始按照文件名称分别解析为标准json格式
      if "Achievements".lower() in json_path.name.lower():  # 成就
        # "成就编号":"成就名称/成就描述/是否默认显示/前置成就编号/解锁帽子索引"
        for key, value in data.items():
          v_parts: list[str] = value.split("^")
          output_data[key] = {
            "Name": v_parts[0],
            "Description": v_parts[1],
            "Display": False if v_parts[2].lower() == "false" else True,
            "PrerequisiteAchievementId": int(v_parts[3]),
            "UnlockHatIndex(Unused)": int(v_parts[4]),
            "Texture": "LooseSprite\\Cursors",
          }
        FileUtils.write_json(output_data, output_path / "Achievements_new.json")
        print("已保存到./output/json/Achievements_new.json.json")

      elif "Boots".lower() in json_path.name.lower():  # 鞋子
        # "鞋子编号":"鞋子名称/鞋子描述/出售价格/防御值/免疫值/行走图颜色索引/显示名称"
        for key, value in data.items():
          v_parts: list[str] = value.split("/")
          output_data[key] = {
            "Name": v_parts[0],
            "DisplayName": v_parts[6],
            "Description": v_parts[1],
            "Price(Unused)": int(v_parts[2]),
            "Defense": int(v_parts[3]),
            "Immunity": int(v_parts[4]),
            "CharacterColorIndex": int(v_parts[5]),
            "SpriteIndex": int(key),
            "Texture": "Maps\\springobjects",
          }
        FileUtils.write_json(output_data, output_path / "Boots_new.json")
        print("已保存到./output/json/Boots_new.json")

      elif "Bundles".lower() in json_path.name.lower():  # 收集包
        # "房间名称/收集包贴图索引":"收集包名称/奖励类型 奖励代码 奖励数量/需求代码1 需求数量1 需求最小品质1 .../收集包颜色索引/需求数量/总数选取数量（混合献祭用）/显示名称"
        for key, value in data.items():
          k_parts: list[str] = key.split("/")
          area_name, sprite_index = k_parts[0], k_parts[1]
          if area_name not in output_data:
            output_data[area_name] = {"AreaName": area_name, "Bundles": []}
          v_parts: list[str] = value.split("/")
          reward = None
          if v_parts[1] != "":
            r_parts: list[str] = v_parts[1].split()
            reward = {
              "Type": r_parts[0],
              "Item": r_parts[1],
              "Count": int(r_parts[2]),
            }
          requirements: list[str] = v_parts[2].split()
          items: list[dict] = [
            {"Item": id, "Count": int(count), "MinQuality": int(quality)}
            for id, count, quality in zip(requirements[0::3], requirements[1::3], requirements[2::3])
          ]
          bundle = {
            "Name": v_parts[0],
            "DisplayName": v_parts[6],
            "Index": len(output_data[area_name]["Bundles"]),
            "IconSpriteIndex": int(sprite_index),
            "IconTexture": "LooseSprites\\JunimoNote",
            "Color": int(v_parts[3]) if v_parts[3] != "" else 0,
            "Items": items,
            "Pick": int(v_parts[5]) if v_parts[5] != "" else -1,
            "RequiredItems": int(v_parts[4]) if v_parts[4] != "" else -1,
            "Reward": reward,
          }
          output_data[area_name]["Bundles"].append(bundle)
        FileUtils.write_json(output_data, output_path / "Bundles_new.json")
        print("已保存到./output/json/Bundles_new.json")

      elif "CookingRecipes".lower() in json_path.name.lower():  # 食谱
        # "食谱名":"原料代码1 数量1 .../未使用/产物代码/解锁条件/显示名称"
        for key, value in data.items():
          v_parts: list[str] = value.split("/")
          i_parts: list[str] = v_parts[0].split()
          output_data[key] = {
            "Name": key,
            "Ingredients": [{"Item": id, "Count": int(count)} for id, count in zip(i_parts[0::2], i_parts[1::2])],
            "Yield": v_parts[2],
            "Conditions": v_parts[3],
            "DisplayName": v_parts[4] if v_parts[4] != "" else None,
          }
        FileUtils.write_json(output_data, output_path / "CookingRecipes_new.json")
        print("已保存到./output/json/CookingRecipes_new.json")

      elif "CraftingRecipes".lower() in json_path.name.lower():  # 制造
        # "配方名":"原料代码1 数量1 .../未使用/产物代码 数量/是否为BC/解锁条件/显示名称"
        for key, value in data.items():
          v_parts: list[str] = value.split("/")
          i_parts: list[str] = v_parts[0].split()
          y_parts: list[str] = v_parts[2].split()
          output_data[key] = {
            "Name": key,
            "Ingredients": [{"Item": id, "Count": int(count)} for id, count in zip(i_parts[0::2], i_parts[1::2])],
            "Yield": {
              "Item": y_parts[0],
              "Count": int(y_parts[1]) if len(y_parts) > 1 else 1,
            },
            "YieldIsBigcraftable": False if v_parts[3].lower() == "false" else True,
            "Conditions": v_parts[4],
            "DisplayName": v_parts[5] if v_parts[5] != "" else None,
          }
        FileUtils.write_json(output_data, output_path / "CraftingRecipes_new.json")
        print("已保存到./output/json/CraftingRecipes_new.json")

      elif "Fish".lower() in json_path.name.lower():  # 鱼
        # "鱼代码": “鱼名称/蟹笼捕获/概率/出没地点编号1 出没概率1 .../水域类型/最小英寸/最大英寸/是否教程鱼”
        # "鱼代码":"鱼名称/难度/运动类型/最小英寸/最大英寸/最早出没时间 最晚出没时间/出没季节1 .../出没天气/出没地点编号1 出没概率1 .../概率最大水深/基础概率/深度乘数/最低需求等级/是否教程鱼"
        for key, value in data.items():
          v_parts: list[str] = value.split("/")
          if v_parts[1] == "trap":  # 蟹笼鱼
            l_parts = v_parts[3].split()
            output_data[key] = {
              "Name": v_parts[0],
              "Type": v_parts[1],
              "Chance": float(v_parts[2]),
              "Location(Unused)": [
                {"ID": id, "Chance": float(chance)} for id, chance in zip(l_parts[0::2], l_parts[1::2])
              ],
              "WaterType": v_parts[4],
              "MinSize": int(v_parts[5]),
              "MaxSize": int(v_parts[6]),
              "TutorialFish": v_parts[7].lower() == "true",
            }
          else:  # 正常鱼
            t_parts: list[str] = v_parts[5].split()
            l_parts: list[str] = v_parts[8].split()
            output_data[key] = {
              "Name": v_parts[0],
              "Difficulty": int(v_parts[1]),
              "MotionType": v_parts[2],
              "MinSize": int(v_parts[3]),
              "MaxSize": int(v_parts[4]),
              "Time": {
                "MinTime": int(t_parts[0]),
                "MaxTime": int(t_parts[1]),
              },
              "Season": v_parts[6].split(),
              "weather": v_parts[7],
              "Location(Unused)": [
                {"ID": id, "Chance": float(chance)} for id, chance in zip(l_parts[0::2], l_parts[1::2])
              ]
              if len(l_parts) > 1
              else int(l_parts[0]),
              "MaxDepth": int(v_parts[9]),
              "Chance": float(v_parts[10]),
              "DepthMultiplier": float(v_parts[11]),
              "MinLevel": int(v_parts[12]),
              "TutorialFish": v_parts[13].lower() == "true",
            }
        FileUtils.write_json(output_data, output_path / "Fish_new.json")
        print("已保存到./output/json/Fish_new.json")

      elif "Furniture".lower() in json_path.name.lower():  # 装饰
        # "物品代码"："物品名称/物品类型/占地大小/碰撞大小/允许旋转类型/价格/放置限制/显示名称/贴图索引/能否出现在目录中/Tag"
        for key, value in data.items():
          v_parts: list[str] = value.split("/")
          tile_sheet_size: list[str] = v_parts[2].split()
          bounding_box_size: list[str] = v_parts[3].split()
          placement_map: dict[str, str] = {"-1": "default", "0": "indoors_only", "1": "outdoors_only", "2": "both"}
          output_data[key] = {
            "Name": v_parts[0],
            "Type": v_parts[1],
            "TileSheetSize": {
              "X": int(tile_sheet_size[0]),
              "Y": int(tile_sheet_size[1]),
            }
            if len(tile_sheet_size) > 1
            else int(v_parts[2]),
            "BoundingBoxSize": {
              "X": int(bounding_box_size[0]),
              "Y": int(bounding_box_size[1]),
            }
            if len(bounding_box_size) > 1
            else int(v_parts[3]),
            "Rotations": int(v_parts[4]),
            "Price": int(v_parts[5]),
            "Placement": placement_map[v_parts[6]],
            "DisplayName": v_parts[7],
            "SpriteIndex": int(v_parts[8]) if len(v_parts) > 8 and v_parts[8] != "" else int(key),
            "Texture": v_parts[9] if len(v_parts) > 9 and v_parts[9] != "" else "TileSheets\\furniture",
            "InTheCatalogue": v_parts[10].lower() == "true" if len(v_parts) > 10 and v_parts[10] != "" else False,
            "ContextTags": v_parts[11] if len(v_parts) > 11 and v_parts[11] != "" else None,
          }
        FileUtils.write_json(output_data, output_path / "Furniture_new.json")
        print("已保存到./output/json/Furniture_new.json")

      elif "hats".lower() in json_path.name.lower():  # 帽子
        # "物品代码":"名称/描述/是否显示头发/对发型的偏移/贴图路径/显示名称/贴图索引"
        for key, value in data.items():
          v_parts: list[str] = value.split("/")
          output_data[key] = {
            "Name": v_parts[0],
            "Description": v_parts[1],
            "ShowHair": v_parts[2],
            "HairstyleOffset": v_parts[3].lower() == "true",
            "Texture": v_parts[4] if v_parts[4] != "" else "Characters\\Farmer\\hats",
            "DisplayName": v_parts[5],
            "SpriteIndex": int(v_parts[6]) if len(v_parts) > 6 else int(key),
          }
        FileUtils.write_json(output_data, output_path / "hats_new.json")
        print("已保存到./output/json/hats_new.json")

      elif "Monsters".lower() in json_path.name.lower():
        # "怪物名称":"血量/攻击力/最少掉落金钱/最多掉落金钱/能否飞行/移动耐力/掉落物1 概率1 .../防御/抖动/仇恨范围/速度/闪避率/是否生成在矿洞/经验/显示名称"
        for key, value in data.items():
          v_parts: list[str] = value.split("/")
          d_parts: list[str] = v_parts[6].split()
          output_data[key] = {
            "Health": int(v_parts[0]),
            "Damage": int(v_parts[1]),
            "MinCoins(Unused)": int(v_parts[2]),
            "MaxCoins(Unused)": int(v_parts[3]),
            "CanFly": v_parts[4].lower() == "true",
            "DurationMovements": int(v_parts[5]),
            "Drop": [{"Item": id, "Chance": float(chance)} for id, chance in zip(d_parts[0::2], d_parts[1::2])],
            "Defense": int(v_parts[7]),
            "Jitteriness": float(v_parts[8]),
            "Range": int(v_parts[9]),
            "Speed": int(v_parts[10]),
            "Miss": float(v_parts[11]),
            "InTheMine": v_parts[12].lower() == "true",
            "experience": int(v_parts[13]),
            "DisplayName": v_parts[14],
          }
        FileUtils.write_json(output_data, output_path / "Monsters_new.json")
        print("已保存到./output/json/Monsters_new.json")

      elif "NPCGiftTastes".lower() in json_path.name.lower():  # 礼物偏好
        # "礼物类型": "物品代码"
        # "NPC名称": "最爱物品1 .../最爱反应/喜欢物品1 .../喜欢反应/不喜欢物品1 .../不喜欢反应/厌恶物品1 .../厌恶反应/普通物品1 .../普通反应"
        for key, value in data.items():
          v_parts: list[str] = value.split("/")
          if key in [
            "Universal_Love",
            "Universal_Like",
            "Universal_Neutral",
            "Universal_Dislike",
            "Universal_Hate",
          ]:
            output_data[key] = v_parts[0].split()
          else:
            output_data[key] = {
              "Love": v_parts[0],
              "LoveID": v_parts[1].split(),
              "Like": v_parts[2],
              "LikeID": v_parts[3].split(),
              "Dislike": v_parts[4],
              "DislikeID": v_parts[5].split(),
              "Hate": v_parts[6],
              "HateID": v_parts[7].split(),
              "Neutral": v_parts[8],
              "NeutralID": v_parts[9].split(),
            }
        FileUtils.write_json(output_data, output_path / "NPCGiftTastes_new.json")
        print("已保存到./output/json/NPCGiftTastes_new.json")

      elif "Quests".lower() in json_path.name.lower():  # 任务
        # "任务索引":"类型/任务名称/任务描述/任务提示/需求条件/后续任务索引/奖金/奖金理由/能否取消/完成反应"
        for key, value in data.items():
          v_parts: list[str] = value.split("/")
          output_data[key] = {
            "Type": v_parts[0],
            "Title": v_parts[1],
            "Description": v_parts[2],
            "Hint": v_parts[3],
            "Requirements": v_parts[4],
            "NextQuest": v_parts[5],
            "Reward": int(v_parts[6]),
            "RewardDescription(Unused)": v_parts[7] if len(v_parts) > 7 else None,
            "CanCancelled": v_parts[8].lower() == "true" if len(v_parts) > 8 else False,
            "Reaction": v_parts[9] if len(v_parts) > 9 else None,
          }
        FileUtils.write_json(output_data, output_path / "Quests_new.json")
        print("已保存到./output/json/Quests_new.json")
      elif "ChairTiles".lower() in json_path.name.lower():
        print("该文件设置了全游戏固定椅子的判定和类型")
      elif "HairData".lower() in json_path.name.lower():
        print("该文件设置了玩家发色")
      elif "PaintData".lower() in json_path.name.lower():
        print("该文件设置了可调色的建筑")
      else:
        print(f"{json_path.name}文件已为标准json文件，无需解析")

if __name__ == "__main__":
  main()

  ...
