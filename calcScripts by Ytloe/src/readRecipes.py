import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from utils import FileUtils, PerfMonitor, StringUtils


class Item:
  """物品类，存储物品的前缀、代码、数量和名称

  Attributes:
      prefix: 物品的类型识别标志，例如 (O)、(BC)
      code: 物品 ID
      count: 物品数量
      displayName: 物品的汉语名称
      name: 物品的英语名称
  """
  def __init__(self, prefix: str = "(O)", code: str = "", count: int = 1, displayName: str = "", name: str = ""):
    self.prefix = prefix
    self.code = code
    self.count = count
    self.displayName = displayName
    self.name = name

  def __repr__(self):
    return f"{self.displayName}[{self.prefix}{self.code}] × {self.count}"

  def __str__(self):
    return self.__repr__()

  def to_dict(self):
    return {"prefix": self.prefix, "code": self.code, "count": self.count, "name": self.displayName}

  def get_key(self):
    """获取物品的唯一标识键"""
    return f"{self.displayName}[{self.prefix}{self.code}]"


class Recipe:
  """配方类，存储配方名称、原料列表和产物

  Attributes:
      recipe_name: 配方的名称
      materials: 配方所需的原材料
      product: 配方产出的物品
      is_expanded: 配方是否已展开
  """
  def __init__(self, recipe_name: str, materials: List[Item], product: Item, is_expanded: bool = False):
    self.recipe_name = recipe_name
    self.materials = materials
    self.product = product
    self.is_expanded = is_expanded

  def __repr__(self):
    # 配方名称（添加展开标记）
    name_suffix = "（已展开）" if self.is_expanded else ""
    result = f"{self.recipe_name}{name_suffix}：\n"

    # 原料列表
    for material in self.materials:
      result += f" - {material}\n"

    # 产物
    result += f" > {self.product}\n"

    return result

  def __str__(self):
    return self.__repr__()

  def to_dict(self):
    """转换为字典格式用于JSON导出"""
    name_suffix = "（已展开）" if self.is_expanded else ""
    materials_dict = {}
    for material in self.materials:
      materials_dict[material.get_key()] = material.count

    return {
      f"{self.recipe_name}{name_suffix}": {"原料": materials_dict, self.product.get_key(): self.product.count}
    }


class RecipeParser:
  def __init__(self):
    self.cooking_recipes = {}
    self.crafting_recipes = {}
    self.objects_data = {}
    self.objects_zh_cn = {}
    self.bigcraftables_data = {}
    self.bigcraftables_zh_cn = {}
    self.all_recipes = {}
    self.cooking_recipe_objects = {}  # 存储解析后的烹饪配方对象
    self.crafting_recipe_objects = {}  # 存储解析后的制作配方对象
    self.ignore_recipes = ["Transmute (Fe)", "Transmute (Au)"]  # 需要忽略拆解的配方列表
    self.expanded_recipes = set()  # 记录已展开的配方

    # 类别映射
    self.negative_code_mapping = {
      "-4": "鱼类(任意)",
      "-5": "蛋类(任意)",
      "-6": "奶类(任意)",
      "-7": "油类(任意)",
      "-777": "季节种子(任意)",
    }

  def read_json_files(self):
    """读取JSON文件"""
    json_path = Path(__file__).parent.parent / "json"
    self.crafting_recipes = FileUtils.read_json(json_path / "CraftingRecipes.json")
    self.cooking_recipes = FileUtils.read_json(json_path / "CookingRecipes.json")
    self.objects_data = FileUtils.read_json(json_path / "Objects.json")
    self.objects_zh_cn = FileUtils.read_json(json_path / "Objects.zh-CN.json")
    self.bigcraftables_data = FileUtils.read_json(json_path / "BigCraftables.json")
    self.bigcraftables_zh_cn = FileUtils.read_json(json_path / "BigCraftables.zh-CN.json")

  def parse_item(self, item_str: str, is_product: bool = False, is_bc: bool = False) -> Item:
    """解析物品代码为物品类"""

    # 分离代码和数量
    parts = item_str.strip().split()
    if len(parts) == 2:
      code_part, count = parts[0], int(parts[1])
    else:
      code_part, count = parts[0], 1

    # 解析前缀和代码
    if is_product:
      # 产物代码处理
      if is_bc:
        prefix = "(BC)"
      else:
        prefix = "(O)"
      code = code_part
    else:
      # 原料代码处理
      if code_part.startswith("-"):
        # 负数情况
        prefix = ""
        code = code_part
      elif code_part.startswith("(") and ")" in code_part:
        # 带括号前缀的情况
        match = re.match(r"\(([^)]+)\)(.+)", code_part)
        if match:
          prefix = f"({match.group(1)})"
          code = match.group(2)
        else:
          prefix = "(O)"
          code = code_part
      else:
        # 纯数字或英文
        prefix = "(O)"
        code = code_part

    item = Item(prefix=prefix, code=code, count=count, displayName="", name="")
    # 获取物品名称
    (item.displayName, item.name) = self.get_item_name(item)

    return item

  def _parse_recipe(self, recipe_name: str, recipe_str: str, is_crafting: bool = False) -> Recipe:
    """解析单个配方"""
    # 分割配方字符串
    parts = recipe_str.split("/")

    # 解析原料部分
    materials_str = parts[0]
    materials = []

    # 解析每个原料
    material_items = materials_str.split()
    i = 0
    while i < len(material_items):
      # 检查是否是带括号的前缀
      if material_items[i].startswith("(") and ")" in material_items[i]:
        # 带前缀的情况
        if i + 1 < len(material_items) and material_items[i + 1].isdigit():
          item_str = f"{material_items[i]} {material_items[i + 1]}"
          i += 2
        else:
          item_str = material_items[i]
          i += 1
      else:
        # 检查下一个是否是数量
        if i + 1 < len(material_items) and material_items[i + 1].isdigit():
          item_str = f"{material_items[i]} {material_items[i + 1]}"
          i += 2
        else:
          item_str = material_items[i]
          i += 1

      materials.append(self.parse_item(item_str, is_product=False))

    # 解析产物部分
    product_str = parts[2]

    # 判断是否为BC
    is_bc = False
    if is_crafting and len(parts) > 3:
      is_bc = parts[3].lower() == "true"

    # 解析产物
    product = self.parse_item(product_str, is_product=True, is_bc=is_bc)

    return Recipe(recipe_name, materials, product)

  def parse_all_recipes(self) -> Dict[str, Recipe]:
    """解析所有配方"""
    # 读取JSON文件
    self.read_json_files()

    # 解析烹饪配方
    for recipe_name, recipe_str in self.cooking_recipes.items():
      recipe = self._parse_recipe(recipe_name, recipe_str, is_crafting=False)
      self.all_recipes[recipe_name] = recipe
      self.cooking_recipe_objects[recipe_name] = recipe

    # 解析制作配方
    for recipe_name, recipe_str in self.crafting_recipes.items():
      recipe = self._parse_recipe(recipe_name, recipe_str, is_crafting=True)
      self.all_recipes[recipe_name] = recipe
      self.crafting_recipe_objects[recipe_name] = recipe

    # 展开嵌套配方
    self.expand_recipes()

    return self.all_recipes

  def expand_recipes(self) -> None:
    """展开嵌套配方"""
    # 创建产物到配方的映射
    product_to_recipe = {}
    for recipe_name, recipe in self.all_recipes.items():
      if recipe_name not in self.ignore_recipes:
        key = f"{recipe.product.prefix}{recipe.product.code}"
        product_to_recipe[key] = recipe

    # 展开所有配方
    expanded = True
    while expanded:
      expanded = False
      for recipe_name, recipe in self.all_recipes.items():
        # 使用字典来合并相同的材料
        material_dict = {}
        has_expansion = False

        for material in recipe.materials:
          # 构建材料的键
          material_key = f"{material.prefix}{material.code}"

          # 检查是否可以展开
          if material_key in product_to_recipe:
            source_recipe = product_to_recipe[material_key]
            # 展开材料
            for sub_material in source_recipe.materials:
              # 构建子材料的唯一键
              sub_key = f"{sub_material.prefix}{sub_material.code}"
              # 计算新的数量
              new_count = sub_material.count * material.count

              # 如果已存在相同材料，累加数量
              if sub_key in material_dict:
                material_dict[sub_key].count += new_count
              else:
                # 创建新的材料项
                new_item = Item(
                  prefix=sub_material.prefix,
                  code=sub_material.code,
                  count=new_count,
                  displayName=sub_material.displayName,
                  name=sub_material.name
                )
                material_dict[sub_key] = new_item

            expanded = True
            has_expansion = True
          else:
            # 不能展开的材料，也要检查是否已存在
            if material_key in material_dict:
              material_dict[material_key].count += material.count
            else:
              material_dict[material_key] = material

        if has_expansion:
          # 将字典转换回列表
          recipe.materials = list(material_dict.values())
          recipe.is_expanded = True
          self.expanded_recipes.add(recipe_name)

  def get_item_name(self, item: Item) -> tuple[str, str]:
    """获取物品的中文名称"""
    # 处理负数
    if item.prefix == "" and item.code in self.negative_code_mapping:
      ncm = self.negative_code_mapping[item.code]
      return ncm, ncm

    # 根据prefix选择数据源
    if item.prefix == "(O)":
      data_source = self.objects_data
      localization_source = self.objects_zh_cn
    elif item.prefix == "(BC)":
      data_source = self.bigcraftables_data
      localization_source = self.bigcraftables_zh_cn
    else:
      return "", ""

    # 查找物品数据
    if item.code in data_source:
      item_data = data_source[item.code]
      name = item_data.get("Name", "")
      display_name = item_data.get("DisplayName", "")

      # 解析DisplayName中的本地化键
      if display_name.startswith("[LocalizedText"):
        # 提取本地化键，格式如 "[LocalizedText Strings\Objects:Moss_Name]"

        match = re.search(r":([^]]+)_Name]", display_name)
        if match:
          localization_key = match.group(1) + "_Name"
          # 从本地化文件中获取名称
          if localization_key in localization_source:
            return localization_source[localization_key], name

    return "未知物品", "未知物品"

  @staticmethod
  def calc_material_count(recipes: Dict[str, Recipe]) -> Dict[str, int]:
    """计算原料统计"""
    material_stats = defaultdict(int)

    for recipe in recipes.values():
      for material in recipe.materials:
        material_key = material.get_key()
        material_stats[material_key] += material.count

    # 按数量降序排序
    sorted_stats = dict(sorted(material_stats.items(), key=lambda x: x[1], reverse=True))
    return sorted_stats

  def save_recipes_to_files(self, recipes: Dict[str, Recipe], output_dir: Path, file_prefix: str):
    """保存配方到文件"""
    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)

    # 计算统计数据
    material_stats = self.calc_material_count(recipes)

    # 保存TXT文件
    txt_path = output_dir / f"{file_prefix}.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
      # 写入配方
      for recipe in recipes.values():
        f.write(str(recipe))
        f.write("\n\n")

      # 计算统计表宽度
      max_width = 0
      for material, count in material_stats.items():
        width = StringUtils.get_display_width(material)
        max_width = max(max_width, width)

      # 写入统计
      f.write(f"{file_prefix}材料统计")
      f.write("\n" + "=" * (max_width + 16) + "\n")
      header = StringUtils.pad_to_width("原料[代码]", max_width)
      f.write(f"{header} | {'数量（降序）':>8}\n")
      f.write("-" * (max_width + 16) + "\n")
      for material, count in material_stats.items():
        material = StringUtils.pad_to_width(material, max_width)
        f.write(f"{material} | {count:>12}\n")

    # 保存JSON文件
    json_data = {}
    for recipe in recipes.values():
      json_data.update(recipe.to_dict())

    json_path = output_dir / f"{file_prefix}.json"
    FileUtils.write_json(json_data, json_path)

    print(f"已保存 {len(recipes)} 个配方到 {output_dir}")
    print(f"共需要 {len(material_stats)} 种原料")

  def save_all_results(self):
    """保存所有结果"""
    output_base = Path(__file__).parent.parent / "output"

    # 保存烹饪配方
    cooking_dir = output_base / "CookingRecipes"
    self.save_recipes_to_files(self.cooking_recipe_objects, cooking_dir, "CookingRecipes")

    # 保存制作配方
    crafting_dir = output_base / "CraftingRecipes"
    self.save_recipes_to_files(self.crafting_recipe_objects, crafting_dir, "CraftingRecipes")

    # 保存全部配方
    total_dir = output_base / "total"
    self.save_recipes_to_files(self.all_recipes, total_dir, "AllRecipes")


# 使用示例
if __name__ == "__main__":
  monitor = PerfMonitor()
  monitor.start()
  # 创建解析器
  parser = RecipeParser()

  # 解析所有配方
  """
  完整流程：
  read_json_files()读取6个需要的json文件
  parse_all_recipes()→parse_recipe()解析所有配方代码为Item格式
  expand_recipes()展开所有可拆分的原料并打上“已拆分”标记
  get_item_name()进入Objects和BigCraftables中根据完整代码获取对应物品的中文键名
  calc_material_count()计算所有配方的原料数量
  """
  Recipes = parser.parse_all_recipes()

  # 保存所有结果
  parser.save_all_results()
  monitor.stop()
