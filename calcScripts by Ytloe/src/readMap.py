import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Dict, Set


def count_water_tiles(tmx_file: str) -> None:
  # 解析XML文件
  map_dir = Path(__file__).parent.parent / "maps"
  try:
    tree = ET.parse(map_dir / tmx_file)
    root = tree.getroot()
  except ET.ParseError as e:
    print(f"XML解析错误: {e}")
    return
  except FileNotFoundError:
    print(f"文件未找到: {tmx_file}")
    return

  # 存储Water图块的全局ID
  water_global_ids: Set[int] = set()
  water_cont_passable_ids: Set[int] = set()
  # 步骤1: 收集所有带有Water属性的tile ID (结合tileset的firstgid)
  for tileset in root.findall(".//tileset"):
    firstgid_str = tileset.get("firstgid")
    if firstgid_str is None:
      continue  # 跳过没有firstgid的tileset
    try:
      firstgid = int(firstgid_str)
    except ValueError:
      continue  # 跳过无效的firstgid值

    for tile in tileset.findall("tile"):
      tile_id_str = tile.get("id")
      if tile_id_str is None:
        continue

      try:
        tile_id = int(tile_id_str)
      except ValueError:
        continue  # 跳过无效的tile id

      # 检查是否存在Water属性
      properties = tile.find("properties")
      if properties is None:
        continue

      found_water = False
      for prop in properties.findall("property"):
        name_attr = prop.get("name")
        value_attr = prop.get("value")
        if name_attr == "Water" and value_attr == "T":
          # 计算全局ID: firstgid + 本地tile id
          global_id = firstgid + tile_id
          water_global_ids.add(global_id)
          found_water = True
          break
        if name_attr == "Passable" and value_attr == "F":
          cont_passable_id = firstgid + tile_id
          water_cont_passable_ids.add(cont_passable_id)
          break
      if found_water:
        continue  # 继续处理下一个tile

  # 如果没有找到Water图块
  if not water_global_ids:
    print("未找到带有Water属性的图块")
    return

  # 步骤2: 查找ID为1的图层
  layer = root.find(".//layer[@id='1']")
  if layer is None:
    print("未找到ID为1的图层")
    return

  # 步骤3: 解析CSV地图数据
  data_element = layer.find("data")
  if data_element is None:
    print("图层中未找到地图数据")
    return

  # 获取并清理CSV数据
  text_content = data_element.text
  if text_content is None:
    print("地图数据为空")
    return

  # 清理并分割CSV数据
  csv_data = text_content.replace("\n", "").replace(" ", "")
  if not csv_data:
    print("地图数据为空")
    return

  # 统计图块出现次数
  tile_counts: Dict[int, int] = defaultdict(int)
  for tile_id_str in csv_data.split(","):
    try:
      tile_id = int(tile_id_str)
      tile_counts[tile_id] += 1
    except ValueError:
      continue  # 忽略无效的图块ID

  # 计算Water图块总数
  total_water = sum(count for tile_id, count in tile_counts.items() if tile_id in water_global_ids)
  cont_passable_water = sum(count for tile_id, count in tile_counts.items() if tile_id in water_cont_passable_ids)

  # 输出结果
  # print(f"找到 {len(water_global_ids)} 个Water图块全局ID: {sorted(water_global_ids)}")
  print(f"地图{tmx_file}中Water图块总数量: {total_water}，临岸地块数量：{cont_passable_water}")


if __name__ == "__main__":
  all_farms = [
    "Farm.tmx",  # 经典
    "Farm_Fishing.tmx",  # 河边
    "Farm_Foraging.tmx",  # 森林
    "Farm_Mining.tmx",  # 山顶
    "Farm_Combat.tmx",  # 荒野
    "Farm_FourCorners.tmx",  # 四角
    "Farm_Island.tmx",  # 海滩
    "Farm_Ranching.tmx",  # 草原
  ]
  for tmx_file in all_farms:
    # print(f"处理地图: {tmx_file}")
    count_water_tiles(tmx_file)
