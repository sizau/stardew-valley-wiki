"""
utils.py 库的测试和示例程序
展示所有工具类的使用方法
"""

import time
from pathlib import Path

from utils import FileUtils, Logger, PerfMonitor, StringUtils, measure_performance, timer


def test_performance_monitor():
  """测试性能监控器的各种使用方式"""
  print("\n" + "=" * 60)
  print("性能监控器 (PerfMonitor) 测试")
  print("=" * 60)

  # 方式1: 手动控制
  print("\n1. 手动控制方式:")
  monitor = PerfMonitor("手动监控示例")
  monitor.start()

  # 模拟一些工作
  total = 0
  for i in range(1000000):
    total += i
  time.sleep(0.1)  # 模拟耗时操作

  monitor.stop()
  monitor.print_stats("  ")

  # 方式2: 上下文管理器
  print("\n2. 上下文管理器方式:")
  with PerfMonitor("上下文管理器示例") as monitor:
    # 模拟工作
    data = [i**2 for i in range(100000)]
    time.sleep(0.05)

  # 获取原始统计数据
  stats = monitor.get_stats()
  print(f"  原始数据: 运行时间={stats['elapsed_ms']:.2f}ms, 内存增量={stats['memory_delta_mb']:.2f}MB")

  # 方式3: 装饰器
  print("\n3. 装饰器方式:")

  @PerfMonitor.measure("斐波那契计算")
  def fibonacci(n):
    if n <= 1:
      return n
    a, b = 0, 1
    for _ in range(2, n + 1):
      a, b = b, a + b
    return b

  result = fibonacci(10000)
  print(f"  斐波那契(10000)的前10位: {str(result)[:10]}...")

  # 方式4: 便捷函数
  print("\n4. 便捷函数方式:")
  perf = measure_performance("快速任务")
  # 执行任务
  squares = {i: i**2 for i in range(10000)}
  perf.stop()
  print(perf.format_stats("  "))


def test_file_utils():
  """测试文件操作工具"""
  print("\n" + "=" * 60)
  print("文件操作工具 (FileUtils) 测试")
  print("=" * 60)

  # 准备测试数据
  test_data = {
    "name": "测试数据",
    "version": "1.0",
    "items": ["项目1", "项目2", "项目3"],
    "config": {"debug": True, "timeout": 30},
  }

  # 测试JSON写入
  print("\n1. 写入JSON文件:")
  test_file = Path("test_output.json")
  FileUtils.write_json(test_data, test_file)
  print(f"  已写入文件: {test_file}")

  # 测试JSON读取
  print("\n2. 读取JSON文件:")
  loaded_data = FileUtils.read_json(test_file)
  print(f"  读取的数据: {loaded_data}")

  # 测试文件哈希
  print("\n3. 计算文件哈希:")
  md5_hash = FileUtils.get_file_hash(test_file, "md5")
  sha256_hash = FileUtils.get_file_hash(test_file, "sha256")
  print(f"  MD5: {md5_hash}")
  print(f"  SHA256: {sha256_hash}")

  # 测试错误处理
  print("\n4. 错误处理测试:")
  try:
    FileUtils.read_json("不存在的文件.json")
  except FileNotFoundError as e:
    print(f"  捕获到预期的错误: {e}")

  # 清理测试文件
  test_file.unlink()
  print("\n  测试文件已清理")


def test_string_utils():
  """测试字符串处理工具"""
  print("\n" + "=" * 60)
  print("字符串处理工具 (StringUtils) 测试")
  print("=" * 60)

  # 测试显示宽度计算
  print("\n1. 计算字符串显示宽度:")
  test_strings = ["Hello World", "你好世界", "Hello你好World世界", "（括号）【测试】", "emoji😀test"]

  for s in test_strings:
    width = StringUtils.get_display_width(s)
    print(f"  '{s}' -> 宽度: {width}")

  # 测试字符串填充
  print("\n2. 字符串填充到指定宽度:")
  items = [("苹果", 10), ("香蕉", 5), ("西瓜", 20), ("Apple", 8), ("Banana", 15)]

  print("  商品名称          | 数量")
  print("  " + "-" * 30)

  for name, quantity in items:
    padded_name = StringUtils.pad_to_width(name, 20)
    print(f"  {padded_name}| {quantity:>4}")

  # 测试不同填充字符
  print("\n3. 使用不同的填充字符:")
  text = "标题"
  padded1 = StringUtils.pad_to_width(text, 20, "-")
  padded2 = StringUtils.pad_to_width(text, 20, "=")
  padded3 = StringUtils.pad_to_width(text, 20, "*")

  print(f"  '{padded1}'")
  print(f"  '{padded2}'")
  print(f"  '{padded3}'")


def test_logger():
  """测试日志记录器"""
  print("\n" + "=" * 60)
  print("日志记录器 (Logger) 测试")
  print("=" * 60)

  # 创建不保存文件的日志记录器
  print("\n1. 基本日志记录（不保存文件）:")
  logger1 = Logger("TestLogger")

  logger1.info("这是一条信息日志")
  logger1.warning("这是一条警告日志")
  logger1.error("这是一条错误日志")

  # 创建保存到文件的日志记录器
  print("\n2. 日志记录（保存到文件）:")
  log_file = Path("test.log")
  logger2 = Logger("FileLogger", save_to_file=True, filepath=log_file)

  logger2.info("程序启动")
  logger2.info("正在处理数据...")
  logger2.warning("内存使用率较高")
  logger2.error("无法连接到数据库")
  logger2.info("程序结束")

  # 获取所有日志
  print("\n3. 获取所有日志记录:")
  all_logs = logger2.get_logs()
  print(f"  共有 {len(all_logs)} 条日志")
  print("  最后两条日志:")
  for log in all_logs[-2:]:
    print(f"    {log}")

  # 检查日志文件
  if log_file.exists():
    print(f"\n4. 日志文件已创建: {log_file}")
    print("  文件内容预览:")
    with log_file.open("r", encoding="utf-8") as f:
      lines = f.readlines()
      for line in lines[:3]:  # 显示前3行
        print(f"    {line.strip()}")

    # 清理日志文件
    log_file.unlink()
    print("  日志文件已清理")


def test_timer_decorator():
  """测试计时装饰器"""
  print("\n" + "=" * 60)
  print("计时装饰器 (timer) 测试")
  print("=" * 60)

  @timer
  def slow_function(n):
    """模拟耗时函数"""
    total = 0
    for i in range(n):
      total += i**0.5
    time.sleep(0.1)  # 模拟IO操作
    return total

  @timer
  def quick_function():
    """快速函数"""
    return sum(range(1000))

  print("\n执行函数:")
  result1 = slow_function(100000)
  result2 = quick_function()

  print("\n函数返回值:")
  print(f"  slow_function: {result1:.2f}")
  print(f"  quick_function: {result2}")


def test_combined_usage():
  """测试组合使用多个工具"""
  print("\n" + "=" * 60)
  print("组合使用示例")
  print("=" * 60)

  # 创建日志记录器
  logger = Logger("DataProcessor")

  # 使用性能监控器监控整个过程
  with PerfMonitor("数据处理任务") as monitor:
    logger.info("开始处理数据")

    # 模拟数据处理
    data = {"users": ["张三", "李四", "王五"], "scores": [85, 92, 78], "timestamp": "2024-01-01"}

    # 保存数据
    logger.info("保存数据到文件")
    FileUtils.write_json(data, "temp_data.json")

    # 读取并处理数据
    logger.info("读取并处理数据")
    loaded_data = FileUtils.read_json("temp_data.json")

    # 格式化输出
    print("\n  成绩单:")
    print("  " + "-" * 30)
    for user, score in zip(loaded_data["users"], loaded_data["scores"]):
      padded_name = StringUtils.pad_to_width(user, 10)
      print(f"  {padded_name} | {score:>3} 分")

    logger.info("数据处理完成")

    # 清理临时文件
    Path("temp_data.json").unlink()

  # 显示性能统计
  print("\n" + monitor.format_stats("  "))


def main():
  """主测试函数"""
  print("Utils 库功能测试")
  print("=" * 60)

  # 运行所有测试
  test_performance_monitor()
  test_file_utils()
  test_string_utils()
  test_logger()
  test_timer_decorator()
  test_combined_usage()

  print("\n" + "=" * 60)
  print("所有测试完成！")
  print("=" * 60)


if __name__ == "__main__":
  main()
