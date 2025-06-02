import math
import os
import time
import tracemalloc
from collections import defaultdict
from itertools import combinations, permutations

import psutil


def calc_fishing_probs_optimized(fish_list):
  """优化方法：考虑所有组合但不枚举完整排列"""
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

    # 计算组内每条鱼的基础概率
    group_probs = [fish["survival_prob"] * fish["hook_prob"] for fish in group]

    # 计算每条鱼的精确期望概率
    group_expected_probs = {}

    for i, fish in enumerate(group):
      p_i = group_probs[i]

      if n == 1:
        expected_prob = p_i
      else:
        # 精确计算每个位置的概率
        total_prob = 0.0

        for position in range(n):
          if position == 0:
            # 第一个位置，没有其他鱼阻挡
            prob_at_position = p_i
          else:
            # 需要计算前面position条鱼都没被钓到的概率
            # 从其他n-1条鱼中选position条
            other_indices = [j for j in range(n) if j != i]

            sum_prob_not_caught = 0.0
            num_combinations = 0

            # 枚举前面position条鱼的所有可能组合
            for combo in combinations(other_indices, position):
              prob_none_caught = 1.0
              for j in combo:
                prob_none_caught *= 1 - group_probs[j]
              sum_prob_not_caught += prob_none_caught
              num_combinations += 1

            # 平均概率
            avg_prob_not_caught = sum_prob_not_caught / num_combinations
            prob_at_position = p_i * avg_prob_not_caught

          # 该鱼在position位置的概率是1/n
          total_prob += prob_at_position / n

        expected_prob = total_prob

      group_expected_probs[fish["ID"]] = expected_prob
      final_probs[fish["ID"]] = reach_probability * expected_prob

    # 计算该组的精确阻挡概率
    group_exact_block_probs[precedence] = sum(group_expected_probs.values())

  return final_probs


def calc_fishing_probs_original(fish_list):
  """原始方法：枚举所有可能的排列并计算概率"""
  precedence_groups = defaultdict(list)
  for fish in fish_list:
    precedence_groups[fish["Precedence"]].append(fish)

  sorted_precedences = sorted(precedence_groups.keys())

  def generate_all_permutations(groups, precedences):
    if not precedences:
      return [[]]

    current_precedence = precedences[0]
    current_group = groups[current_precedence]
    group_perms = list(permutations(current_group))
    remaining_perms = generate_all_permutations(groups, precedences[1:])

    all_perms = []
    for group_perm in group_perms:
      for remaining_perm in remaining_perms:
        all_perms.append(list(group_perm) + remaining_perm)

    return all_perms

  all_arrangements = generate_all_permutations(precedence_groups, sorted_precedences)
  fish_probs = defaultdict(float)
  num_arrangements = len(all_arrangements)

  for arrangement in all_arrangements:
    cumulative_prob = 0.0
    for fish in arrangement:
      current_prob = (1 - cumulative_prob) * fish["survival_prob"] * fish["hook_prob"]
      fish_probs[fish["ID"]] += current_prob
      cumulative_prob += current_prob

  for fish_id in fish_probs:
    fish_probs[fish_id] /= num_arrangements

  return dict(fish_probs)


def measure_memory_and_time(func, fish_data, method_name):
  """测量函数的内存使用和运行时间"""
  # 获取当前进程
  process = psutil.Process(os.getpid())

  # 记录初始内存
  initial_memory = process.memory_info().rss / 1024 / 1024  # MB

  # 使用tracemalloc进行更精确的内存追踪
  tracemalloc.start()

  # 记录开始时间
  start_time = time.time()

  # 执行函数
  result = func(fish_data)

  # 记录结束时间
  end_time = time.time()

  # 获取内存峰值
  current, peak = tracemalloc.get_traced_memory()
  tracemalloc.stop()

  # 获取最终内存
  final_memory = process.memory_info().rss / 1024 / 1024  # MB

  # 计算统计信息
  execution_time = end_time - start_time
  peak_memory_mb = peak / 1024 / 1024
  current_memory_mb = current / 1024 / 1024
  process_memory_increase = final_memory - initial_memory

  return {
    "result": result,
    "execution_time": execution_time,
    "peak_memory_mb": peak_memory_mb,
    "current_memory_mb": current_memory_mb,
    "process_memory_increase_mb": process_memory_increase,
    "method_name": method_name,
  }


def main():
  # 创建20条鱼的列表
  fish_data = []

  # 定义优先级分配
  precedences = [-100, -20, -10] + [0] * 15 + [10, 20]

  # 生成A-T的鱼（20条）
  for i in range(12):
    fish_id = chr(65 + i)  # A-T
    precedence = precedences[i]
    # 概率从0.05开始，每次递增0.03
    prob = 0.05 + i * 0.03

    fish_data.append({"ID": fish_id, "Precedence": precedence, "survival_prob": prob, "hook_prob": prob})

  print("=" * 80)
  print("钓鱼概率计算 - 20条鱼测试（含内存使用统计）")
  print("=" * 80)

  print("\n计算中...")

  # 测量原始方法
  original_stats = measure_memory_and_time(calc_fishing_probs_original, fish_data, "原始方法")

  # 稍微等待一下，让内存稳定
  time.sleep(0.1)

  # 测量精确优化方法
  exact_stats = measure_memory_and_time(calc_fishing_probs_optimized, fish_data, "精确优化")

  # 获取结果
  result_original = original_stats["result"]
  result_exact = exact_stats["result"]

  # 输出结果
  print("\n" + "=" * 80)
  print("计算结果对比")
  print("=" * 80)
  print(f"\n{'鱼ID':<6} {'原始方法(%)':<20} {'精确优化(%)':<20} {'绝对误差':<20} {'相对误差(%)':<20}")
  print("-" * 90)

  total_absolute_error = 0
  total_relative_error = 0
  max_absolute_error = 0
  max_relative_error = 0

  for fish_id in sorted(result_original.keys()):
    orig = result_original[fish_id]
    exact = result_exact[fish_id]

    # 转换为百分比
    orig_percent = orig * 100
    exact_percent = exact * 100

    # 计算误差
    absolute_error = abs(orig - exact)
    relative_error = abs(orig - exact) / orig * 100 if orig > 0 else 0

    total_absolute_error += absolute_error
    total_relative_error += relative_error
    max_absolute_error = max(max_absolute_error, absolute_error)
    max_relative_error = max(max_relative_error, relative_error)

    print(
      f"{fish_id:<6} {orig_percent:<20.10f} {exact_percent:<20.10f} {absolute_error:<20.10f} {relative_error:<20.10f}"
    )

  # 误差统计
  print("\n" + "=" * 80)
  print("误差统计")
  print("=" * 80)
  print(f"平均绝对误差: {total_absolute_error / len(result_original):.10f}")
  print(f"最大绝对误差: {max_absolute_error:.10f}")
  print(f"平均相对误差: {total_relative_error / len(result_original):.10f}%")
  print(f"最大相对误差: {max_relative_error:.10f}%")

  # 性能对比
  print("\n" + "=" * 80)
  print("性能对比")
  print("=" * 80)

  # 时间对比
  print("\n运行时间:")
  print(f"  原始方法: {original_stats['execution_time']:.6f} 秒")
  print(f"  精确优化方法: {exact_stats['execution_time']:.6f} 秒")
  print(f"  速度提升: {original_stats['execution_time'] / exact_stats['execution_time']:.2f}x")

  # 内存对比
  print("\n内存使用:")
  print("  原始方法:")
  print(f"    - 峰值内存: {original_stats['peak_memory_mb']:.2f} MB")
  print(f"    - 当前内存: {original_stats['current_memory_mb']:.2f} MB")
  print(f"    - 进程内存增长: {original_stats['process_memory_increase_mb']:.2f} MB")

  print("  精确优化方法:")
  print(f"    - 峰值内存: {exact_stats['peak_memory_mb']:.2f} MB")
  print(f"    - 当前内存: {exact_stats['current_memory_mb']:.2f} MB")
  print(f"    - 进程内存增长: {exact_stats['process_memory_increase_mb']:.2f} MB")

  print("\n内存使用对比:")
  print(f"  峰值内存减少: {(1 - exact_stats['peak_memory_mb'] / original_stats['peak_memory_mb']) * 100:.1f}%")
  print(f"  内存效率提升: {original_stats['peak_memory_mb'] / exact_stats['peak_memory_mb']:.2f}x")

  # 显示优先级分组信息
  print("\n" + "=" * 80)
  print("优先级分组信息")
  print("=" * 80)
  groups = defaultdict(list)
  for fish in fish_data:
    groups[fish["Precedence"]].append(fish["ID"])

  for precedence in sorted(groups.keys()):
    print(f"优先级 {precedence}: {', '.join(groups[precedence])} ({len(groups[precedence])}条鱼)")

  # 计算优先级0组的排列数
  priority_0_count = len(groups[0])
  print(f"\n优先级0组的排列数: {math.factorial(priority_0_count):,}")


if __name__ == "__main__":
  main()
