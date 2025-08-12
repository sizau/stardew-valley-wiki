from __future__ import annotations
import math
import re
from pathlib import Path
from typing import Any, Literal

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
        fruit_trees_data: 解析 FruitTrees.json 得到的字典
        namespace: 当前位于哪个空间，Vanilla 为原版，或 SVE
    """

    def __init__(self, namespace: Literal["Vanilla", "SVE"] = "Vanilla") -> None:
        self.objects_data: dict[str, dict] = {}
        self.objects_zh_cn: dict[str, str] = {}
        self.bigcraftables_data: dict[str, dict] = {}
        self.bigcraftables_zh_cn: dict[str, str] = {}
        self.crops_data: dict[str, dict] = {}
        self.fruit_trees_data: dict[str, dict] = {}
        self.shops_data: dict[str, dict] = {}
        self.item_id: dict[str, str] = {}
        self.namespace = namespace

        # 根据命名空间，获取相关原始数据
        match namespace:
            # 读取原版 JSON 文件
            case "Vanilla":
                json_path = Path(__file__).parent.parent / "json"
                self.objects_data = FileUtils.read_json(json_path / "Objects.json")
                self.objects_zh_cn = FileUtils.read_json(json_path / "Objects.zh-CN.json")
                self.bigcraftables_data = FileUtils.read_json(json_path / "BigCraftables.json")
                self.bigcraftables_zh_cn = FileUtils.read_json(json_path / "BigCraftables.zh-CN.json")
                self.crops_data = FileUtils.read_json(json_path / "Crops.json")
                self.fruit_trees_data = FileUtils.read_json(json_path / "FruitTrees.json")
                self.shops_data = FileUtils.read_json(json_path / "Shops.json")
                self.item_id = FileUtils.read_json(json_path / "ItemID.json")
            # 读取 SVE JSON 文件
            case "SVE":
                json_path = Path(__file__).parent.parent / "json_sve"
                self.objects_data = FileUtils.read_json(json_path / "Objects.json")
                self.objects_zh_cn = self.bigcraftables_zh_cn = FileUtils.read_json(json_path / "zh.json")
                self.bigcraftables_data = FileUtils.read_json(json_path / "BigCraftables.json")
                self.bigcraftables_zh_cn = self.bigcraftables_zh_cn = FileUtils.read_json(json_path / "zh.json")
                self.crops_data = FileUtils.read_json(json_path / "Crops.json")
                self.fruit_trees_data = FileUtils.read_json(json_path / "FruitTrees.json")
                self.namespace = "SVE"

        if self.objects_data == {}:
            raise ValueError("不合法的命名空间！")

    def try_get_item(self, code: str) -> Item | None:
        """
        根据物品的 QualifiedItemID 来创建 Item 实例。
        :param code: 物品的 QualifiedItemID
        :return: 物品实例
        :exception KeyError: 未找到对应的物品
        """
        try:
            code = Item.trim(code)
            item = self.objects_data[code]
            return Item(item)
        except (KeyError, TypeError):
            return None

    def try_get_crop(self, code: str) -> Crop | None:
        """
        根据作物种子的 QualifiedItemID 来创建 Crop 实例。
        :param code: 作物种子的 QualifiedItemID
        :return: 作物种子实例
        :exception KeyError: 未找到对应的作物
        """
        try:
            code = Item.trim(code)
            crop = self.objects_data[code]
            return Crop(crop)
        except (KeyError, TypeError):
            return None

    def try_get_fruit(self, code: str) -> FruitTree | None:
        """
        根据果树树苗的 QualifiedItemID 来创建 FruitTree 实例。
        :param code: 果树树苗的 QualifiedItemID
        :return: 果树树苗实例
        :exception KeyError: 未找到对应的果树
        """
        try:
            code = Item.trim(code)
            fruit = self.objects_data[code]
            return FruitTree(fruit)
        except (KeyError, TypeError):
            return None

    def quick_get_name(self, code: str) -> str | None:
        """
        快速获取物品的内部名称（英文）
        :param code: 物品的 QualifiedItemId
        :return: 物品的内部名称
        """
        data_source = self.item_id
        return data_source.get(code)

    def get_name(self, code: str) -> str:
        """
        获取物品的内部名称（英文）
        :param code: 物品的 QualifiedItemId
        :return: 物品的内部名称
        """
        data_source = self.objects_data
        if code in data_source:
            item_data = data_source[code]
            name = item_data.get("Name", "")

            return name

        return "未知物品"

    def get_display_name(self, code: str) -> str:
        """
        获取物品的本地化名称，仅限于原版物品
        :param code: 物品的 QualifiedItemId
        :return: 物品的本地化名称
        """
        data_source = self.objects_data
        if code in data_source:
            item_data = data_source[code]
            display_name = item_data.get("DisplayName", "")
            localization_key = None

            match self.namespace:
                case "Vanilla":
                    # 解析DisplayName中的本地化键
                    if display_name.startswith("[LocalizedText"):
                        # 提取本地化键，格式如 "[LocalizedText Strings\Objects:Moss_Name]"
                        match = re.search(r":([^]]+)_Name]", display_name)
                        if match:
                            localization_key = match.group(1) + "_Name"
                case "SVE":
                    # 解析DisplayName中的本地化键
                    if display_name.startswith("{{i18n:"):
                        # 提取本地化键，格式如 "[LocalizedText Strings\Objects:Moss_Name]"
                        match = re.search(r"\{\{i18n:([^}]+)}}", display_name)
                        if match:
                            localization_key = match.group(1)

            if localization_key is None:
                raise ValueError("unknown namespace!")

            # 从本地化文件中获取名称
            if localization_key in self.objects_zh_cn:
                return self.objects_zh_cn[localization_key]

        return "未知物品"


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
                return tag[6:].replace("_", " ")
        return ""

    @staticmethod
    def trim(code: str) -> str:
        """
        去除物品代码的 “(O)” 前缀
        :param code: 需要去除前缀的物品代码
        :return: 去除前缀后的物品代码
        :exception TypeError: 物品代码类型不合法
        """
        if type(code) is not str:
            raise TypeError("code must be str!")
        if code.startswith("(O)"):
            return code[3:]
        return code

    @staticmethod
    def qualify(code: str) -> str:
        if code.startswith("(O)"):
            return code
        return "(O)" + code

    def get_field(self, field: str) -> Any:
        """
        获取物品的指定属性信息
        :param field: 需要获取的属性
        :exception KeyError: 不存在该属性
        :return: 获取到的物品属性
        """
        try:
            return self.raw[field]
        except KeyError:
            return "No such field!"


class Crop:
    """
    作物类，存储作物的各项基本数据

    Attributes:
        raw: 作物的原始数据字典
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
        if len(string) == 78:
            return "All"
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
        except KeyError:
            return "No such field!"


class FruitTree:
    """
    果树类，存储果树的各项基本数据

    Attributes:
        raw: 作物的原始数据字典
        harvest: 果树收获得到的果实
        seasons: 作物生长的季节
    """

    def __init__(self, fruit_tree: dict):
        self.raw: dict = fruit_tree
        self.harvest: str = fruit_tree.get("Fruit")[0].get("ItemId")
        self.seasons: str = self._get_season(fruit_tree.get("Seasons"))

    @staticmethod
    def _get_season(seasons: list[str]) -> str:
        """将 list[seasons] 转化为 wiki 格式"""
        string = ""
        for s in seasons:
            string = string + "{{Season|" + s + "}} • "
        return string[:-3]

    def get_field(self, field: str) -> Any:
        """
        获取物品的指定属性信息
        :param field: 需要获取的属性
        :exception KeyError: 不存在该属性
        """
        try:
            return self.raw[field]
        except KeyError:
            return "No such field!"


if __name__ != "__main__":
    game_data = GameData()
