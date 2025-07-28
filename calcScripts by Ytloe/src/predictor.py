import math
from pathlib import Path

from cs_random import CSRandom
from utils import FileUtils

# --- 全局常量 ---
# 由于是固定版本和单人模式，这些可以被硬编码
NUM_COLUMNS = 6  # Geode, Frozen, Magma, Omni, Trove, Coconut for v1.6+


def _get_random_seed(num_cracked: int, game_id_half: float) -> int:
  """为单人游戏计算随机种子"""
  return int(num_cracked + game_id_half)


def predict_geode_treasures(game_id: int, geodes_cracked: int, prediction_count: int = 20) -> list[list[str]]:
  """
  预测星露谷物语中的晶洞产物 (针对v1.6.15单人优化版)。

  Args:
      game_id (int): 你的游戏存档ID。
      geodes_cracked (int): 你已经打开的晶洞总数。
      prediction_count (int, optional): 要预测的晶洞数量。默认为 20。

  Returns:
      list[list[str]]: 一个二维列表，包含预测的物品ID。
                       每行代表一次开启，列顺序为：
                       [普通晶洞, 冰封晶洞, 岩浆晶洞, 万象晶洞, 古物宝藏, 金色椰子]
  """
  json_path = Path(__file__).parent.parent / "json"
  geode_contents = FileUtils.read_json(json_path / "geode_contents.json")

  predictions = []
  game_id_half = game_id / 2.0

  for g in range(1, prediction_count + 1):
    num_cracked = geodes_cracked + g
    item = [""] * NUM_COLUMNS

    # 为每个晶洞重新生成RNG实例，以匹配游戏逻辑
    # 在1.6+版本中，普通晶洞和古物宝藏使用相同的种子但独立的RNG实例
    seed = _get_random_seed(num_cracked, game_id_half)
    rng = CSRandom(seed)
    rng_trove = CSRandom(seed)

    # --- RNG预热 (v1.4+ 逻辑) ---
    prewarm_amount = rng.next(1, 10)
    rng_trove.next()
    for _ in range(prewarm_amount):
      rng.next_double()
      rng_trove.next_double()

    prewarm_amount = rng.next(1, 10)
    rng_trove.next()
    for _ in range(prewarm_amount):
      rng.next_double()
      rng_trove.next_double()

    # --- 齐豆检查 (v1.5+ 逻辑) ---
    # 即使我们不显示，也必须调用以保持RNG状态同步
    rng.next_double()  # couldBeBeans
    rng_trove.next_double()  # couldBeBeansTrove

    # --- 古物宝藏 (275) 和 金色椰子 (791) (v1.4+ & v1.5+ 逻辑) ---
    c = rng_trove.next_double()
    item[4] = geode_contents["275"][math.floor(c * len(geode_contents["275"]))]

    roll = math.floor(rng_trove.next_double() * len(geode_contents["791"]))
    item[5] = geode_contents["791"][roll]

    # --- 四种主要晶洞的预测 ---
    roll = rng.next_double()
    get_good_stuff = roll < 0.5  # v1.6+ 逻辑

    if get_good_stuff:
      next_val = rng.next_double()
      item[0] = geode_contents["535"][math.floor(next_val * len(geode_contents["535"]))]
      item[1] = geode_contents["536"][math.floor(next_val * len(geode_contents["536"]))]
      item[2] = geode_contents["537"][math.floor(next_val * len(geode_contents["537"]))]

      # v1.6+ 的五彩碎片逻辑
      if next_val < 0.008 and num_cracked > 15:
        item[3] = "74"  # Prismatic Shard ID
      else:
        item[3] = geode_contents["749"][rng.next(len(geode_contents["749"]))]
    else:
      qty = rng.next(3) * 2 + 1
      if rng.next_double() < 0.1:
        qty = 10
      if rng.next_double() < 0.01:
        qty = 20

      if rng.next_double() < 0.5:
        c = rng.next(4)
        if c < 2:
          stone = "390"  # Stone
          item[0], item[1], item[2], item[3] = stone, stone, stone, stone
        elif c == 2:
          clay = "330"  # Clay
          item[0], item[1], item[2], item[3] = clay, clay, clay, clay
        else:
          item[0] = "86"  # Earth Crystal
          item[1] = "84"  # Frozen Tear
          item[2] = "82"  # Fire Quartz
          item[3] = str(82 + rng.next(3) * 2)  # Fire Quartz, Frozen Tear, or Earth Crystal
      else:
        next_val = rng.next_double()
        # 普通晶洞 (535) - deepestMineLevel > 25 为 True
        c = math.floor(next_val * 3)
        item[0] = "378" if c == 0 else "382" if c == 2 else "380"
        # 冰封晶洞 (536) - deepestMineLevel > 75 为 True
        c = math.floor(next_val * 4)
        item[1] = "378" if c == 0 else "380" if c == 1 else "382" if c == 2 else "384"
        # 岩浆 (537) & 万象 (749) 晶洞
        c = math.floor(next_val * 5)
        ore_id = "378" if c == 0 else "380" if c == 1 else "382" if c == 2 else "384" if c == 3 else "386"
        item[2] = ore_id
        item[3] = ore_id

    predictions.append(item)

  return predictions


if __name__ == "__main__":
  # --- 请在此处输入你的参数 ---
  YOUR_GAME_ID = 123456789
  YOUR_GEODES_CRACKED = 500

  print(f"为 Game ID: {YOUR_GAME_ID} 预测从第 {YOUR_GEODES_CRACKED + 1} 个晶洞开始的产物：\n")

  # 调用主函数获取预测列表
  predicted_items = predict_geode_treasures(
    game_id=YOUR_GAME_ID,
    geodes_cracked=YOUR_GEODES_CRACKED,
    prediction_count=25,  # 你可以按需修改预测数量
  )

  # 格式化输出
  if predicted_items:
    header = ["#", "普通晶洞", "冰封晶洞", "岩浆晶洞", "万象晶洞", "古物宝藏", "金色椰子"]
    print(
      f"{header[0]:>4} {header[1]:<10} {header[2]:<10} {header[3]:<10} {header[4]:<10} {header[5]:<10} {header[6]:<10}"
    )
    print("-" * 75)
    for i, row in enumerate(predicted_items):
      num = YOUR_GEODES_CRACKED + i + 1
      print(f"{num:>4} {row[0]:<10} {row[1]:<10} {row[2]:<10} {row[3]:<10} {row[4]:<10} {row[5]:<10}")
