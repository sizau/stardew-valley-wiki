from typing import Any, Optional, Union
from inspect import stack


def get_input(
  prompt: str = "请输入(允许用空格批量输入)",
  def_val: Any = None,
  val_type: Optional[type] = None,
  range: Optional[Union[tuple, list]] = None,
) -> Any:
  """增强型输入校验函数

  - 参数校验阶段：收集所有参数错误，统一报告后退出
  - 用户输入阶段：循环获取用户输入直到满足所有约束条件

  Args:
      prompt (str): 输入提示词，默认 "请输入(允许用空格批量输入)"
      def_val (Any): 默认值，当用户直接按回车时使用，默认 None
      val_type (Optional[type]): 期望的值类型，如 int、str、bool 等，默认 None
      range (Optional[Union[tuple, list]]): 值的限制范围
          - list: 候选值列表，如 ["red", "green", "blue"]
          - tuple: 数值范围，如 (0, 100) 表示 0 到 100 之间
          默认 None

  Returns:
      Any: 验证通过的单个值或多个值的元组
      - 单个输入返回该值本身
      - 多个输入返回元组

  Examples:
      >>> # 基本字符串输入
      >>> get_input("请输入姓名", "张三", str)

      >>> # 数值范围限制
      >>> get_input("请输入年龄(0-120)", 18, int, (0, 120))

      >>> # 候选列表选择
      >>> get_input("选择颜色", "red", str, ["red", "green", "blue"])

      >>> # 布尔值输入(支持多种表示)
      >>> get_input("是否同意条款", True, bool)

      >>> # 批量数值输入
      >>> get_input("输入多个分数", None, int, (0, 100))
      # 用户输入: 85 92 78
      # 返回: (85, 92, 78)

  Raises:
      SystemExit: 当参数验证失败时退出程序并显示详细错误信息和调用位置
  """
  # 校验流程: 判断存不存在->判断是否合法->统计所有不规范的传参->一次性输出所有需要修改的地方->中断程序
  # 参数预校验模块
  error = []
  hint = []
  min_val = max_val = None
  range_set = None  # 添加初始化

  # 类型校验
  if val_type is not None:  # 存在类型校验
    if not isinstance(val_type, type):  # 检查传入值是否为类型
      error.append(f"val_type参数类型错误，应传入type对象，实际收到 {type(val_type).__name__}")
    else:  # 已确认传入的val_type是类型对象
      # 校验传入的def_val默认值是否符合传入类型
      if def_val is not None and not isinstance(def_val, val_type):
        error.append(f"默认值类型不匹配：{def_val}({type(def_val).__name__}) ≠ {val_type}，类型非法")
      if val_type is bool:
        if range is not None:
          print("提示：val_type参数为bool时，range将自动设置为[True, False, 'T', 'F', '1', '0', 'Y', 'N']")
        range = [True, False, "T", "F", "1", "0", "Y", "N"]
        prompt += "(允许大小写混用)"
      elif range is not None:
        # 校验传入的range候选列表中每个值是否符合传入类型
        if isinstance(range, list):
          for idx, val in enumerate(iterable=range, start=1):
            if not isinstance(val, val_type):
              error.append(f"候选列表#{idx} {val}({type(val).__name__}) 不是 {val_type.__name__}，类型非法")
        # 校验传入的range范围元组中上下限是否符合传入类型
        elif isinstance(range, tuple):
          for idx, val in enumerate(iterable=range, start=1):
            if not isinstance(val, val_type):
              error.append(f"范围元组#{idx} {val}({type(val).__name__}) 不是 {val_type.__name__}，类型非法")
        else:
          error.append("range参数应为候选列表[]或范围元组()")

  # 范围校验模块
  if range is not None:  # 存在范围校验
    try:  # 尝试自动去重
      range_set = set(range)
      # 去重成功，校验其中不同元素个数
      if isinstance(range, list):
        if len(range_set) < 2:
          error.append(f"候选列表需包含至少2个不同值，当前 {len(range_set)} 个")
        if def_val is not None and def_val not in range_set:
          error.append(f"默认值 {def_val} 不在候选列表 {range_set} 中")
      elif isinstance(range, tuple):
        if len(range_set) != 2:
          error.append(f"范围约束应为不同元素的二元组 (min, max)，当前为{range_set}")
        else:  # 已确认包含上下限
          try:  # 尝试排序成(min, max)
            min_val, max_val = sorted(range_set)
          except TypeError:
            error.append("范围值需为可比较类型（如数字）")
          else:  # 已确认是合法的范围元组
            # 校验传入的def_val默认值是否在范围元组中
            if def_val is not None and not (min_val <= def_val <= max_val):
              error.append(f"默认值 {def_val} 超出范围 [{min_val}, {max_val}]")
      else:  # 存在范围校验但类型不合法
        error.append("range参数应为候选列表[]或范围元组()")
    except TypeError:
      error.append("传入的range中包含不可哈希的元素，无法确定包含多少个不同元素")
    finally:
      if len(range) < 2:
        error.append(f"range至少传入2个元素，当前 {len(range)} 个")

  # 提示语校验模块
  if not isinstance(prompt, str) or not prompt.strip():
    error.append("提示语必须为非空字符串")

  # 参数校验失败处理
  if error:
    print("\n".join(f"参数错误 {i}: {e}" for i, e in enumerate(iterable=error, start=1)))
    print(f"调用位置：{stack()[1].filename}:{stack()[1].lineno}")
    exit(1)
  # 只有无error时才允许用户输入，此时所有参数都必定合法或为None

  # 输入处理循环
  # 输入值校验逻辑: 请求输入->无输入判断有无默认值->有默认值直接返回默认值-->无默认值则请求重新输入
  # ->按空格拆分输入值->依次判断是否合法->不合法统一记录->存在不合法就统一列出->要求重新输入
  while True:
    # 构建提示信息
    hint.clear()  # 清空之前的提示信息，避免重复累积
    if def_val is not None:
      hint.append(f"默认：{def_val}")
    if val_type is not None:
      hint.append(f"类型：{val_type.__name__}")
    if range is not None:
      if isinstance(range, tuple):
        # 使用 assert 确保 min_val 和 max_val 不为 None
        assert min_val is not None and max_val is not None, "范围元组的最小值和最大值应该已经被设置"
        hint.append(f"范围：{min_val}~{max_val}")
      else:
        # 使用 assert 确保 range_set 不为 None
        assert range_set is not None, "候选列表的集合应该已经被设置"
        hint.append(f"候选值：{range_set}")
    full_hint = " | ".join(hint) + " | 可用空格分隔批量输入" + "\n" + prompt + ": "

    try:  # 中断输入报错
      user_input: str = input(full_hint).strip()
    except (KeyboardInterrupt, EOFError):
      print("\n操作终止")
      exit(1)

    # 空输入处理
    if not user_input:
      if def_val is not None:
        print(f"使用默认值：{def_val}")
        return def_val
      print("错误：无输入且无默认值")
      continue

    # 值处理流程
    values: list[str] = user_input.split()
    results: list = []
    errors: list = []

    for idx, val in enumerate(iterable=values, start=1):
      # 类型转换
      checked_val = None
      try:
        if val_type is bool:
          lower = val.lower()
          if lower in {"true", "yes", "1", "y", "t"}:
            checked_val = True
          elif lower in {"false", "no", "0", "n", "f"}:
            checked_val = False
          else:
            # 使用 assert 确保 range 不为 None（因为 bool 类型时 range 会被自动设置）
            assert range is not None, "布尔类型时 range 应该已经被自动设置"
            errors.append(f"输入值#{idx} {val} 不在候选列表 {range} 中")
        else:
          checked_val = val_type(val) if val_type is not None else val
          if range is not None:  # 范围校验
            # 候选列表模式
            if isinstance(range, list):
              # 使用 assert 确保 range_set 不为 None
              assert range_set is not None, "候选列表的集合应该已经被设置"
              if checked_val not in range_set:
                errors.append(f"输入值#{idx} {checked_val} 不在候选列表 {range_set} 中")
            # 数值范围模式
            elif isinstance(range, tuple):
              # 使用 assert 确保 min_val 和 max_val 不为 None
              assert min_val is not None and max_val is not None, "范围元组的最小值和最大值应该已经被设置"
              if not (min_val <= checked_val <= max_val):
                errors.append(f"输入值#{idx} {checked_val} 超出范围 [{min_val}, {max_val}]")
      except ValueError:
        # 使用 assert 确保 val_type 不为 None（因为进入这个分支说明有类型转换）
        assert val_type is not None, "类型转换失败时 val_type 应该不为 None"
        errors.append(f"输入值#{idx} '{val}' 不是{val_type.__name__}类型")

      results.append(checked_val)

    # 错误展示
    if errors:
      print("输入错误：\n  " + "\n  ".join(errors))
      continue

    return tuple(results) if len(results) > 1 else results[0]


def main() -> None:
  print(get_input(prompt="请输入3以内的非负整数", def_val=0, val_type=int, range=(0, 3)))
  print(get_input(prompt="请输入布尔值", def_val=False, val_type=bool, range=[0, 1, "t"]))

  ...


if __name__ == "__main__":
  main()

  ...
