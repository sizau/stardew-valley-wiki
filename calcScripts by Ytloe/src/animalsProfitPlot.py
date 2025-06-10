"""
星露谷物语动物收益计算器
用于计算不同好感度下动物的日收益，支持常规产物和加工产物的收益对比
"""

import warnings
from pathlib import Path
from typing import List, Optional, Tuple, Union

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray

from utils import PerfMonitor, get_input


def get_animal_base_data(animal_id) -> dict:
  """获取对应动物的基础数据"""
  pig_cycle = 112 / (112 - 28 - 15.732)  # 猪的特殊生产周期：考虑雨天和冬天
  animals_base_data = [
    {"type": "鸡", "base_price": 50, "lrg_price": 95, "proc_price": 190, "cycle": 1, "maturity": 3},
    {"type": "虚空鸡", "base_price": 65, "lrg_price": 0, "proc_price": 275, "cycle": 1, "maturity": 3},
    {"type": "金鸡", "base_price": 500, "lrg_price": 0, "proc_price": 190, "cycle": 1, "maturity": 3},
    {"type": "鸭", "base_price": 95, "lrg_price": 250, "proc_price": 375, "cycle": 2, "maturity": 5},
    {"type": "兔子", "base_price": 340, "lrg_price": 565, "proc_price": 470, "cycle": 4, "maturity": 6},
    {"type": "恐龙", "base_price": 350, "lrg_price": 0, "proc_price": 800, "cycle": 7, "maturity": 0},
    {"type": "牛", "base_price": 125, "lrg_price": 190, "proc_price": 230, "cycle": 1, "maturity": 5},
    {"type": "山羊", "base_price": 225, "lrg_price": 345, "proc_price": 400, "cycle": 2, "maturity": 5},
    {"type": "绵羊", "base_price": 340, "lrg_price": 0, "proc_price": 470, "cycle": 3, "maturity": 4},
    {"type": "猪", "base_price": 625, "lrg_price": 0, "proc_price": 1065, "cycle": pig_cycle, "maturity": 10},
    {"type": "鸵鸟", "base_price": 600, "lrg_price": 0, "proc_price": 190, "cycle": 7, "maturity": 7},
  ]
  return animals_base_data[animal_id]


def get_available_skills(animal_type: str) -> list[str]:
  """根据动物类型获取可用技能列表"""
  coop_animals = ["鸡", "虚空鸡", "金鸡", "鸭", "兔子", "恐龙"]
  barn_animals = ["牛", "山羊", "绵羊", "猪", "鸵鸟"]

  base_skills = ["无技能", "畜牧人", "", "工匠"]

  if animal_type in coop_animals:
    base_skills[2] = "鸡舍大师"
    if animal_type == "恐龙":
      base_skills.append("古物书")
  elif animal_type in barn_animals and animal_type != "猪":
    base_skills[2] = "牧羊人"
  else:  # 猪
    base_skills[1] = "采集者"
    base_skills[2] = "植物学家"

  return base_skills


def calc_quality_prices(
  base_price: int, skills: list[str], animal_type: str, is_proc: bool, profit_rate: float
) -> NDArray[np.int32]:
  """计算各品质的价格"""
  multiplier = 1.0

  if "无技能" in skills:
    multiplier = 1.0
  elif is_proc:
    if "工匠" in skills:
      multiplier = 1.4
    elif any(skill in skills for skill in ["畜牧人", "鸡舍大师", "牧羊人"]):
      multiplier = 1.2
  else:  # 非加工产物
    if any(skill in skills for skill in ["畜牧人", "鸡舍大师", "牧羊人"]) and animal_type != "恐龙":
      multiplier = 1.2
    elif "古物书" in skills:  # 恐龙专用
      multiplier = 3.0

  # 品质倍率：无星1.0, 银星1.25, 金星1.5, 铱星2.0
  quality_mults = np.array([1.0, 1.25, 1.5, 2.0])
  prices = np.floor(np.floor(np.floor(base_price * quality_mults) * multiplier) * profit_rate).astype(np.int32)

  return prices


def calc_product_profit(
  prod_prob: NDArray[np.float64],
  quality_probs: NDArray[np.float64],
  quality_prices: NDArray[np.int32],
  cycle_prod: NDArray[np.float64],
  pickup_mult: Union[float, NDArray[np.float64]],
) -> NDArray[np.float64]:
  """计算产物收益的通用公式"""
  if quality_probs.ndim == 2:
    quality_revenue = np.sum(quality_probs * quality_prices, axis=1)
  else:
    quality_revenue = np.sum(quality_probs * quality_prices)

  return prod_prob * quality_revenue * cycle_prod * pickup_mult


def setup_animal_config(
  animal_id: Optional[int] = None,
  skill_ids: Optional[list[int]] = None,
  profit_rate: Optional[float] = None,
  use_golden_cookie: Optional[bool] = None,
) -> dict:
  """设置动物配置信息"""

  # 获取动物编号
  if animal_id is None:
    coop_animals = ["鸡", "虚空鸡", "金鸡", "鸭", "兔子", "恐龙"]
    barn_animals = ["牛", "山羊", "绵羊", "猪", "鸵鸟"]

    coop_prompt = "、".join(f"{i}-{name}" for i, name in enumerate(coop_animals))
    barn_prompt = "、".join(f"{i + 6}-{name}" for i, name in enumerate(barn_animals))
    full_prompt = f"可输入的动物编号：\n{coop_prompt}\n{barn_prompt}\n请输入要查看的动物编号"

    animal_id = get_input(prompt=full_prompt, def_val=0, val_type=int, range=(0, 10))

  # 确保animal_id不为None
  assert animal_id is not None, "animal_id should not be None"
  animal_data = get_animal_base_data(animal_id)
  animal_type = animal_data["type"]

  # 获取技能配置
  if skill_ids is None:
    available_skills = get_available_skills(animal_type)
    skill_prompt = "、".join(f"{idx}-{skill}" for idx, skill in enumerate(available_skills))
    skill_input = get_input(
      prompt=f"可输入的技能编号：\n{skill_prompt}\n请输入技能编号",
      def_val=0,
      val_type=int,
      range=(0, len(available_skills) - 1),
    )
    skill_ids = [skill_input] if isinstance(skill_input, int) else skill_input

  # 确保skill_ids不为None
  assert skill_ids is not None, "skill_ids should not be None"
  available_skills = get_available_skills(animal_type)
  selected_skills = [available_skills[i] for i in sorted(set(skill_ids)) if 0 <= i < len(available_skills)]

  if animal_type == "绵羊" and "牧羊人" in selected_skills:
    animal_data["cycle"] -= 1
  # 获取觅食等级（仅猪需要）
  foraging_level = -1
  if animal_type == "猪" and "植物学家" not in selected_skills:
    min_level = 5 if "采集者" in selected_skills else 0
    foraging_level = get_input(prompt="请输入觅食等级", def_val=10, val_type=int, range=(min_level, 14))

  # 获取利润率
  if profit_rate is None:
    profit_rate = get_input(prompt="请输入利润率", def_val=1.0, val_type=float, range=(0.25, 1.0))

  # 获取金饼干使用情况
  if use_golden_cookie is None:
    use_golden_cookie = get_input(
      prompt="0-否、1-是\n请输入是否使用金饼干", def_val=0, val_type=bool, range=[0, 1]
    )

  # 确保profit_rate不为None
  assert profit_rate is not None, "profit_rate should not be None"

  # 计算各种价格
  raw_prices = calc_quality_prices(animal_data["base_price"], selected_skills, animal_type, False, profit_rate)
  lrg_prices = (
    calc_quality_prices(animal_data["lrg_price"], selected_skills, animal_type, False, profit_rate)
    if animal_data["lrg_price"] > 0
    else np.zeros(4, dtype=np.int32)
  )
  proc_prices = calc_quality_prices(animal_data["proc_price"], selected_skills, animal_type, True, profit_rate)

  return {
    "type": animal_type,
    "raw_prices": raw_prices,
    "lrg_prices": lrg_prices,
    "proc_prices": proc_prices,
    "cycle": animal_data["cycle"],
    "maturity": animal_data["maturity"],
    "skills": selected_skills,
    "foraging_level": foraging_level,
    "use_golden_cookie": use_golden_cookie,
    "profit_rate": profit_rate,
  }


def calc_daily_profits(
  animal_config: dict,
) -> Tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
  """计算0-1000好感度的日收益"""
  animal_type = animal_config["type"]
  skills = animal_config["skills"]

  # 创建好感度数组 (0-1000)
  friendship_levels = np.arange(0, 1001, dtype=np.int32)

  # 获取特殊参数
  daily_luck = 0.0
  daily_frames = 0

  if animal_type == "兔子":
    daily_luck = get_input(prompt="请输入平均每日运气", def_val=0.0, val_type=float, range=(-0.1, 0.125))
  elif animal_type == "鸭":
    daily_luck = get_input(prompt="请输入平均每日运气", def_val=0.0, val_type=float, range=(-0.1, 0.125))
  elif animal_type == "猪":
    daily_frames = get_input(
      prompt="请输入猪每天工作的平均帧数(每小时2628帧)", def_val=26280, val_type=int, range=(0, 52560)
    )

  # 计算品质概率数组 (1001, 4)
  if animal_type == "猪":
    # 猪的固定品质概率
    if "无技能" not in skills and "植物学家" in skills:
      quality_probs = np.tile([0.0, 0.0, 0.0, 1.0], (1001, 1))
    else:
      Au_prob = np.clip(animal_config["foraging_level"] / 30, 0, 1)
      Ag_prob = np.clip((1 - Au_prob) * (animal_config["foraging_level"] / 15), 0, 1 - Au_prob)
      No_prob = max(1 - Au_prob - Ag_prob, 0)
      quality_probs = np.tile([No_prob, Ag_prob, Au_prob, 0.0], (1001, 1))
  else:
    # 其他动物的动态品质概率
    skill_bonus = 0.33 if any(skill in skills for skill in ["鸡舍大师", "牧羊人"]) else 0.0
    mood = 255

    quality = (friendship_levels / 1000) - (1 - (mood / 225)) + skill_bonus
    Ir_probs = np.where(quality <= 0.95, 0, np.clip(quality / 2, 0, 1))
    Au_probs = np.clip((1 - Ir_probs) * (quality / 2), 0, (1 - Ir_probs))
    Ag_probs = np.clip((1 - Ir_probs - Au_probs) * quality, 0, (1 - Ir_probs - Au_probs))
    No_probs = np.maximum(1 - Ir_probs - Au_probs - Ag_probs, 0)

    quality_probs = np.column_stack([No_probs, Ag_probs, Au_probs, Ir_probs])

  # 计算大产物概率数组 (1001,)
  has_lrg_prod = animal_config["lrg_prices"][0] > 0
  if has_lrg_prod:
    mood = 255
    mood_modifier = 1.5 if mood > 200 else min(0, mood - 100)

    if animal_type == "兔子":
      friendship_modifier = 5000
      luck_modifier = 1.02
      threshold = 0
    elif animal_type == "鸭":
      friendship_modifier = 4750
      luck_modifier = 1.01
      threshold = 200
    else:
      friendship_modifier = 1200
      luck_modifier = 0.0
      threshold = 200

    lrg_probs = np.where(
      friendship_levels >= threshold,
      np.minimum(1, (friendship_levels + mood * mood_modifier) / friendship_modifier + daily_luck * luck_modifier),
      0,
    )
  else:
    lrg_probs = np.zeros(1001)

  # 计算每周期产出数组 (1001,)
  if animal_type == "猪":
    keep_work_probs = np.clip(friendship_levels / 1500, 0, 0.9999)
    decay_factors = 1.0 - (1.0 - keep_work_probs) * 0.0002
    cycle_prods = (1.0 / (1.0 - keep_work_probs)) * (1.0 - decay_factors**daily_frames)
  else:
    cycle_prods = np.ones(1001)

  # 计算拾取倍数
  if animal_type == "猪":
    pickup_mult = 1.2 if "采集者" in skills else 1.0
  else:
    pickup_mult = 2.0 if animal_config["use_golden_cookie"] else 1.0

  # 计算常规产物和大产物的收益
  row_probs = 1 - lrg_probs

  row_profits = calc_product_profit(
    row_probs, quality_probs, animal_config["raw_prices"], cycle_prods, pickup_mult
  )

  lrg_profits = calc_product_profit(
    lrg_probs, quality_probs, animal_config["lrg_prices"], cycle_prods, pickup_mult
  )

  # 猪的特殊处理：松露蟹收益
  if animal_type == "猪":
    row_profits *= 0.998
    crab_profit = (
      ((0.999 + 0.5 + 0.1) * animal_config["raw_prices"][0] + 0.1 * animal_config["proc_prices"][0])
      * cycle_prods
      * 0.002
    )
    row_profits += crab_profit

  # 处理绵羊牧羊人和>=900好感度时周期各-1的逻辑
  cycle_days = animal_config["cycle"]
  if animal_type == "绵羊":
    # 创建动态周期数组：好感度>=900时周期-1
    cycle_array = np.where(friendship_levels >= 900, cycle_days - 1, cycle_days)
  else:
    cycle_array = np.full(1001, cycle_days)

  # 计算常规日收益
  raw_daily_profits = ((row_profits + lrg_profits) / cycle_array - 50) * 1

  # 计算加工收益
  if animal_type == "猪":
    material_counts = cycle_prods * (pickup_mult * 0.998 + (0.999 + 0.5 + 0.1 + 0.1) * 0.002)
  else:
    material_counts = cycle_prods * pickup_mult

  # 设置加工后的品质概率和产出倍数
  if animal_type == "金鸡":
    output_quality_probs = np.tile([0.0, 0.0, 1.0, 0.0], (1001, 1))
    output_mult = 3.0
  elif animal_type == "鸵鸟":
    output_quality_probs = quality_probs
    output_mult = 10.0
  elif animal_type in ["兔子", "绵羊"]:
    quality_mults = np.array([1.0, 1.1, 1.5, 2.0])
    output_mult = np.sum(quality_probs * quality_mults, axis=1)
    output_quality_probs = np.tile([1.0, 0.0, 0.0, 0.0], (1001, 1))
  else:
    output_quality_probs = np.tile([1.0, 0.0, 0.0, 0.0], (1001, 1))
    output_mult = 1.0

  # 计算加工后的收益
  proc_row_profits = calc_product_profit(
    row_probs,
    output_quality_probs,
    animal_config["proc_prices"],
    material_counts,
    output_mult,
  )
  output_quality_probs = np.tile([0.0, 0.0, 1.0, 0.0], (1001, 1))
  proc_lrg_profits = calc_product_profit(
    lrg_probs,
    output_quality_probs,
    animal_config["proc_prices"],
    material_counts,
    output_mult,
  )

  # 鸭和兔子的大产物不能加工
  if animal_type in ["鸭", "兔子"]:
    proc_lrg_profits = lrg_profits

  # 计算加工日收益
  proc_daily_profits = ((proc_row_profits + proc_lrg_profits) / cycle_array - 50) * 1

  # 如果有更细致的计算需求，除了以下4个数值还可以自己输出
  # 常规产物日收益：row_profits
  # 大产物日收益：lrg_profits
  # 常规产物日收益（加工）：proc_row_profits
  # 大产物日收益（加工）：proc_lrg_profits
  return raw_daily_profits, proc_daily_profits, lrg_probs, quality_probs


def plot_profit_comparison(
  data_list: List[NDArray[np.float64]],
  labels: List[str],
  save_path: Optional[str] = "profit_comparison.png",
  animal_id: int = 0,
  title_suffix: str = "好感度与日收益对比图",
) -> None:
  """
  绘制多组数据的收益对比图，支持添加注释点

  Args:
      data_list: 包含多组数据的列表，每组数据是一个NDArray[np.float64]
      labels: 每条折线的标签列表，长度应与data_list相同
      save_path: 保存路径
      animal_id: 动物ID
      title_suffix: 图表标题后缀
  """
  # 参数验证
  if len(data_list) != len(labels):
    raise ValueError("数据组数与标签数量不匹配")

  if len(data_list) == 0:
    raise ValueError("至少需要一组数据")

  plt.rcParams["font.sans-serif"] = ["SimHei"]
  plt.rcParams["axes.unicode_minus"] = False

  x = np.arange(1001)

  # 获取y轴范围
  all_values = np.concatenate(data_list)
  y_min = np.min(all_values)
  y_max = np.max(all_values)
  y_min_floor = (int(y_min) // 100) * 100
  y_max_ceil = ((int(y_max) + 99) // 100) * 100

  # 设置画布 - 固定DPI以确保一致性
  fig, ax = plt.subplots(figsize=(12, 6), dpi=100)

  # 设置背景图片
  bg_path = Path("img/bg.jpg")
  if bg_path.exists():
    # 抑制EXIF警告

    with warnings.catch_warnings():
      warnings.filterwarnings("ignore", message="Corrupt EXIF data")
      warnings.filterwarnings("ignore", category=UserWarning)
      # 读取背景图
      img = plt.imread(bg_path)

    # 获取figure的实际尺寸
    fig_width_inch, fig_height_inch = fig.get_size_inches()
    dpi = fig.dpi
    fig_width_px = int(fig_width_inch * dpi)
    fig_height_px = int(fig_height_inch * dpi)

    # 获取背景图的原始尺寸
    img_height, img_width = img.shape[:2]

    # 计算缩放比例（保持长宽比）
    scale = min(fig_width_px / img_width, fig_height_px / img_height)

    # 如果图片需要缩放
    if scale != 1:
      # 计算新的尺寸
      new_height = int(img_height * scale)
      new_width = int(img_width * scale)

      if scale < 1:
        step_h = max(1, img_height // new_height)
        step_w = max(1, img_width // new_width)
        img = img[::step_h, ::step_w]

    # 计算居中位置
    xo = (fig_width_px - img.shape[1]) // 2
    yo = (fig_height_px - img.shape[0]) // 2

    # 添加背景图
    fig.figimage(img, xo=xo, yo=yo, alpha=0.3, zorder=-1)
    ax.set_facecolor("none")
  else:
    ax.set_facecolor("white")

  # 定义颜色列表，用于多条折线
  colors = [
    "blue",
    "green",
    "red",
    "orange",
    "purple",
    "brown",
    "pink",
    "gray",
    "olive",
    "cyan",
    "magenta",
    "yellow",
    "black",
    "lime",
    "navy",
    "teal",
    "maroon",
    "aqua",
  ]

  # 如果折线数量超过预定义颜色，使用matplotlib的颜色映射
  if len(data_list) > len(colors):
    # 使用tab20颜色映射或者生成HSV颜色
    if len(data_list) <= 20:
      cmap = plt.cm.get_cmap("tab20")
      colors = [cmap(i / len(data_list)) for i in range(len(data_list))]
    else:
      # 使用HSV色彩空间生成均匀分布的颜色

      colors = []
      for i in range(len(data_list)):
        hue = i / len(data_list)
        rgb = mcolors.hsv_to_rgb([hue, 0.8, 0.9])
        colors.append(rgb)

  # 绘制多条折线
  for i, (data, label) in enumerate(zip(data_list, labels)):
    color = colors[i % len(colors)]
    ax.plot(x, data, label=label, color=color, linewidth=2, zorder=5)

  # 默认的重要转折点
  vertical_lines: list[tuple[int, str]] = []
  animal_type = get_animal_base_data(animal_id)["type"]
  if animal_type != "猪":
    vertical_lines.extend(
      [
        (487, "487：开始有铱星产物"),
        (536, "536：开始没无星产物"),
        (818, "818：开始有铱星产物"),
        (867, "867：开始没无星产物"),
      ]
    )
  if animal_type in ["鸡", "鸭", "牛", "山羊"]:
    vertical_lines.append((200, "200：开始有大产物"))
  if animal_type in ["鸡", "牛", "山羊"]:
    vertical_lines[2] = (818, "818：必定大产物且开始有铱星产物")
  if animal_type == "绵羊":
    vertical_lines.append((900, "900：绵羊生产周期-1"))

  # 绘制垂直虚线和标签
  line_colors = ["red", "purple", "brown", "pink", "gray", "cyan", "magenta"]
  for i, (x_pos, line_label) in enumerate(vertical_lines):
    if 0 <= x_pos <= 1000:
      color = line_colors[i % len(line_colors)]

      # 绘制垂直虚线
      ax.axvline(x=x_pos, color=color, linestyle="--", linewidth=1.5, alpha=0.8, zorder=3)

      # 在顶部添加标签
      ax.text(
        x_pos,
        y_max_ceil - (y_max_ceil - y_min_floor) * 0.05,
        line_label,
        rotation=90,
        verticalalignment="top",
        horizontalalignment="right",
        color=color,
        fontsize=9,
        weight="bold",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor=color, alpha=0.8),
      )

  # 设置坐标轴
  ax.set_xlabel("好感度")
  ax.set_ylabel("日收益")
  ax.set_xticks(np.arange(0, 1001, 200))

  # 设置x轴范围，添加5%的边距使图表更美观
  x_margin = 50  # 好感度轴的边距
  ax.set_xlim(-x_margin, 1000 + x_margin)

  y_tick_step = max((y_max_ceil - y_min_floor) // 5, 100)
  y_ticks = np.arange(y_min_floor, y_max_ceil + 1, y_tick_step)
  ax.set_yticks(y_ticks)

  # 设置y轴范围，添加适当边距
  y_margin = (y_max_ceil - y_min_floor) * 0.05
  ax.set_ylim(y_min_floor - y_margin, y_max_ceil + y_margin)

  ax.set_title(f"{animal_type}{title_suffix}")

  # 动态调整图例位置和列数
  n_lines = len(data_list)
  if n_lines <= 4:
    ax.legend(loc="upper left")
  elif n_lines <= 8:
    ax.legend(loc="upper left", ncol=2)
  else:
    # 对于更多折线，使用更多列或放在图外
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", ncol=max(1, n_lines // 10))

  ax.grid(True, linestyle="--", alpha=0.5, zorder=1)

  # 先调用tight_layout
  plt.tight_layout()

  # 确保img文件夹存在并保存
  if save_path:
    img_dir = Path("img")
    img_dir.mkdir(exist_ok=True)  # 创建文件夹，如果已存在则忽略

    # 将保存路径修改为img文件夹中
    save_file = img_dir / save_path if not save_path.startswith("img") else Path(save_path)

    # 使用bbox_inches保存图片
    plt.savefig(save_file, bbox_inches="tight", pad_inches=0.1, facecolor="white")
    print(f"图表已保存到 ./img/{save_path}")

  # 展示图像
  # plt.show()


def main() -> None:
  """主函数"""
  # 调用性能监控
  monitor = PerfMonitor("动物收益计算")
  monitor.start()
  # 测试准确性能时记得把plot_profit_comparison()的plt.show()注释掉，并采用animal_id = 0
  print("=== 星露谷物语动物收益计算器 ===")
  # 0-鸡、1-虚空鸡、2-金鸡、3-恐龙、4-鸭、5-兔子、6-牛、7-山羊、8-绵羊、9-猪、10-鸵鸟
  # for animal_id in range(11):
  animal_id: int = 0
  # setup_animal_config()
  print("\n配置动物信息（有技能）...")
  config_with_skills = setup_animal_config(
    animal_id=animal_id,
    skill_ids=[1, 2, 3, 4],
    profit_rate=1.0,
    use_golden_cookie=True,
  )

  print(f"配置完成：{config_with_skills['type']}")
  print(f"技能：{config_with_skills['skills']}")

  # 计算有技能的收益
  print("\n计算有技能配置的收益...")
  raw_skilled, proc_skilled, lrg_probs_skilled, quality_probs_skilled = calc_daily_profits(config_with_skills)

  # 配置无技能
  print("\n配置动物信息（无技能）...")
  config_no_skills = setup_animal_config(
    animal_id=animal_id,
    skill_ids=[0],  # 无技能
    profit_rate=1.0,
    use_golden_cookie=False,
  )

  print(f"配置完成：{config_no_skills['type']}")
  print(f"技能：{config_no_skills['skills']}")

  # 计算无技能的收益
  print("\n计算无技能配置的收益...")
  raw_no_skills, proc_no_skills, lrg_probs_no_skills, quality_probs_no_skills = calc_daily_profits(
    config_no_skills
  )
  # 有查看概率的需求可以自行for print输出lrg_probs和quality_probs，都是1001个元素

  # 输出关键节点的收益数据
  print("\n=== 好感度收益对比 ===")
  # key_points = [0, 200, 400, 600, 800, 1000]
  for friendship in range(0, 1001, 100):
    print(f"好感度 {friendship}:")
    print(
      f"  全技能 - 常规: {raw_skilled[friendship]:.4f}, \
      加工: {proc_skilled[friendship]:.4f}，\
      品质概率：{quality_probs_skilled[friendship]}，\
      大产物概率：{lrg_probs_skilled[friendship]}"
    )
    print(
      f"  无技能 - 常规: {raw_no_skills[friendship]:.4f}, \
      加工: {proc_no_skills[friendship]:.4f}，\
      品质概率：{quality_probs_no_skills[friendship]}，\
      大产物概率：{lrg_probs_no_skills[friendship]}"
    )

  # 绘制对比图
  print(config_with_skills)
  print("\n绘制收益对比图...")
  plot_profit_comparison(
    data_list=[raw_skilled, proc_skilled, raw_no_skills, proc_no_skills],
    labels=["全技能常规日收益", "全技能加工日收益", "无技能常规日收益", "无技能加工日收益"],
    save_path=f"{config_with_skills['type']}_profit_comparison.png",
    animal_id=animal_id,
  )
  monitor.stop()
  monitor.print_stats()


if __name__ == "__main__":
  main()
