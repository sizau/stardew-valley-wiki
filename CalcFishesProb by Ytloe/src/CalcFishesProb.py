import time
import sys
import tracemalloc
import argparse
import json
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

  python CalcFishesProb.py run [json绝对路径]

  Args:
    arg: 命令行传入参数，仅包含 json_file 路径
  """
  with open(arg.json_file, "r", encoding="utf-8") as f:
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

  # 内存追踪
  tracemalloc.start()

  # 记录时间
  start_time = time.perf_counter()

  # 执行计算
  results = calc_fishing_prob(fish_data)

  end_time = time.perf_counter()

  # 获取内存使用情况
  current_memory, peak_memory = tracemalloc.get_traced_memory()
  tracemalloc.stop()

  # 计算运行时间（毫秒）
  execution_time_ms = (end_time - start_time) * 1000

  # 输出结果
  output_lines = ["钓鱼概率计算结果",
                  "=" * 50,
                  f"{'鱼ID':<6} {'概率(%)':<20}",
                  "-" * 50]

  for fish_id in sorted(results.keys()):
    probability_percent = results[fish_id] * 100
    output_lines.append(f"{fish_id:<6} {probability_percent:.10f}")

  output_lines.append("\n" + "=" * 50)
  output_lines.append("性能统计")
  output_lines.append("=" * 50)
  output_lines.append(f"峰值内存使用: {peak_memory:,} bytes")
  output_lines.append(f"运行时间: {execution_time_ms:.3f} ms")

  # 写入 out.txt，覆盖旧内容
  with open("out.txt", "w", encoding="utf-8") as out_file:
    out_file.write("\n".join(output_lines))


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
  main()
