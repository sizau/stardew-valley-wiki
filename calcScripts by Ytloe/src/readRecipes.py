import csv
import datetime
import re
from pathlib import Path
from typing import Any

# 导入通用工具库
from utils import FileUtils, Logger, PerfMonitor, StringUtils


class RecipeParser:
  def __init__(self):
    """初始化并预加载所有需要的JSON文件"""
    # 创建日志目录
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # 创建日志记录器
    self.logger = Logger("RecipeParser", save_to_file=True, filepath=log_dir / "recipe_parser.log")

    # 创建性能监控器
    self.perf_monitor = PerfMonitor("整体运行")
    self.perf_monitor.start()

    # 设置输出目录结构
    self.output_base_dir = Path(__file__).parent.parent / "output"
    self.crafting_dir = self.output_base_dir / "crafting"
    self.cooking_dir = self.output_base_dir / "cooking"
    self.total_dir = self.output_base_dir / "total"

    # 创建输出目录
    for dir_path in [self.crafting_dir, self.cooking_dir, self.total_dir]:
      dir_path.mkdir(parents=True, exist_ok=True)

    # 初始化类别映射表
    self.manual_item_mapping = {
      "-4": "鱼类(任意)",
      "-5": "蛋类(任意)",
      "-6": "奶类(任意)",
      "-7": "油类(任意)",
      "-777": "季节种子(任意)",
      # 可以根据需要添加更多映射
    }
    self.logger.info("已加载手动物品映射表")

    self.logger.info("正在加载数据文件...")

    # 预加载所有JSON文件到内存
    self.crafting_recipes_data : dict[str, str] = self._load_json_safe("CraftingRecipes.json")
    self.cooking_recipes_data : dict[str, str] = self._load_json_safe("CookingRecipes.json")
    self.objects_data : dict[str, dict[str, Any]] = self._load_json_safe("Objects.json")
    self.objects_localization : dict[str, str] = self._load_json_safe("Objects.zh-CN.json")
    self.bigcraftables_data : dict[str, dict[str, Any]] = self._load_json_safe("BigCraftables.json")
    self.bigcraftables_localization : dict[str, str]  = self._load_json_safe("BigCraftables.zh-CN.json")

    self.logger.info("数据加载完成")

  def _load_json_safe(self, filename) -> dict[str, Any]:
    """安全加载JSON文件"""
    try:
      json_path = Path(__file__).parent.parent / "json" / filename
      data = FileUtils.read_json(json_path)
      self.logger.info(f"成功加载文件: {filename}")
      return data
    except FileNotFoundError:
      self.logger.warning(f"找不到文件: {filename}")
      return {}
    except Exception as ex:
      self.logger.error(f"加载 {filename} 时出错: {ex}")
      return {}

  def read_recipes(self) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    """读取配方文件，解析物品代码和数量，分别返回制造和烹饪配方"""
    crafting_recipes = {}
    cooking_recipes = {}

    # 解析制造配方
    for recipe_name, recipe_string in self.crafting_recipes_data.items():
      parts = recipe_string.split("/")
      if len(parts) >= 4:
        materials = []
        material_parts = parts[0].split()

        for i in range(0, len(material_parts), 2):
          if i + 1 < len(material_parts):
            item_code = material_parts[i]
            quantity = int(material_parts[i + 1])
            materials.append({"code": item_code, "quantity": quantity})

        product_parts = parts[2].split()
        product_code = product_parts[0]
        product_quantity = int(product_parts[1]) if len(product_parts) > 1 else 1
        is_bigcraftable = parts[3].lower() == "true"

        crafting_recipes[recipe_name] = {
          "materials": materials,
          "product": {"code": product_code, "quantity": product_quantity, "is_bigcraftable": is_bigcraftable},
          "type": "crafting",
        }

    # 解析烹饪配方
    for recipe_name, recipe_string in self.cooking_recipes_data.items():
      parts = recipe_string.split("/")
      if len(parts) >= 3:
        materials = []
        material_parts = parts[0].split()

        for i in range(0, len(material_parts), 2):
          if i + 1 < len(material_parts):
            item_code = material_parts[i]
            quantity = int(material_parts[i + 1])
            materials.append({"code": item_code, "quantity": quantity})

        product_parts = parts[2].split()
        product_code = product_parts[0]
        product_quantity = int(product_parts[1]) if len(product_parts) > 1 else 1

        cooking_recipes[recipe_name] = {
          "materials": materials,
          "product": {"code": product_code, "quantity": product_quantity, "is_bigcraftable": False},
          "type": "cooking",
        }

    self.logger.info(f"成功解析 {len(crafting_recipes)} 个制造配方和 {len(cooking_recipes)} 个烹饪配方")
    return crafting_recipes, cooking_recipes

  def get_item_info(self, item_code, is_bigcraftable=None):
    """统一的物品信息获取方法"""
    # 先检查手动映射表
    if item_code in self.manual_item_mapping:
      # 对于手动映射的物品，返回None作为localization_key，因为它们不需要从本地化文件查找
      return None, item_code, item_code

    # 处理负数物品代码（检查是否在手动映射中）
    if item_code.startswith("-"):
      return None, item_code, item_code

    clean_code = item_code
    has_prefix = False
    if item_code.startswith("(") and ")" in item_code:
      prefix_end = item_code.index(")") + 1
      clean_code = item_code[prefix_end:]
      has_prefix = True

    if is_bigcraftable is not None:
      search_bigcraftable = is_bigcraftable
    elif has_prefix and item_code.startswith("(BC)"):
      search_bigcraftable = True
    else:
      search_bigcraftable = False

    if search_bigcraftable:
      if clean_code in self.bigcraftables_data:
        display_name = self.bigcraftables_data[clean_code].get("DisplayName", "")
        match = re.search(r":(\w+_Name)]", display_name)
        if match:
          return match.group(1), clean_code, f"(BC){clean_code}"
    else:
      if clean_code in self.objects_data:
        display_name = self.objects_data[clean_code].get("DisplayName", "")
        match = re.search(r":(\w+_Name)]", display_name)
        if match:
          return match.group(1), clean_code, f"(O){clean_code}"

    return None, clean_code, item_code

  def get_item_name(self, item_code, is_bigcraftable=None):
    """统一的物品名称获取方法"""
    # 首先检查手动映射表
    clean_code = item_code
    if item_code.startswith("(") and ")" in item_code:
      prefix_end = item_code.index(")") + 1
      clean_code = item_code[prefix_end:]

    if clean_code in self.manual_item_mapping:
      mapped_name = self.manual_item_mapping[clean_code]
      # self.logger.info(f"使用手动映射: {item_code} -> {mapped_name}")
      return mapped_name, item_code

    # 如果不在手动映射表中，继续原有的解析逻辑
    localization_key, clean_code, normalized_code = self.get_item_info(item_code, is_bigcraftable)

    if localization_key:
      if normalized_code.startswith("(BC)"):
        localization_data = self.bigcraftables_localization
      else:
        localization_data = self.objects_localization

      if localization_key in localization_data:
        return localization_data[localization_key], normalized_code

    # 如果都找不到，再次检查是否为负数代码（可能在手动映射中）
    if item_code.startswith("-") and item_code in self.manual_item_mapping:
      return self.manual_item_mapping[item_code], item_code

    return f"未知物品({item_code})", item_code

  def get_all_recipes_with_names(self) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    """获取所有配方并转换物品代码为中文名称"""
    crafting_recipes, cooking_recipes = self.read_recipes()

    # 处理制造配方
    for recipe_name, recipe_info in crafting_recipes.items():
      for material in recipe_info["materials"]:
        material["name"], material["normalized_code"] = self.get_item_name(material["code"])
      product = recipe_info["product"]
      product["name"], product["normalized_code"] = self.get_item_name(
        product["code"], product.get("is_bigcraftable", False)
      )

    # 处理烹饪配方
    for recipe_name, recipe_info in cooking_recipes.items():
      for material in recipe_info["materials"]:
        material["name"], material["normalized_code"] = self.get_item_name(material["code"])
      product = recipe_info["product"]
      product["name"], product["normalized_code"] = self.get_item_name(
        product["code"], product.get("is_bigcraftable", False)
      )

    return crafting_recipes, cooking_recipes

  @staticmethod
  def calc_material_usage_detailed(recipes) -> dict[str, Any]:
    """统计指定配方集合中每种材料的总使用量，返回详细信息"""
    # 使用材料名称作为键，值为包含代码和数量的字典
    material_usage = {}

    for recipe_name, recipe_info in recipes.items():
      for material in recipe_info["materials"]:
        material_name = material["name"]
        material_code = material["normalized_code"]
        quantity = material["quantity"]

        if material_name not in material_usage:
          material_usage[material_name] = {"code": material_code, "quantity": 0}
        material_usage[material_name]["quantity"] += quantity

    # 按数量排序
    sorted_usage = dict(sorted(material_usage.items(), key=lambda x: x[1]["quantity"], reverse=True))
    return sorted_usage

  def save_recipes_txt(self, recipes, output_dir, recipe_type):
    """保存配方信息到TXT文件"""
    output_file = output_dir / "recipes.txt"

    with output_file.open("w", encoding="utf-8") as f:
      f.write(f"=== {recipe_type}配方信息 ===\n")
      f.write(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
      f.write(f"配方总数: {len(recipes)}\n\n")

      for recipe_name, recipe_info in recipes.items():
        product = recipe_info["product"]
        f.write(f"{recipe_name}: {product['name']} [{product['normalized_code']}] × {product['quantity']}\n")
        for material in recipe_info["materials"]:
          f.write(f"  - {material['name']} [{material['normalized_code']}] × {material['quantity']}\n")
        f.write("\n")

    self.logger.info(f"{recipe_type}配方TXT已保存到: {output_file}")

  def save_recipes_json(self, recipes, output_dir, recipe_type):
    """保存配方信息到JSON文件"""
    output_file = output_dir / "recipes.json"

    export_data = {
      "生成时间": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      "配方类型": recipe_type,
      "配方总数": len(recipes),
      "配方详情": {},
    }

    for recipe_name, recipe_info in recipes.items():
      export_data["配方详情"][recipe_name] = {
        "产品": {
          "名称": recipe_info["product"]["name"],
          "代码": recipe_info["product"]["normalized_code"],
          "数量": recipe_info["product"]["quantity"],
        },
        "材料": [
          {"名称": mat["name"], "代码": mat["normalized_code"], "数量": mat["quantity"]}
          for mat in recipe_info["materials"]
        ],
      }

    FileUtils.write_json(export_data, output_file)
    self.logger.info(f"{recipe_type}配方JSON已保存到: {output_file}")

  def save_statistics_txt(self, crafting_usage, cooking_usage, total_usage, output_dir) -> None:
    """保存统计信息到TXT文件"""
    output_file = output_dir / "statistics.txt"

    with output_file.open("w", encoding="utf-8") as f:
      f.write("=== 材料使用统计 ===\n")
      f.write(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

      # 制造配方统计
      f.write("== 制造配方材料统计 ==\n")
      self._write_usage_table_with_code(f, crafting_usage)

      # 烹饪配方统计
      f.write("\n== 烹饪配方材料统计 ==\n")
      self._write_usage_table_with_code(f, cooking_usage)

      # 总统计
      f.write("\n== 总材料使用统计 ==\n")
      self._write_usage_table_with_code(f, total_usage)

    self.logger.info(f"统计TXT已保存到: {output_file}")

  @staticmethod
  def _write_usage_table_with_code(file_handle, usage_dict) -> None:
    """写入材料使用统计表格"""
    # 计算材料名称[代码]的最大显示宽度
    max_width = 0
    for material_name, info in usage_dict.items():
      display_text = f"{material_name} [{info['code']}]"
      width = StringUtils.get_display_width(display_text)
      max_width = max(max_width, width)

    # 设置列宽，留一些余量
    name_column_width = max_width + 2

    # 写入表头
    header = StringUtils.pad_to_width("材料名称 [物品代码]", name_column_width)
    file_handle.write(f"{header}| {'总使用量':>8}\n")
    file_handle.write("-" * (name_column_width + 12) + "\n")

    # 写入数据
    for material_name, info in usage_dict.items():
      display_text = f"{material_name}[{info['code']}]"
      padded_text = StringUtils.pad_to_width(display_text, name_column_width)
      file_handle.write(f"{padded_text}| {info['quantity']:>8}\n")

  def save_statistics_json(self, crafting_usage, cooking_usage, total_usage, output_dir):
    """保存统计信息到JSON文件"""
    output_file = output_dir / "statistics.json"

    # 从详细数据中提取只包含数量的字典
    crafting_simple = {name: info["quantity"] for name, info in crafting_usage.items()}
    cooking_simple = {name: info["quantity"] for name, info in cooking_usage.items()}
    total_simple = {name: info["quantity"] for name, info in total_usage.items()}

    export_data = {
      "生成时间": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      "制造配方材料统计": {"材料种类": len(crafting_simple), "材料使用情况": crafting_simple},
      "烹饪配方材料统计": {"材料种类": len(cooking_simple), "材料使用情况": cooking_simple},
      "总材料统计": {"材料种类": len(total_simple), "材料使用情况": total_simple},
    }

    FileUtils.write_json(export_data, output_file)
    self.logger.info(f"统计JSON已保存到: {output_file}")

  def save_statistics_csv(self, crafting_usage, cooking_usage, total_usage, output_dir):
    """保存统计信息到CSV文件"""
    output_file = output_dir / "statistics.csv"

    with output_file.open("w", encoding="utf-8-sig", newline="") as f:
      writer = csv.writer(f)
      writer.writerow(["类别", "材料名称", "物品代码", "使用量"])

      # 写入制造配方统计
      for material_name, info in crafting_usage.items():
        writer.writerow(["制造配方", material_name, f"{info['code']}", info["quantity"]])

      # 写入烹饪配方统计
      for material_name, info in cooking_usage.items():
        writer.writerow(["烹饪配方", material_name, f"{info['code']}", info["quantity"]])

      # 写入总统计
      for material_name, info in total_usage.items():
        writer.writerow(["总计", material_name, f"{info['code']}", info["quantity"]])

    self.logger.info(f"统计CSV已保存到: {output_file}")

  def process_and_save_all(self):
    """处理所有数据并保存到各种格式"""
    # 获取配方数据
    crafting_recipes, cooking_recipes = self.get_all_recipes_with_names()

    # 计算材料使用统计（使用新的详细方法）
    crafting_usage = self.calc_material_usage_detailed(crafting_recipes)
    cooking_usage = self.calc_material_usage_detailed(cooking_recipes)

    # 计算总统计
    total_usage = {}

    # 合并制造配方的材料
    for material_name, info in crafting_usage.items():
      total_usage[material_name] = {"code": info["code"], "quantity": info["quantity"]}

    # 合并烹饪配方的材料
    for material_name, info in cooking_usage.items():
      if material_name in total_usage:
        total_usage[material_name]["quantity"] += info["quantity"]
      else:
        total_usage[material_name] = {"code": info["code"], "quantity": info["quantity"]}

    # 按数量排序
    total_usage = dict(sorted(total_usage.items(), key=lambda x: x[1]["quantity"], reverse=True))

    # 保存制造配方数据
    self.logger.info("正在保存制造配方数据...")
    self.save_recipes_txt(crafting_recipes, self.crafting_dir, "制造")
    self.save_recipes_json(crafting_recipes, self.crafting_dir, "制造")

    # 保存烹饪配方数据
    self.logger.info("正在保存烹饪配方数据...")
    self.save_recipes_txt(cooking_recipes, self.cooking_dir, "烹饪")
    self.save_recipes_json(cooking_recipes, self.cooking_dir, "烹饪")

    # 保存统计数据
    self.logger.info("正在保存统计数据...")
    self.save_statistics_txt(crafting_usage, cooking_usage, total_usage, self.total_dir)
    self.save_statistics_json(crafting_usage, cooking_usage, total_usage, self.total_dir)
    self.save_statistics_csv(crafting_usage, cooking_usage, total_usage, self.total_dir)

    self.logger.info("所有数据保存完成！")

  def show_performance_stats(self):
    """显示性能统计信息"""
    self.perf_monitor.stop()
    print(f"\n{self.perf_monitor.format_stats()}")

    stats = self.perf_monitor.get_stats()
    self.logger.info(
      f"程序运行完成 - 总时间: {stats['elapsed_ms']:.2f}ms, 内存增量: {stats['memory_delta_mb']:.2f}MB"
    )


# 使用示例
if __name__ == "__main__":
  try:
    # 创建解析器实例
    parser = RecipeParser()

    # 处理并保存所有数据
    parser.process_and_save_all()

    # 显示性能统计
    parser.show_performance_stats()

    print(f"\n所有文件已保存到: {parser.output_base_dir}")
    print(f"- 制造配方: {parser.crafting_dir}")
    print(f"- 烹饪配方: {parser.cooking_dir}")
    print(f"- 总统计: {parser.total_dir}")

  except Exception as e:
    print(f"发生错误: {e}")
    import traceback

    traceback.print_exc()
