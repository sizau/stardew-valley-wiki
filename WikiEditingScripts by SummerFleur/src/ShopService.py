from src.ItemService import *


class Goods:
    """
    存储商店售卖的物品的类

    Attributes:
        raw: 货物的原始数据字典
        id: 货物的识别标签
        item_id: 物品 ID
        price: 出售价格，若为 -1 则需要进行额外判定
        trade_item_id: 以物易物所需的物品 ID
        trade_item_amount: 以物易物所需的物品数量
        max_stack: 购买限额
        is_recipe: 是否是配方
        ignore_pm: 是否忽略商店价格修饰器
    """
    def __init__(self, goods: dict) -> None:
        self.raw: dict = goods
        self.id: str = goods.get("Id")
        self.item_id: str | None = goods.get("ItemId")
        self.price: int = goods.get("Price")
        self.trade_item_id: str | None = goods.get("TradeItemId")
        self.trade_item_amount: int = goods.get("TradeItemAmount")
        self.max_stack: int = goods.get("MaxStack")
        self.is_recipe: bool = goods.get("IsRecipe")
        self.ignore_pm: bool = goods.get("IgnoreShopPriceModifiers")
        self.item: Item | None = game_data.try_get_item(self.item_id)

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
            raise KeyError("no such field!")


class PriceModifier:
    """
    价格修饰器

    Attributes:
        modification: 修饰方法
        amount: 固定操作数
        random_amount: 随机操作数
    """
    def __init__(self, modifiers: dict[str, Any]) -> None:
        self.modification: str = modifiers.get("Modification")
        self.amount: float = modifiers.get("Amount")
        self.random_amount: list[float] = modifiers.get("RandomAmount")

    def apply(self, goods: Goods) -> int | str:
        """
        应用价格修饰，对物品价格进行处理
        :param goods: 商品实例
        :return: 修饰后的商品价格
        """
        match self.modification:
            # 修饰方法为乘法
            case "Multiply" if self.amount != 0:
                # 若价格修饰器无效，直接返回商品价格
                if goods.ignore_pm:
                    return goods.price
                else:
                    return int(self.amount * goods.price)
            case "Set" if self.amount != 0:
                return int(self.amount)
            case "Set" if self.random_amount is not None:
                return f"{int(min(self.random_amount))} - {int(max(self.random_amount))}"
        return -1


class ShopData:
    def __init__(self, shop: dict, is_traveler=False) -> None:
        self.raw: dict = shop
        self.price_modifiers: PriceModifier | None = None
        self.goods: list[Goods] = []

        # 尝试获取修饰器
        if shop.get("PriceModifiers") is not None:
            self.price_modifiers = PriceModifier(shop.get("PriceModifiers")[0])

        # 若当前商店不是旅行商店
        if not is_traveler:
            for g in shop.get("Items"):
                self.goods.append(Goods(g))
        # 若当前商店是旅行商店
        else:
            # 获取猪车全部可能出售的物品
            for random_id in range(2, 790):
                item = game_data.try_get_item(str(random_id))
                # 看是否被排除
                if item is None or item.category == -999 or item.get_field("ExcludeFromRandomSale") is True:
                    continue
                g = Goods(shop.get("Items")[0])
                g.price = item.sellprice
                g.id = f"RandomSale (O){random_id}"
                g.item_id = Item.qualify(str(random_id))
                self.goods.append(g)

        self._apply_price_modifiers()

    def try_get_goods(self, code: str) -> Goods | None:
        """
        根据物品的 QualifiedItemID 来创建 Goods 实例。
        :param code: 物品的 QualifiedItemID
        :return: 商品实例
        """
        try:
            for g in self.goods:
                trimmed_id = Item.trim(g.item_id)
                if trimmed_id == code:
                    return g
            return None
        except (KeyError, TypeError):
            return None

    def _apply_price_modifiers(self) -> None:
        """
        应用商店价格修饰器
        :return: 修饰后的物品价格
        """
        for g in self.goods:
            if g.is_recipe:
                g.price *= 10
            elif g.price < 0 and g.item is not None:
                g.price = g.item.sellprice * 2

            if self.price_modifiers is not None:
                g.price = self.price_modifiers.apply(g)


class ShopManager:
    def __init__(self) -> None:
        self.seed_shop = ShopData(game_data.shops_data.get("SeedShop"))
        self.joja_mart = ShopData(game_data.shops_data.get("Joja"))
        self.oasis = ShopData(game_data.shops_data.get("Sandy"))
        self.traveler = ShopData(game_data.shops_data.get("Traveler"), is_traveler=True)
        self.island_trade = ShopData(game_data.shops_data.get("IslandTrade"))
        self.raccoon_shop = ShopData(game_data.shops_data.get("Raccoon"))
        self.nmday1 = ShopData(game_data.shops_data.get("Festival_NightMarket_MagicBoat_Day1"))
        self.nmday2 = ShopData(game_data.shops_data.get("Festival_NightMarket_MagicBoat_Day2"))
        self.nmday3 = ShopData(game_data.shops_data.get("Festival_NightMarket_MagicBoat_Day3"))


if __name__ == "__main__":
    ...
