import math
import re
from pathlib import Path
from typing import Any

from utils import FileUtils


class GameData:
    """
    存储游戏数据的类

    Attributes:
        objects_data: 解析 Object.json 得到的字典
        objects_zh_cn: 英文名 -> 中文名
        bigcraftables_data: 解析 Bigcraftables.json 得到的字典
        bigcraftables_zh_cn: 英文名 -> 中文名
        crops_data: 解析 Crops.json 得到的字典
        namespace: 当前位于哪个空间，Vanilla 为原版，或 SVE
    """

    def __init__(self, namespace="Vanilla") -> None:
        self.objects_data: dict[str, dict] = {}
        self.objects_zh_cn: dict[str, str] = {}
        self.bigcraftables_data: dict[str, dict] = {}
        self.bigcraftables_zh_cn: dict[str, str] = {}
        self.crops_data: dict[str, dict] = {}
        self.namespace = namespace

    def read_json_files(self) -> None:
        """读取 JSON 文件，获取 Object 和 BigCraftable 信息"""
        json_path = Path(__file__).parent.parent / "json"
        self.objects_data = FileUtils.read_json(json_path / "Objects.json")
        self.objects_zh_cn = FileUtils.read_json(json_path / "Objects.zh-CN.json")
        self.bigcraftables_data = FileUtils.read_json(json_path / "BigCraftables.json")
        self.bigcraftables_zh_cn = FileUtils.read_json(json_path / "BigCraftables.zh-CN.json")
        self.crops_data = FileUtils.read_json(json_path / "Crops.json")

    def read_json_files_sve(self) -> None:
        """读取 SVE JSON 文件，获取 Object 和 BigCraftable 信息"""
        json_path = Path(__file__).parent.parent / "json_sve"
        self.objects_data = FileUtils.read_json(json_path / "Objects.json")
        self.bigcraftables_data = FileUtils.read_json(json_path / "BigCraftables.json")
        self.namespace = "SVE"


class Item:
    """
    物品类，存储物品的前缀、代码、数量和名称

    Attributes:
        raw: 物品的原始数据字典
        name: 物品的英语名称
        category: 物品类型值，例如 -79
        sellprice: 物品的出售价格
        edibility: 物品的可食用性
        color: 物品的颜色值
    """

    def __init__(self, item: dict) -> None:
        self.raw: dict = item
        self.name: str = item.get("Name")
        self.category: int = item.get("Category")
        self.sellprice: int = item.get("Price")
        self.edibility: int = item.get("Edibility")
        self.color: str = self._get_color()

    def _get_color(self) -> str:
        """
        从 ContextTags 中获取物品的颜色值
        :return: 物品的颜色值，若未获取到，则返回空字符串
        """
        tags: list[str] = self.raw.get("ContextTags")
        if tags is None:
            return ""

        for tag in tags:
            if tag.startswith("color_"):
                return tag[6:]
        return ""

    @staticmethod
    def get_name(code: str, data: GameData) -> str:
        data_source = data.objects_data
        if code in data_source:
            item_data = data_source[code]
            name = item_data.get("Name", "")

            return name

        return "未知物品"

    @staticmethod
    def get_display_name(code: str, data: GameData) -> str:
        data_source = data.objects_data
        if code in data_source:
            item_data = data_source[code]
            display_name = item_data.get("DisplayName", "")

            # 解析DisplayName中的本地化键
            if display_name.startswith("[LocalizedText"):
                # 提取本地化键，格式如 "[LocalizedText Strings\Objects:Moss_Name]"

                match = re.search(r":([^]]+)_Name]", display_name)
                if match:
                    localization_key = match.group(1) + "_Name"
                    # 从本地化文件中获取名称
                    if localization_key in data.objects_zh_cn:
                        return data.objects_zh_cn[localization_key]

        return "未知物品"

    def get_field(self, field: str) -> Any:
        """
        获取物品的指定属性信息
        :param field: 需要获取的属性
        :exception KeyError: 不存在该属性
        """
        try:
            return self.raw[field]
        except Exception:
            raise KeyError("no such field!")


class Crop:
    """
    物品类，存储物品的前缀、代码、数量和名称

    Attributes:
        raw: 物品的原始数据字典
        harvest: 作物收获得到的物品
        growth: 作物成熟所需时间
        seasons: 作物生长的季节
    """

    def __init__(self, crop: dict):
        self.raw: dict = crop
        self.harvest: str = crop.get("HarvestItemId")
        self.growth: int = sum(crop.get("DaysInPhase"))
        self.seasons: str = self._get_season(crop.get("Seasons"))

    @staticmethod
    def _get_season(seasons: list[str]) -> str:
        """将 list[seasons] 转化为 wiki 格式"""
        string = ""
        for s in seasons:
            string = string + "{{Season|" + s + "}} • "
        return string[:-3]

    @staticmethod
    def get_xp(sellprice: int) -> int:
        """使用游戏内的经验计算公式，传入作物售价以计算收获作物得到的经验值"""
        exp = 16 * math.log(0.018 * sellprice + 1)
        exp = round(exp, 0)
        return int(exp)

    def get_field(self, field: str) -> Any:
        """
        获取物品的指定属性信息
        :param field: 需要获取的属性
        :exception KeyError: 不存在该属性
        """
        try:
            return self.raw[field]
        except Exception:
            raise KeyError("no such field!")


if __name__ == "__main__":
    Data = GameData()
    Data.read_json_files_sve()
    print(Data.objects_data)
