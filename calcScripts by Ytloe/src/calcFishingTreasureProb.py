import itertools
import operator
from collections import defaultdict
from functools import reduce

# --- 玩家状态与游戏常量 ---
# 修改此处的字典值以模拟不同的游戏内场景。
PLAYER_STATS = {
  "goldenTreasure": True,
  "isSpring": True,
  "isBeach": False,
  "numberOfFishCaught": 1,  # 用于万能鱼饵和挑战鱼饵
  "hasWildBaitRecipe": True,
  "isQiBeansOrderActive": True,
  "averageDailyLuck": 0.0,
  "masteryFishing": True,
  "masteryForaging": True,
  "clearWaterDistance": 5,
  "luckLevel": 0,
  "fishingLevel": 10,
  "lostBooksFound": 21,  # 21就是全收集
  "hasLostBookMail": True,
  "archaeologyFoundCount": 1,
  "dailyLuck": 0.0,
  "hasWeapon14": False,
  "hasWeapon51": False,
  "hasFarmEternalMail": True,
  "fishingTreasuresStat": 5,
  "hasBookRoe": True,
  "mailReceived_roeBookDropped": False,
}

# --- 核心计算脚本 ---


def calculate_single_loop_prospects(consts):
  """
  第一阶段：计算单次循环的条件概率。

  本函数的目标是：假设已进入`while`循环体，计算出在该次循环中，
  获得每种物品的条件概率，以及发生中断事件的条件概率。
  它精确地模拟了源码中的每一个分支和随机检定。
  """
  p_components = defaultdict(list)
  item_order = []

  # 辅助函数，用于添加物品的概率“组件”并维持其在代码中出现的顺序。
  # 一个物品可能有多个来源，因此其总概率由多个组件构成。
  def add_prob(item_id, probability):
    if probability > 1e-12:  # 忽略可忽略不计的极小概率
      if item_id not in item_order:
        item_order.append(item_id)
      p_components[item_id].append(probability)

  # --- 循环体顶部的独立事件 ---
  if consts["isSpring"] and not consts["isBeach"]:
    add_prob("(O)273", 0.1)
  if consts["numberOfFishCaught"] > 1 and consts["hasWildBaitRecipe"]:
    add_prob("(O)774", 0.5)
  if consts["isQiBeansOrderActive"]:
    add_prob("(O)890", 0.33)
  box_id = "(O)GoldenMysteryBox" if consts["masteryFishing"] else "(O)MysteryBox"
  add_prob(box_id, 0.08 + consts["averageDailyLuck"] / 5.0)
  if consts["masteryForaging"]:
    add_prob("(O)GoldenAnimalCracker", 0.05)

  # --- 黄金宝箱与标准宝箱的分支逻辑 ---
  prob_enter_standard_block = 1.0  # 默认进入标准宝箱逻辑的概率
  if consts["goldenTreasure"]:
    prob_enter_standard_block = 0.5  # 黄金宝箱模式下，有50%概率“掉落”到标准逻辑
    prob_golden_path = 0.5
    prob_golden_case = prob_golden_path / 13.0
    add_prob("(O)337", prob_golden_case)
    add_prob("RaccoonSeed", prob_golden_case)
    for i in range(5):
      add_prob(f"(O)SkillBook_{i}", prob_golden_case / 5.0)
    add_prob("(O)213", prob_golden_case)
    add_prob("(O)872", prob_golden_case)
    add_prob("(O)687", prob_golden_case)
    add_prob("(O)ChallengeBait", prob_golden_case)
    add_prob("(O)703", prob_golden_case)
    add_prob("(O)StardropTea", prob_golden_case)
    add_prob("(O)797", prob_golden_case)
    add_prob("(O)733", prob_golden_case)
    add_prob("(O)728", prob_golden_case)
    add_prob("(O)SonarBobber", prob_golden_case)

  # --- 标准宝箱 switch(4) 块 ---
  prob_case_base = prob_enter_standard_block * 0.25

  # Case 0: 资源（精确组合概率模型）
  if consts["clearWaterDistance"] >= 5:
    add_prob("(O)386", prob_case_base * 0.03)
  prob_case0_main_block = prob_case_base * (1.0 - (0.03 if consts["clearWaterDistance"] >= 5 else 0))
  always_present = ["(O)382"]
  if consts["clearWaterDistance"] >= 4:
    always_present.append("(O)384")
  conditional_items = [("(O)378", 0.6), ("(O)388", 0.6), ("(O)390", 0.6)]
  if consts["clearWaterDistance"] >= 3:
    conditional_items.append(("(O)380", 0.6))

  # 遍历所有可能的列表组合，计算每种组合的加权概率
  for combo in itertools.product([True, False], repeat=len(conditional_items)):
    prob_combo = 1.0
    final_list = always_present[:]
    for i in range(len(conditional_items)):
      item_name, item_prob = conditional_items[i]
      if combo[i]:
        prob_combo *= item_prob
        final_list.append(item_name)
      else:
        prob_combo *= 1 - item_prob
    if final_list:
      prob_of_being_chosen = 1 / len(final_list)
      for item in final_list:
        add_prob(item, prob_case0_main_block * prob_combo * prob_of_being_chosen)

  # Case 1: 鱼饵/浮标 (精确if/else if概率流模型)
  p_rem = prob_case_base
  prob_block1_succeeds = 0
  if consts["clearWaterDistance"] >= 4 and consts["fishingLevel"] >= 6:
    prob_block1_succeeds = p_rem * 0.1
  add_prob("(O)687", prob_block1_succeeds)
  p_rem -= prob_block1_succeeds
  prob_block2_succeeds = 0
  if consts["hasWildBaitRecipe"]:
    prob_block2_succeeds = p_rem * 0.25
  add_prob("(O)774", prob_block2_succeeds)
  p_rem -= prob_block2_succeeds
  prob_block3_succeeds = 0
  if consts["fishingLevel"] >= 6:
    prob_block3_succeeds = p_rem * 0.11
  add_prob("(O)SonarBobber", prob_block3_succeeds)
  p_rem -= prob_block3_succeeds
  prob_block4_succeeds = 0
  if consts["fishingLevel"] >= 6:
    prob_block4_succeeds = p_rem
  add_prob("(O)DeluxeBait", prob_block4_succeeds)
  p_rem -= prob_block4_succeeds
  add_prob("(O)685", p_rem)

  # Case 2: 古物/晶球
  p_case2 = prob_case_base
  if consts["lostBooksFound"] < 21 and consts["hasLostBookMail"]:
    add_prob("(O)102", p_case2 * 0.1)
  elif consts["archaeologyFoundCount"] > 0 and consts["fishingLevel"] > 1:
    prob_c2_split = p_case2 * 0.25 / 3.0
    add_prob("(O)585", prob_c2_split)
    add_prob("(O)586", prob_c2_split)
    add_prob("(O)587", prob_c2_split)
    prob_c2_artifacts = p_case2 * 0.5 / 17.0
    for i in range(103, 120):
      add_prob(f"(O){i}", prob_c2_artifacts)
    add_prob("(O)535", p_case2 * 0.25)
  else:
    add_prob("(O)535", p_case2)

  # Case 3: 混合/稀有
  p_subcase = prob_case_base / 3.0
  if consts["clearWaterDistance"] >= 4:
    add_prob("(O)537", p_subcase * 0.6)
    add_prob("(O)536", p_subcase * 0.2)
    add_prob("(O)535", p_subcase * 0.2)
  elif consts["clearWaterDistance"] >= 3:
    add_prob("(O)536", p_subcase * 0.6)
    add_prob("(O)535", p_subcase * 0.4)
  else:
    add_prob("(O)535", p_subcase)

  prob_diamond_guaranteed = 0.028 * (consts["clearWaterDistance"] / 5.0)
  p_gem_base = p_subcase * (1 - prob_diamond_guaranteed)
  if consts["clearWaterDistance"] >= 4:
    add_prob("(O)82", p_gem_base * 0.3)
    add_prob("(O)60", p_gem_base * 0.35)
    add_prob("(O)64", p_gem_base * 0.35)
  elif consts["clearWaterDistance"] >= 3:
    add_prob("(O)84", p_gem_base * 0.3)
    add_prob("(O)70", p_gem_base * 0.35)
    add_prob("(O)62", p_gem_base * 0.35)
  else:
    add_prob("(O)86", p_gem_base * 0.3)
    add_prob("(O)66", p_gem_base * 0.35)
    add_prob("(O)68", p_gem_base * 0.35)
  add_prob("(O)72", p_subcase * prob_diamond_guaranteed)

  p_cond_interrupt = 0.0
  if consts["fishingLevel"] >= 2:
    luck_mod = (1.0 + consts["dailyLuck"]) * (consts["clearWaterDistance"] / 5.0)
    if not consts["hasWeapon14"]:
      add_prob("(W)14", p_subcase * 0.05 * luck_mod)
    if not consts["hasWeapon51"]:
      add_prob("(W)51", p_subcase * 0.05 * luck_mod)
    prob_ring_block = p_subcase * 0.07 * luck_mod
    prob_luck_ring = consts["luckLevel"] / 11.0
    add_prob("(R)517", prob_ring_block * (1 / 3.0) * prob_luck_ring)
    add_prob("(R)516", prob_ring_block * (1 / 3.0) * (1 - prob_luck_ring))
    add_prob("(R)519", prob_ring_block * (1 / 3.0) * prob_luck_ring)
    add_prob("(R)518", prob_ring_block * (1 / 3.0) * (1 - prob_luck_ring))
    for i in range(529, 535):
      add_prob(f"(R){i}", prob_ring_block * (1 / 3.0) / 6.0)
    add_prob("(O)166", p_subcase * 0.02 * luck_mod)
    if consts["fishingLevel"] > 5:
      add_prob("(O)74", p_subcase * 0.001 * luck_mod)
    add_prob("(O)127", p_subcase * 0.01 * luck_mod)
    add_prob("(O)126", p_subcase * 0.01 * luck_mod)
    add_prob("(O)527", p_subcase * 0.01 * luck_mod)
    for i in range(504, 514):
      add_prob(f"(B){i}", p_subcase * 0.01 * luck_mod / 10.0)
    if consts["hasFarmEternalMail"]:
      add_prob("(O)928", p_subcase * 0.01 * luck_mod)
    if consts["fishingTreasuresStat"] > 3:
      p_cond_interrupt = p_subcase * 0.05 * luck_mod
      for i in range(5):
        add_prob(f"(O)SkillBook_{i}", p_cond_interrupt / 5.0)
  else:
    add_prob("(O)770", p_subcase)

  # 将一个物品所有来源的概率组件进行合并，得到其在单次循环中的总条件概率
  p_cond_wins = {}
  for item in item_order:
    prob_not_getting = reduce(operator.mul, (1 - p for p in p_components[item]), 1.0)
    p_cond_wins[item] = 1.0 - prob_not_getting
  return p_cond_wins, p_cond_interrupt, item_order


def calculate_final_probabilities(p_cond_wins, p_cond_interrupt, consts):
  """
  第二阶段：应用迭代模型计算最终的总概率。

  此函数模拟 `while` 循环的多次迭代，精确追踪衰减的 `chance`
  和“进程存活”概率，将单次循环的条件概率累加为最终的总概率。
  """
  P_total_win = defaultdict(float)
  p_active = 1.0  # “进程存活”（未被中断）的绝对概率
  chance = 1.0  # C# 源码中的 chance 变量
  decay_factor = 0.6 if consts["goldenTreasure"] else 0.4

  for _ in range(30):
    # 本轮循环体被执行的绝对概率
    p_exec_abs = p_active * chance
    if p_exec_abs < 1e-15:
      break

    # 基于本轮执行的概率，累加每种物品“首次获得”的概率
    for item, p_cond in p_cond_wins.items():
      P_total_win[item] += (1 - P_total_win[item]) * p_exec_abs * p_cond

    # 只有在本轮被执行且未被中断的情况下，进程才能继续到下一轮
    p_active = p_exec_abs * (1.0 - p_cond_interrupt)

    # 更新 chance，用于下一轮的循环判定
    chance *= decay_factor
  return P_total_win


if __name__ == "__main__":
  print("--- 星露谷钓鱼宝箱概率计算 (最终版) ---")
  print(f"使用玩家状态: {PLAYER_STATS}\n")

  # 阶段1 & 2: 计算所有可能在循环内获得的物品的最终概率
  conditional_wins, conditional_interrupt, item_order = calculate_single_loop_prospects(PLAYER_STATS)
  loop_probabilities = calculate_final_probabilities(conditional_wins, conditional_interrupt, PLAYER_STATS)

  # 阶段3: 计算循环结束后的独立事件，包括“保底”机制
  post_loop_probabilities = defaultdict(float)

  # 计算 "while循环一无所获" 的概率，这会触发保底(O)685
  prob_loop_yields_nothing = reduce(operator.mul, (1 - p for p in loop_probabilities.values()), 1.0)
  post_loop_probabilities["(O)685"] = prob_loop_yields_nothing

  # 计算其他循环后物品的概率
  if PLAYER_STATS["hasBookRoe"]:
    post_loop_probabilities["FlavoredRoe"] = 0.25
  if PLAYER_STATS["fishingLevel"] > 4 and PLAYER_STATS["fishingTreasuresStat"] > 2:
    roe_book_mod = (
      PLAYER_STATS["fishingTreasuresStat"] * 0.001 if not PLAYER_STATS["mailReceived_roeBookDropped"] else 0.001
    )
    post_loop_probabilities["(O)Book_Roe"] = 0.02 + roe_book_mod

  # 将循环外物品添加到顺序列表的末尾，以备输出
  for item in post_loop_probabilities.keys():
    if item not in item_order:
      item_order.append(item)

  # 最终合并：将循环内和循环外的所有概率来源进行整合
  final_probabilities = defaultdict(float)
  for item in item_order:
    p_loop = loop_probabilities.get(item, 0.0)
    p_post = post_loop_probabilities.get(item, 0.0)
    final_probabilities[item] = 1 - ((1 - p_loop) * (1 - p_post))

  # --- 最终输出 ---
  print(f"每次循环的条件中断概率: {conditional_interrupt:.4%}")
  print("每种物品至少获得一个的最终概率 (按代码逻辑顺序):")
  for item in item_order:
    prob = final_probabilities[item]
    if prob > 0:
      print(f"  - {item:<35}: {prob:.4%}")
