import time
import sys
import tracemalloc
import argparse
import json
import os
import hashlib
from collections import defaultdict
from itertools import combinations
from typing import Any

import numpy as np


class Fish:
  """
  存储鱼数据的类

  Attributes:
      ID: 鱼的 DisplayName
      Precedence: 鱼的“优先级”
      SurvivalProb: 从 Locations 里读出来经过 GetChance 算出来的概率
      HookProb: 从 Fish 里读出来经过整个 CheckGenericFishRequirements 方法算出来的概率
  """
  ID: str = ""
  Precedence: int = 0
  SurvivalProb: float = 0.0
  HookProb: float = 0.0

  def __init__(self, ID: str, Precedence: int, SurvivalProb: float, HookProb: float):
    self.ID = ID
    self.Precedence = Precedence
    self.SurvivalProb = SurvivalProb
    self.HookProb = HookProb


def calc_fishing_prob(fishes: list[Fish]) -> dict[Any, Any]:
  """
  计算优先级排序的方法

  Args:
      fishes (list[Fish]): 传入的鱼

  Returns:
      dict[Any, Any]: _description_
  """
  # 按优先级分组
  groups_by_precedence = defaultdict(list)
  for fish in fishes:
    groups_by_precedence[fish.Precedence].append(fish)

  sorted_precedences = sorted(groups_by_precedence.keys())
  final_probs = {}

  # 存储每个优先级组的精确阻挡概率
  group_exact_block_probs = {}

  for group_idx, precedence in enumerate(sorted_precedences):
    group = groups_by_precedence[precedence]
    n = len(group)

    # 计算到达当前组的概率
    reach_probability = 1.0
    for prev_precedence in sorted_precedences[:group_idx]:
      reach_probability *= 1 - group_exact_block_probs[prev_precedence]

    # 使用NumPy数组存储组内每条鱼的基础概率
    group_probs = np.array([fish.SurvivalProb * fish.HookProb for fish in group])

    # 计算每条鱼的精确期望概率
    group_expected_probs = {}

    for i, fish in enumerate(group):
      p_i = group_probs[i]

      if n == 1:
        expected_prob = p_i
      else:
        # 精确计算每个位置的概率
        total_prob = 0.0

        # 获取其他鱼的概率
        other_probs = np.delete(group_probs, i)

        for position in range(n):
          if position == 0:
            # 第一个位置，没有其他鱼阻挡
            prob_at_position = p_i
          else:
            # 使用NumPy优化组合计算
            if position < n - 1:
              # 预计算所有组合的"未被钓到"概率
              combos = list(combinations(range(n - 1), position))

              # 向量化计算
              combo_array = np.array(combos)
              # 创建一个矩阵来存储每个组合中每条鱼的概率
              prob_matrix = other_probs[combo_array]
              # 计算每个组合的"都不被钓"概率
              not_caught_probs = np.prod(1 - prob_matrix, axis=1)
              # 平均概率
              avg_prob_not_caught = np.mean(not_caught_probs)
            else:
              # position == n-1，所有其他鱼都在前面
              avg_prob_not_caught = np.prod(1 - other_probs)

            prob_at_position = p_i * avg_prob_not_caught

          # 该鱼在position位置的概率是1/n
          total_prob += prob_at_position / n

        expected_prob = total_prob

      group_expected_probs[fish.ID] = expected_prob
      final_probs[fish.ID] = reach_probability * expected_prob

    # 计算该组的精确阻挡概率
    group_exact_block_probs[precedence] = sum(group_expected_probs.values())

  return final_probs


def run(arg) -> None:
  """
  读取鱼类数据 json 文件，反序列化后调用 calc_fishing_prob 计算具体概率，并写入文件，命令行使用样例：

  python CalcFishesProb.py run [json绝对路径，工作目录对的话相对路径也行]

  Args:
    arg: 命令行传入参数，仅包含 json_file 路径
  """
  _run(arg.json_file)


def _run(json_f, delete_secret_notes=True) -> None:
  """
  run 函数的内部调用
  """
  with open(json_f, "r", encoding="utf-8") as f:
    fish_list = json.load(f)
    fish_data = [
      Fish(
        fish["ID"],
        int(fish["Precedence"]),
        float(fish["SurvivalProb"]),
        float(fish["HookProb"])
      )
      for fish in fish_list
    ]

  # 删除秘密纸条
  if delete_secret_notes:
    for fish in fish_data:
      if fish.ID == "秘密纸条":
        fish_data.remove(fish)
        break

  # 执行计算
  results = calc_fishing_prob(fish_data)

  # 输出 txt 结果
  output_lines1 = ["钓鱼概率计算结果",
                  "=" * 50,
                  f"{'鱼ID':<6} {'概率(%)':<20}",
                  "-" * 50]

  output_lines2 = ["鱼ID,概率(%)"]

  for fish_id in sorted(results.keys()):
    probability_percent = results[fish_id] * 100
    output_lines1.append(f"{fish_id:<6} {probability_percent:.10f}")
    output_lines2.append(f"{fish_id},{probability_percent:.10f}")

  filename = json_f.split(".")[0]
  output_lines1.append("\n" + "=" * 50)

  # 写入 out.txt
  with open(filename + ".txt", "w", encoding="utf-8") as out_file:
    out_file.write("\n".join(output_lines1))

  # 写入 out.csv
  with open(filename + ".csv", "w", encoding="gbk") as out_file:
    out_file.write("\n".join(output_lines2))

  print(filename + "计算完成")


def merge_duplicate_fish_data(location_dir):
  """
  合并指定地点目录下连续重复的鱼类数据文件。
  注意，重命名后丢失了文件名内的最大钓鱼区数据，在此处注明：
    - 沙漠：2
    - 秘密森林：3
    - 姜岛西部_河流：3
    - 姜岛北部：1

  运行完成后，需要手动将 Locations 目录内的所有文件移动到 Output 目录下
  Args:
      location_dir: 地点文件夹路径
  """
  # 获取目录下所有json文件
  all_files = [f for f in os.listdir(location_dir) if f.endswith('.json')]

  # 按季节和天气分组
  file_groups: dict[ tuple, list[tuple] ] = {}
  for filename in all_files:
    try:
      # 解析文件名: 季节,天气,时间,10,5.json
      parts = filename.split(',')
      season = parts[0]
      weather = parts[1]
      time_str = parts[2]
      time_val = int(time_str)  # 将时间转换为整数用于排序

      group_key : tuple = (season, weather)
      file_path = os.path.join(location_dir, filename)

      if group_key not in file_groups:
        file_groups[group_key] = []

      file_groups[group_key].append((time_val, filename, file_path))
    except (IndexError, ValueError):
      print(f"跳过无效文件名: {filename}")
      continue

  # 处理每个分组
  delete_count = 0
  for group_key, files in file_groups.items():
    season, weather = group_key
    # 按时间排序 (630, 730, ..., 2530)
    files.sort(key=lambda x: x[0])

    print(f"\n处理分组: {season}, {weather}")
    print(f"找到 {len(files)} 个文件")

    current_hash = None
    files_to_keep : list[tuple] = []
    files_to_remove : list[tuple] = []

    # 1. 合并连续重复的文件
    for time_val, filename, file_path in files:
      # 计算文件哈希
      with open(file_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()

      # 第一个文件或遇到新哈希值
      if current_hash is None or file_hash != current_hash:
        current_hash = file_hash
        files_to_keep.append((time_val, filename, file_path))
        print(f"保留文件: {filename} (新哈希块开始)")
      else:
        files_to_remove.append((time_val, filename, file_path))
        print(f"标记删除: {filename} (与前一文件重复)")

    # 2. 删除重复文件
    for file_to_remove in files_to_remove:
      os.remove(file_to_remove[2])
      print(f"已删除: {os.path.basename(file_to_remove[2])}")

    # 3. 重命名保留的文件
    if not files_to_keep:
      continue

    print("\n开始重命名保留文件:")

    # 对保留文件按时间排序（虽然应该已经有序，但确保安全）
    files_to_keep.sort(key=lambda x: x[0])

    for i in range(len(files_to_keep)):
      time_val, filename, file_path = files_to_keep[i]

      # 计算开始时间（向下取整到整百）
      start = (time_val - 30)

      # 计算结束时间
      if i < len(files_to_keep) - 1:
        # 下一个保留文件的时间（向下取整到整百）
        end = (files_to_keep[i + 1][0] - 30)
      else:
        # 最后一个文件，结束时间为2600
        end = 2600

      new_filename = f"{season},{weather},{start},{end}.json"
      new_path = os.path.join(location_dir, new_filename)

      # 重命名文件
      os.rename(file_path, new_path)
      print(f"重命名: {filename} -> {new_filename}")

    delete_count += len(files_to_remove)
    print(f"分组处理完成: 保留 {len(files_to_keep)} 个文件, 删除 {len(files_to_remove)} 个文件")

  print(f"合计删除 {delete_count} 个重复文件")

def main() -> None:
  """
  命令行调用主函数
  """
  parser = argparse.ArgumentParser()
  subparsers = parser.add_subparsers()

  parser_func = subparsers.add_parser("run")
  parser_func.add_argument("json_file", type=str, help="JSON 文件路径，包含鱼数据")
  parser_func.set_defaults(func=run)

  args = parser.parse_args()

  try:
    result = args.func(args)
    if isinstance(result, str):
      print(result)
      sys.exit(0)
    else:
      sys.exit(result)
  except Exception as e:
    print(f"Error: {str(e)}", file=sys.stderr)
    sys.exit(99)


if __name__ == "__main__":
  # main()
  # 内存追踪
  tracemalloc.start()

  # 记录时间
  start_time = time.perf_counter()

  locations = os.listdir("Locations")
  for location in locations:
    merge_duplicate_fish_data(os.path.join("Locations", location))
    jsons = os.listdir(os.path.join("Locations", location))
    for fish_json in jsons:
      if fish_json.endswith(".json"):
        _run(os.path.join("Locations", location, fish_json))

  end_time = time.perf_counter()

  # 获取内存使用情况
  current_memory, peak_memory = tracemalloc.get_traced_memory()
  tracemalloc.stop()

  # 计算运行时间（毫秒）
  execution_time_ms = (end_time - start_time) * 1000

  print("性能统计")
  print("=" * 50)
  print(f"峰值内存使用: {peak_memory:,} bytes")
  print(f"运行时间: {execution_time_ms:.3f} ms")
