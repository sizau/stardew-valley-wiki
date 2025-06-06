import datetime
import re
from collections import defaultdict
from pathlib import Path

# 导入通用工具库
from utils import FileUtils, Logger, PerfMonitor, StringUtils


class RecipeParser:
  def __init__(self):
    """初始化并预加载所有需要的JSON文件"""
    # 创建日志记录器
    self.logger = Logger("RecipeParser", save_to_file=True, filepath=Path("recipe_parser.log"))

    # 创建性能监控器
    self.perf_monitor = PerfMonitor("整体运行")
    self.perf_monitor.start()

    # 创建输出文件路径
    self.output_file = Path(__file__).parent.parent / "json" / "output.txt"
    self.output_content = []

    self._print("正在加载数据文件...")

    # 预加载所有JSON文件到内存
    self.objects_data = self._load_json_safe("Objects.json")
    self.bigcraftables_data = self._load_json_safe("BigCraftables.json")
    self.objects_localization = self._load_json_safe("Objects.zh-CN.json")
    self.bigcraftables_localization = self._load_json_safe("BigCraftables.zh-CN.json")
    self.recipes_data = self._load_json_safe("CraftingRecipes.json")

    self._print("数据加载完成")
    self.logger.info("数据加载完成")

  def _print(self, content=""):
    """同时输出到控制台和保存到列表"""
    print(content)
    self.output_content.append(content)

  def save_output(self):
    """将所有输出内容保存到文件"""
    with self.output_file.open("w", encoding="utf-8") as f:
      f.write("\n".join(self.output_content))
    self._print(f"\n输出已保存到: {self.output_file}")
    self.logger.info(f"输出已保存到: {self.output_file}")

  def _load_json_safe(self, filename):
    """安全加载JSON文件"""
    try:
      json_path = Path(__file__).parent.parent / "json" / filename
      data = FileUtils.read_json(json_path)
      self.logger.info(f"成功加载文件: {filename}")
      return data
    except FileNotFoundError:
      self._print(f"警告: 找不到文件 {filename}")
      self.logger.warning(f"找不到文件: {filename}")
      return {}
    except Exception as e:
      self._print(f"警告: 加载 {filename} 时出错: {e}")
      self.logger.error(f"加载 {filename} 时出错: {e}")
      return {}

  def read_recipes(self):
    """读取配方文件，解析物品代码和数量"""
    parsed_recipes = {}

    for recipe_name, recipe_string in self.recipes_data.items():
      parts = recipe_string.split("/")

      if len(parts) >= 4:  # 确保有足够的部分，包括第3索引的布尔值
        # 解析材料
        materials = []
        material_parts = parts[0].split()

        for i in range(0, len(material_parts), 2):
          if i + 1 < len(material_parts):
            item_code = material_parts[i]
            quantity = int(material_parts[i + 1])
            materials.append({"code": item_code, "quantity": quantity})

        # 解析产品（格式：物品代码 数量）
        product_parts = parts[2].split()
        product_code = product_parts[0]
        product_quantity = int(product_parts[1]) if len(product_parts) > 1 else 1

        # 获取第3索引的布尔值，判断产品类型
        is_bigcraftable = parts[3].lower() == "true"

        parsed_recipes[recipe_name] = {
          "materials": materials,
          "product": {"code": product_code, "quantity": product_quantity, "is_bigcraftable": is_bigcraftable},
        }

    self.logger.info(f"成功解析 {len(parsed_recipes)} 个配方")
    return parsed_recipes

  def get_item_info(self, item_code, is_bigcraftable=None):
    """
    统一的物品信息获取方法
    返回: (localization_key, clean_code, normalized_code)

    参数:
    - item_code: 原始物品代码
    - is_bigcraftable: 是否为大型可制作物品（对于材料，此参数为None，需要从前缀判断）
    """
    # 处理负数物品代码
    if item_code.startswith("-"):
      return None, item_code, item_code

    # 提取clean_code（去除前缀）
    clean_code = item_code
    has_prefix = False
    if item_code.startswith("(") and ")" in item_code:
      prefix_end = item_code.index(")") + 1
      clean_code = item_code[prefix_end:]
      has_prefix = True

    # 确定物品类型
    # 如果is_bigcraftable参数明确指定（产品情况）
    if is_bigcraftable is not None:
      search_bigcraftable = is_bigcraftable
    # 如果是材料，根据前缀判断
    elif has_prefix and item_code.startswith("(BC)"):
      search_bigcraftable = True
    else:
      search_bigcraftable = False

    # 查找物品信息
    if search_bigcraftable:
      if clean_code in self.bigcraftables_data:
        display_name = self.bigcraftables_data[clean_code].get("DisplayName", "")
        match = re.search(r":(\w+_Name)\]", display_name)
        if match:
          return match.group(1), clean_code, f"(BC){clean_code}"
    else:
      if clean_code in self.objects_data:
        display_name = self.objects_data[clean_code].get("DisplayName", "")
        match = re.search(r":(\w+_Name)\]", display_name)
        if match:
          return match.group(1), clean_code, f"(O){clean_code}"

    return None, clean_code, item_code

  def get_item_name(self, item_code, is_bigcraftable=None):
    """
    统一的物品名称获取方法
    返回: (name, normalized_code)
    """
    # 获取物品信息
    localization_key, clean_code, normalized_code = self.get_item_info(item_code, is_bigcraftable)

    if localization_key:
      # 根据normalized_code判断使用哪个本地化文件
      if normalized_code.startswith("(BC)"):
        localization_data = self.bigcraftables_localization
      else:
        localization_data = self.objects_localization

      if localization_key in localization_data:
        return localization_data[localization_key], normalized_code

    return f"未知物品({item_code})", item_code

  def get_all_recipes_with_names(self):
    """获取所有配方并转换物品代码为中文名称"""
    recipes = self.read_recipes()

    for recipe_name, recipe_info in recipes.items():
      # 转换材料名称（材料不传is_bigcraftable参数，让方法自动判断）
      for material in recipe_info["materials"]:
        material["name"], material["normalized_code"] = self.get_item_name(material["code"])

      # 转换产品名称（产品传入is_bigcraftable参数）
      product = recipe_info["product"]
      product["name"], product["normalized_code"] = self.get_item_name(
        product["code"], product.get("is_bigcraftable", False)
      )

    return recipes

  def calculate_material_usage(self):
    """统计所有配方中每种材料的总使用量"""
    recipes = self.get_all_recipes_with_names()
    material_usage = defaultdict(int)

    for recipe_name, recipe_info in recipes.items():
      for material in recipe_info["materials"]:
        material_name = material["name"]
        quantity = material["quantity"]
        material_usage[material_name] += quantity

    # 转换为普通字典并按使用量排序
    sorted_usage = dict(sorted(material_usage.items(), key=lambda x: x[1], reverse=True))
    self.logger.info(f"统计完成，共有 {len(sorted_usage)} 种材料")
    return sorted_usage

  def display_recipes_info(self):
    """显示所有配方信息"""
    recipes = self.get_all_recipes_with_names()

    self._print("\n=== 配方信息 ===")
    for recipe_name, recipe_info in recipes.items():
      product = recipe_info["product"]
      self._print(f"\n{recipe_name}: {product['name']} [{product['normalized_code']}] ×{product['quantity']}")

      for material in recipe_info["materials"]:
        self._print(f" - {material['name']} [{material['normalized_code']}] ×{material['quantity']:<3}")

  def display_material_statistics(self):
    """显示材料使用统计"""
    usage = self.calculate_material_usage()

    self._print("\n=== 材料使用统计 ===")

    # 设置列宽
    name_column_width = 20  # 材料名称列的显示宽度

    # 打印表头
    header_name = StringUtils.pad_to_width("材料名称", name_column_width)
    self._print(f"{header_name}| {'总使用量':>8}")
    self._print("-" * (name_column_width + 12))

    # 打印数据
    for material_name, total_quantity in usage.items():
      padded_name = StringUtils.pad_to_width(material_name, name_column_width)
      self._print(f"{padded_name}| {total_quantity:>8}")

  def show_performance_stats(self):
    """显示性能统计信息"""
    # 停止监控并获取统计信息
    self.perf_monitor.stop()
    stats_text = self.perf_monitor.format_stats()
    self._print(f"\n{stats_text}")

    # 记录到日志
    stats = self.perf_monitor.get_stats()
    self.logger.info(
      f"程序运行完成 - 总时间: {stats['elapsed_ms']:.2f}ms, 内存增量: {stats['memory_delta_mb']:.2f}MB"
    )

  def export_statistics_to_json(self):
    """将统计结果导出为JSON文件"""
    # 获取所有配方和材料统计
    recipes = self.get_all_recipes_with_names()
    material_usage = self.calculate_material_usage()

    # 构建导出数据
    export_data = {
      "生成时间": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      "配方总数": len(recipes),
      "材料种类": len(material_usage),
      "材料使用统计": material_usage,
      "配方详情": {},
    }

    # 添加配方详情
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

    # 保存到文件
    output_path = Path(__file__).parent.parent / "json" / "recipe_statistics.json"
    FileUtils.write_json(export_data, output_path)
    self._print(f"\n统计数据已导出到: {output_path}")
    self.logger.info(f"统计数据已导出到: {output_path}")


# 使用示例
if __name__ == "__main__":
  try:
    # 创建解析器实例
    parser = RecipeParser()

    # 显示配方信息
    parser.display_recipes_info()

    # 显示材料统计
    parser.display_material_statistics()

    # 导出统计数据到JSON
    # parser.export_statistics_to_json()

    # 显示性能统计
    parser.show_performance_stats()

    # 保存输出到文件
    parser.save_output()

  except Exception as e:
    print(f"发生错误: {e}")
    import traceback

    traceback.print_exc()
