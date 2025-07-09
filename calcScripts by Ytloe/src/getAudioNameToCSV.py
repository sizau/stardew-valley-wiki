from io import StringIO
from pathlib import Path

import pandas as pd
import requests


def make_names_unique(df_column):
  """
  一个健壮的函数，为Pandas Series中的重复项添加数字后缀 (e.g., 'name', 'name (2)', 'name (3)').
  """
  seen_counts = {}
  unique_names = []
  for name in df_column:
    original_name = name
    if name not in seen_counts:
      seen_counts[name] = 1
      unique_names.append(name)
    else:
      count = seen_counts.get(original_name, 0) + 1
      seen_counts[original_name] = count
      new_name = f"{original_name} ({count})"
      while new_name in seen_counts:
        count += 1
        seen_counts[original_name] = count
        new_name = f"{original_name} ({count})"
      seen_counts[new_name] = 1
      unique_names.append(new_name)
  return unique_names


def generate_csv_files():
  """
  根据最终要求，从指定Wiki页面抓取数据，处理后生成两个CSV文件。
  """
  # 需求 4: 使用新的"沙盒"页面URL
  url = "https://wiki.biligame.com/stardewvalley/%E6%B2%99%E7%9B%92:%E9%9F%B3%E9%A2%91"
  headers = {"User-Agent": "Mozilla/5.0"}

  # 需求 1 (路径): 定位到 ../output/csv 文件夹
  # Path(__file__) -> 当前脚本路径
  # .parent -> src 目录
  # .parent -> 项目根目录
  output_dir = Path(__file__).resolve().parent.parent / "output" / "csv"

  # 确保目标目录存在，如果不存在则创建
  output_dir.mkdir(parents=True, exist_ok=True)
  print(f"[信息] 文件将被保存在目录: {output_dir}")

  # 需求 2 (CSV名称): 定义新的CSV文件名
  csv_path_wavebank = output_dir / "wavebank.csv"
  csv_path_wavebank_1_4 = output_dir / "wavebank_1_4.csv"

  print(f"\n正在从 {url} 获取数据...")
  try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    # 让pandas自动检测表头，以适应各种表格结构
    tables = pd.read_html(StringIO(response.text), flavor="lxml")
    print(f"成功获取数据，共发现 {len(tables)} 个表格。")
  except Exception as e:
    print(f"[错误] 解析或请求时发生错误：{e}")
    return

  all_data = pd.DataFrame()
  valid_table_indices = []

  # 遍历所有表格，提取符合条件的数据
  for i, df in enumerate(tables):
    # 将所有列名转为小写字符串以便于匹配
    temp_df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
      # 如果是多级表头，尝试取第二层
      try:
        temp_df.columns = temp_df.columns.get_level_values(1)
      except IndexError:
        # 如果第二层不存在，就跳过这个表
        continue

    temp_df.columns = [str(c).lower() for c in temp_df.columns]

    required_cols = ["name", "wavebank", "hexadecimal"]
    if all(col in temp_df.columns for col in required_cols):
      # 如果表格符合要求，记录其索引并合并数据
      valid_table_indices.append(str(i + 1))
      all_data = pd.concat([all_data, df[df.columns]], ignore_index=True)

  # 需求 1 (日志): 输出总结信息
  if not valid_table_indices:
    print("\n[错误] 在所有表格中均未找到包含 'name', 'wavebank', 'hexadecimal' 的有效表格。")
    return
  print(f"\n[信息] 在 {len(tables)} 个表格中，第 {', '.join(valid_table_indices)} 个表格符合格式要求。")

  # 重命名列以进行统一处理
  all_data.columns = (
    ["name", "wavebank", "decimal", "hexadecimal", "description"]
    if len(all_data.columns) == 5
    else all_data.columns
  )

  # --- 数据清洗和处理 ---
  # 需求 3: 无需对name进行过多处理，只做最基础的清理
  all_data.dropna(subset=["name", "hexadecimal", "wavebank"], inplace=True)
  all_data["hexadecimal"] = all_data["hexadecimal"].astype(str).str.strip()
  all_data["name"] = all_data["name"].astype(str).str.strip()
  # 过滤掉内容是表头本身的行
  all_data = all_data[all_data["name"].str.lower() != "name"]

  # --- 文件生成 ---
  # 分别处理两个wavebank的数据
  for bank_name, csv_path in [("Wavebank", csv_path_wavebank), ("Wavebank(1.4)", csv_path_wavebank_1_4)]:
    df_bank = all_data[all_data["wavebank"].str.lower() == bank_name.lower()].copy()

    if not df_bank.empty:
      # 需求 2 (重名处理): 确保name列唯一
      print(f"\n正在处理 {bank_name} 内的重名...")
      df_bank["name"] = make_names_unique(df_bank["name"])

      output_df = df_bank[["hexadecimal", "name"]]

      # 需求 2 (带表头): to_csv默认header=True，我们只需不设置header=False即可
      output_df.to_csv(csv_path, index=False, encoding="utf-8-sig")

      print(f"成功生成 {csv_path.name}，包含 {len(output_df)} 条记录。")
    else:
      print(f"\n[警告] 未找到 '{bank_name}' 对应的数据。")

  print("\n所有操作完成！")


if __name__ == "__main__":
  generate_csv_files()
