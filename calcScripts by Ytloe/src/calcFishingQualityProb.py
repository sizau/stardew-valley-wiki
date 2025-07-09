def calculate_fish_quality_probabilities(water_distance, fishing_level, uses_favorite_bait=False):
  """计算鱼类品质概率分布

  参数:
      water_distance (float): 净水距离
      fishing_level (int): 钓鱼技能等级
      uses_favorite_bait (bool): 是否使用最爱鱼饵（默认False）

  返回:
      dict: 包含概率分布和统计信息的字典
          - 'probabilities': (普通品质概率, 银星品质概率, 金星品质概率)
          - 'min_percentile': 最小尺寸百分位
          - 'max_percentile': 最大尺寸百分位
  """
  # 计算基础参数
  min_size_contribution = 1 + fishing_level // 2
  max_size_contribution = max(6, min_size_contribution)
  if min_size_contribution == max_size_contribution:
    max_size_contribution += 1

  # 计算随机值范围
  size_contribution_range = list(range(min_size_contribution, max_size_contribution))
  num_size_contributions = len(size_contribution_range)
  num_fluctuation_values = 21  # 波动范围：-10到10
  total_combinations = num_size_contributions * num_fluctuation_values

  # 初始化品质计数器和统计值
  quality_counts = [0, 0, 0]  # [普通, 银星, 金星]
  min_percentile = float("inf")
  max_percentile = float("-inf")

  # 遍历所有可能的组合
  for size_contribution in size_contribution_range:
    # 计算基础尺寸百分比
    base_size_percentile = water_distance / 5.0 * size_contribution / 5.0

    # 应用鱼饵加成
    if uses_favorite_bait:
      base_size_percentile *= 1.2

    # 遍历波动因子
    for fluctuation_percent in range(-10, 11):
      # 应用随机波动
      final_size_percentile = base_size_percentile * (1.0 + fluctuation_percent / 100.0)

      # 限制在有效范围内
      final_size_percentile = max(0.0, min(1.0, final_size_percentile))

      # 更新统计值
      min_percentile = min(min_percentile, final_size_percentile)
      max_percentile = max(max_percentile, final_size_percentile)

      # 确定品质等级
      if final_size_percentile < 0.33:
        quality_index = 0  # 普通
      elif final_size_percentile < 0.66:
        quality_index = 1  # 银星
      else:
        quality_index = 2  # 金星

      quality_counts[quality_index] += 1

  # 计算概率
  normal_probability = quality_counts[0] / total_combinations
  silver_probability = quality_counts[1] / total_combinations
  gold_probability = quality_counts[2] / total_combinations

  return {
    "probabilities": (normal_probability, silver_probability, gold_probability),
    "min_percentile": min_percentile,
    "max_percentile": max_percentile,
  }


class StringUtils:
  @staticmethod
  def pad_to_width(text, width):
    """简单的字符串填充工具"""
    return text.ljust(width)


def display_fish_quality_analysis():
  """显示鱼类品质计算结果"""
  for water_distance in range(0, 6):
    if water_distance == 4:
      continue
    print('{|class = "wikitable mw-collapsible mw-collapsed";')
    print(f'! colspan="2" |离岸距离: {water_distance}')
    print('! colspan="3" | 品质概率 ')
    print('! colspan="2" | 完美尺寸（鲶鱼）')
    print("|-")
    print("! 钓鱼等级 !! Size Factor")
    print("! 普通 !! [[File:Silver Quality.png|20px]] 银星 !! [[File:Gold Quality.png|20px]] 金星 ")
    print("! 英寸 !! 厘米")

    for fishing_level in range(0, 20, 2):
      result = calculate_fish_quality_probabilities(water_distance, fishing_level)
      normal_prob, silver_prob, gold_prob = result["probabilities"]
      min_pct = round(result["min_percentile"], 10)
      max_pct = round(result["max_percentile"], 10)

      # 计算尺寸
      min_inches = int(12 + (72 - 12) * min_pct) + 1
      min_centimeters = round(min_inches * 2.54)
      max_inches = int(12 + (72 - 12) * max_pct) + 1
      max_centimeters = round(max_inches * 2.54)

      print("|-")

      column1 = StringUtils.pad_to_width(f"| {fishing_level} ~ {fishing_level + 1} ", 10)
      column2 = f"|| {min_pct:5} ~ {max_pct:<5} "
      column3 = f"|| {normal_prob:<7.2%} || {silver_prob:<7.2%} || {gold_prob:<7.2%} "
      column4 = f"|| {min_inches:>2} ~ {max_inches:<2} || {min_centimeters:>3} ~ {max_centimeters:<3}"

      print(column1 + column2 + column3 + column4)
    print("|}\n")


if __name__ == "__main__":
  display_fish_quality_analysis()
