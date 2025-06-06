"""
Utils - Python通用工具库
包含各种实用工具类和函数，提高开发效率
"""

import datetime
import hashlib
import json
import os
import time
from functools import wraps
from inspect import stack
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import psutil

# ==================== 性能监控模块 ====================


class PerfMonitor:
  """
  性能监控器

  使用方式:
  1. 上下文管理器: with PerfMonitor() as monitor: ...
  2. 装饰器: @PerfMonitor.measure
  3. 手动控制: monitor = PerfMonitor(); monitor.start(); ...; monitor.stop()
  """

  def __init__(self, name: str = "Performance"):
    """
    初始化性能监控器

    Args:
        name: 监控任务名称，用于输出时的标识
    """
    self.name = name
    self.start_time: Optional[float] = None
    self.start_memory: Optional[int] = None
    self.end_time: Optional[float] = None
    self.end_memory: Optional[int] = None
    self.process = psutil.Process(os.getpid())
    self._is_running = False
    self._stats: Optional[Dict[str, Any]] = None  # 保存统计信息

  def start(self) -> "PerfMonitor":
    """开始监控"""
    if self._is_running:
      raise RuntimeError("监控器已经在运行中")

    # 强制垃圾回收以获得更准确的内存读数
    import gc

    gc.collect()

    self.start_time = time.time()
    self.start_memory = self.process.memory_info().rss
    self._is_running = True
    return self

  def stop(self) -> Dict[str, Any]:
    """停止监控并返回统计数据"""
    if not self._is_running:
      raise RuntimeError("监控器尚未启动")

    if self.start_time is None or self.start_memory is None:
      raise RuntimeError("监控器数据不完整")

    self.end_time = time.time()
    self.end_memory = self.process.memory_info().rss
    self._is_running = False

    # 保存统计信息
    self._stats = self._calculate_stats()
    return self._stats

  def _calculate_stats(self) -> Dict[str, Any]:
    """计算统计数据"""
    if self.start_time is None or self.end_time is None or self.start_memory is None or self.end_memory is None:
      raise RuntimeError("数据不完整，无法计算统计信息")

    elapsed_ms = (self.end_time - self.start_time) * 1000
    memory_delta = self.end_memory - self.start_memory

    return {
      "name": self.name,
      "elapsed_ms": elapsed_ms,
      "memory_delta_bytes": memory_delta,
      "memory_delta_mb": memory_delta / 1024 / 1024,
      "final_memory_bytes": self.end_memory,
      "final_memory_mb": self.end_memory / 1024 / 1024,
    }

  def get_stats(self) -> Dict[str, Any]:
    """获取性能统计数据"""
    if self._stats is not None:
      return self._stats

    if self.start_time is None or self.end_time is None or self.start_memory is None or self.end_memory is None:
      raise RuntimeError("没有可用的性能数据")

    return self._calculate_stats()

  def print_stats(self, prefix: str = "") -> None:
    """打印格式化的统计信息"""
    stats = self.get_stats()
    output = f"{prefix}=== {stats['name']} 性能统计 ===\n"
    output += f"{prefix}运行时间: {stats['elapsed_ms']:.2f}ms\n"
    output += f"{prefix}内存增量: {stats['memory_delta_bytes']:,} bytes ({stats['memory_delta_mb']:.2f} MB)\n"
    output += f"{prefix}当前内存: {stats['final_memory_bytes']:,} bytes ({stats['final_memory_mb']:.2f} MB)"
    print(output)

  def format_stats(self, prefix: str = "") -> str:
    """返回格式化的统计信息字符串"""
    stats = self.get_stats()
    output = f"{prefix}=== {stats['name']} 性能统计 ===\n"
    output += f"{prefix}运行时间: {stats['elapsed_ms']:.2f}ms\n"
    output += f"{prefix}内存增量: {stats['memory_delta_bytes']:,} bytes ({stats['memory_delta_mb']:.2f} MB)\n"
    output += f"{prefix}当前内存: {stats['final_memory_bytes']:,} bytes ({stats['final_memory_mb']:.2f} MB)"
    return output

  # 上下文管理器支持
  def __enter__(self) -> "PerfMonitor":
    self.start()
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.stop()
    return False

  # 装饰器支持
  @staticmethod
  def measure(name: str = "Function"):
    """
    装饰器：自动测量函数性能

    使用方式:
    @PerfMonitor.measure("MyFunction")
    def my_function(): ...
    """

    def decorator(func: Callable) -> Callable:
      @wraps(func)
      def wrapper(*args, **kwargs):
        monitor = PerfMonitor(name)
        monitor.start()
        try:
          result = func(*args, **kwargs)
        finally:
          monitor.stop()
          monitor.print_stats()
        return result

      return wrapper

    return decorator


# ==================== 文件操作模块 ====================


class FileUtils:
  """文件操作工具类"""

  @staticmethod
  def read_json(filepath: Union[str, Path], encoding: str = "utf-8") -> Dict:
    """安全读取JSON文件"""
    filepath = Path(filepath)
    try:
      with filepath.open("r", encoding=encoding) as f:
        return json.load(f)
    except FileNotFoundError:
      raise FileNotFoundError(f"找不到文件: {filepath}")
    except json.JSONDecodeError as e:
      raise ValueError(f"JSON解析错误 in {filepath}: {e}")

  @staticmethod
  def write_json(data: Dict, filepath: Union[str, Path], encoding: str = "utf-8", indent: int = 2) -> None:
    """写入JSON文件"""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with filepath.open("w", encoding=encoding) as f:
      json.dump(data, f, ensure_ascii=False, indent=indent)

  @staticmethod
  def get_file_hash(filepath: Union[str, Path], algorithm: str = "md5") -> str:
    """计算文件哈希值"""
    filepath = Path(filepath)
    hash_func = getattr(hashlib, algorithm)()
    with filepath.open("rb") as f:
      for chunk in iter(lambda: f.read(4096), b""):
        hash_func.update(chunk)
    return hash_func.hexdigest()


# ==================== 字符串处理模块 ====================


class StringUtils:
  """字符串处理工具类"""

  @staticmethod
  def get_display_width(text: str) -> int:
    """计算字符串的显示宽度（中文字符算2，英文字符算1）"""
    width = 0
    for char in text:
      if (
        ("\u4e00" <= char <= "\u9fff")  # CJK统一汉字
        or ("\u3000" <= char <= "\u303f")  # CJK标点符号
        or ("\uff00" <= char <= "\uffef")  # 全角ASCII、全角标点
        or ("\u2000" <= char <= "\u206f")  # 常用标点
        or ("\u3200" <= char <= "\u32ff")  # 括号CJK字符
        or ("\u3300" <= char <= "\u33ff")  # CJK兼容
        or ("\u2e80" <= char <= "\u2eff")  # CJK部首补充
        or ("\u3400" <= char <= "\u4dbf")  # CJK扩展A
        or ("\u2f00" <= char <= "\u2fdf")  # 康熙部首
        or char in "（）【】《》「」『』〈〉〔〕｛｝"
      ):
        width += 2
      else:
        width += 1
    return width

  @staticmethod
  def pad_to_width(text: str, target_width: int, fill_char: str = " ") -> str:
    """填充字符串到指定显示宽度"""
    current_width = StringUtils.get_display_width(text)
    padding_needed = target_width - current_width
    return text + fill_char * padding_needed


# ==================== 日志记录模块 ====================


class Logger:
  """简单的日志记录器"""

  def __init__(self, name: str = "Logger", save_to_file: bool = False, filepath: Optional[Path] = None):
    self.name = name
    self.save_to_file = save_to_file
    self.filepath = filepath or Path(f"{name}_{datetime.datetime.now():%Y%m%d_%H%M%S}.log")
    self.logs: List[str] = []

  def log(self, message: str, level: str = "INFO") -> None:
    """记录日志"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] [{level}] {message}"
    print(formatted_message)
    self.logs.append(formatted_message)

    if self.save_to_file:
      with self.filepath.open("a", encoding="utf-8") as f:
        f.write(formatted_message + "\n")

  def info(self, message: str) -> None:
    self.log(message, "INFO")

  def warning(self, message: str) -> None:
    self.log(message, "WARNING")

  def error(self, message: str) -> None:
    self.log(message, "ERROR")

  def get_logs(self) -> List[str]:
    """获取所有日志"""
    return self.logs.copy()


# ==================== 便捷函数 ====================


def measure_performance(name: str = "Task") -> PerfMonitor:
  """创建并启动一个性能监控器"""
  return PerfMonitor(name).start()


def timer(func: Callable) -> Callable:
  """简单的计时装饰器"""

  @wraps(func)
  def wrapper(*args, **kwargs):
    start = time.time()
    result = func(*args, **kwargs)
    elapsed = (time.time() - start) * 1000
    print(f"{func.__name__} 执行时间: {elapsed:.2f}ms")
    return result

  return wrapper


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
