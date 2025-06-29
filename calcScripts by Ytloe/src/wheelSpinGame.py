import math

from utils import PerfMonitor, StringUtils


def spin_once(init_vel: float, pick_green: bool, allow_adjust: bool):
  """
  模拟一局转盘

  参数
  init_vel    初始角速度
  pick_green  True 押绿色 / False 押橙色
  allow_adjust True 进行尾速调整
  返回值
  (终止角度, 本局是否尾速调整过, 调整触发角度)
  """
  angle = 0.0
  vel = init_vel
  decel = -math.pi / 5000.0

  adjusted = False
  adjust_pos = None

  while vel > 0:
    prev_vel = vel
    vel += decel

    # 尾速调整判定（角速度第一次到π/80进行尾速调整判断）
    need_adjust = allow_adjust and vel <= math.pi / 80 and prev_vel > math.pi / 80 and not adjusted
    if need_adjust:
      adjust_pos = angle
      if pick_green:  # 押绿：旋转角度刚好在 (π/2, 11π/8] 区间才有1/15概率调整
        if math.pi / 2 < angle <= 11 * math.pi / 8:
          vel = math.pi / 48
          adjusted = True
      else:  # 押橙：旋转角度刚好在 [0, 3π/8] ∪ [π, 2π) 区间才有1/20概率调整
        if ((angle + math.pi) % (2 * math.pi)) <= 11 * math.pi / 8:
          vel = math.pi / 48
          adjusted = True

    # 正常积分
    if vel > 0:
      angle = (angle + vel) % (2 * math.pi)

  return angle, adjusted, adjust_pos


def color_at(angle: float) -> str:
  """
  角度 → 颜色

  (π/2, 3π/2]为橙色区域；
  否则为绿色区域
  """
  return "橙色" if math.pi / 2 < angle <= 3 * math.pi / 2 else "绿色"


def main() -> None:
  monitor = PerfMonitor("转盘概率计算")
  monitor.start()
  # 生成 30 种初速度
  init_vel_list = []
  for idx in range(15):
    for extra in (0, 1):
      v = math.pi / 16 + idx * math.pi / 256 + extra * math.pi / 64
      init_vel_list.append((v, idx, extra))

  # 格式化表头
  head_vel = StringUtils.pad_to_width("初速度", 25)
  head_raw = StringUtils.pad_to_width("指向(角度)", 20)
  head_green = StringUtils.pad_to_width("尾速调整（绿）", 20)
  head_orange = "尾速调整（橙）"
  print(f"{head_vel}| {head_raw}| {head_green}| {head_orange}")
  print("-" * 95)

  # 统计
  green_raw = 0  # 无尾速调整绿赢
  orange_raw = 0  # 无尾速调整橙赢
  green_adjust = 0  # 调整后绿赢
  orange_adjust = 0  # 调整后橙赢
  green_adjust_count = 0  # 选绿尾速调整总数
  orange_adjust_count = 0  # 选橙尾速调整总数

  # 遍历 30 种初速度
  for vel, idx, extra in init_vel_list:
    # 无调整
    angle_raw, _, _ = spin_once(vel, pick_green=True, allow_adjust=False)
    color_raw = color_at(angle_raw)

    # 选绿调整结果
    angle_green, adjusted_green, _ = spin_once(vel, True, True)
    color_green = color_at(angle_green)

    # 选橙调整结果
    angle_orange, adjusted_orange, _ = spin_once(vel, False, True)
    color_orange = color_at(angle_orange)

    # 胜负统计
    if color_raw == "绿色":
      green_raw += 1
    else:
      orange_raw += 1
    if color_green == "绿色":
      green_adjust += 1
    if color_orange == "橙色":
      orange_adjust += 1

    # 调整次数
    if adjusted_green:
      green_adjust_count += 1
    if adjusted_orange:
      orange_adjust_count += 1

    # 初速度列
    init_vel = "π/16"
    if idx:
      init_vel += f" + {idx}π/256"
    if extra:
      init_vel += " + π/64"
    init_vel = StringUtils.pad_to_width(init_vel, 25)
    # 无调整列
    raw_result = StringUtils.pad_to_width(f"{color_raw}({angle_raw * 180 / math.pi:.2f}°)", 20)

    # 选绿调整列
    if adjusted_green:
      green_result = f"{color_green}({angle_green * 180 / math.pi:.2f}°)"
      if color_green == "绿色" and color_raw != "绿色":
        green_result = "*" + green_result
      else:
        green_result = " " + green_result
    else:
      green_result = " - "
    green_result = StringUtils.pad_to_width(green_result, 20)

    # 选橙调整列
    if adjusted_orange:
      orange_result = f"{color_orange}({angle_orange * 180 / math.pi:.2f}°)"
      if color_orange == "橙色" and color_raw != "橙色":
        orange_result = "*" + orange_result
      else:
        orange_result = " " + orange_result
    else:
      orange_result = " - "

    print(f"{init_vel}| {raw_result}| {green_result}| {orange_result}")

  print("-" * 95)

  # 汇总
  print("\n====================== 结果汇总 ======================")
  print(f"选绿获胜：{green_raw}/30，尾速调整：{green_adjust}/30，尾速调整总数：{green_adjust_count}")
  print(f"选橙获胜：{orange_raw}/30，尾速调整：{orange_adjust}/30，尾速调整总数：{orange_adjust_count}")
  print("每 +1 幸运等级增加获胜概率：")
  print(f"选绿：+{(green_adjust - green_raw)}/{15 * 30}")
  print(f"选橙：+{orange_adjust - orange_raw}/{20 * 30}")

  monitor.stop()
  monitor.print_stats()


if __name__ == "__main__":
  main()

  ...
