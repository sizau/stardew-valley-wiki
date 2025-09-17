from src.ShopService import *


def parse_all_shop_data() -> dict[str, list[dict]]:
    shops = game_data.shops_data
    shops_data: dict[str, list[dict]] = {}

    for shop_name, shop_data in shops.items():
        if shop_name != "Traveler":
            shop = ShopData(shop_data)
        else:
            shop = ShopData(shop_data, is_traveler=True)

        goods: list[dict] = []
        for g in shop.goods:
            goods.append(g.to_dict())

        shops_data[shop_name] = goods

    return shops_data


if __name__ == "__main__":
    ...
