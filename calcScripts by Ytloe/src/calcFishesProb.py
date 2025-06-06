import time
import tracemalloc
from collections import defaultdict
from itertools import combinations
from typing import Any

import numpy as np


def calc_fishing_prob(fish_list: list[dict]) -> dict[Any, Any]:
  """
  计算优先级排序的方法

  Args:
      fish_list (list[dict]): 传入鱼的优先级和存活概率和咬钩概率，具体看下面的main

  Returns:
      dict[Any, Any]: _description_
  """
  # 按优先级分组
  groups_by_precedence = defaultdict(list)
  for fish in fish_list:
    groups_by_precedence[fish["Precedence"]].append(fish)

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
    group_probs = np.array([fish["survival_prob"] * fish["hook_prob"] for fish in group])

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

      group_expected_probs[fish["ID"]] = expected_prob
      final_probs[fish["ID"]] = reach_probability * expected_prob

    # 计算该组的精确阻挡概率
    group_exact_block_probs[precedence] = sum(group_expected_probs.values())

  return final_probs


def main():
  # 创建20条鱼的数据
  fish_data = []
  precedences = [-100, -20, -10] + [0] * 15 + [10, 20]

  for i in range(20):
    fish_id = chr(65 + i)  # A-T
    precedence = precedences[i]
    prob = 0.05 + i * 0.03

    fish_data.append({"ID": fish_id, "Precedence": precedence, "survival_prob": prob, "hook_prob": prob})
    # survival_prob：从Locations里读出来经过get_chance算出来的概率
    # hook_prob：从Fish里读出来经过整个CheckGenericFishRequirements方法算出来的概率

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
  print("钓鱼概率计算结果")
  print("=" * 50)
  print(f"{'鱼ID':<6} {'概率(%)':<20}")
  print("-" * 50)

  for fish_id in sorted(results.keys()):
    probability_percent = results[fish_id] * 100
    print(f"{fish_id:<6} {probability_percent:.10f}")

  print("\n" + "=" * 50)
  print("性能统计")
  print("=" * 50)
  print(f"峰值内存使用: {peak_memory:,} bytes")
  print(f"运行时间: {execution_time_ms:.3f} ms")


if __name__ == "__main__":
  main()
