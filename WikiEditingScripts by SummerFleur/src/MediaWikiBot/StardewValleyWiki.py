from mwclient import Site
from pathlib import Path
from utils import FileUtils

_available = False
_sess: dict[str, str] = FileUtils.read_json(Path(__file__).parent.parent.parent / "json" / "SESSDATA.json")
wiki: Site | None = Site("wiki.biligame.com/stardewvalley", path="/")


def initialize(uid: str) -> bool:

    wiki.login(cookies={'SESSDATA': _sess["SummerFleur"]})

    if wiki.username == uid:
        print("Login Successful!")
        return True

    return False


def new_redirect(**kwargs) -> None:
    target_page = wiki.pages[kwargs['page']]
    result = target_page.edit(text=f"#重定向 [[{kwargs['redirect']}]]", summary="重定向")
    print(result)


def flavored_artisan() -> None:
    artisans: dict[str, list[str]] = FileUtils.read_json(Path(__file__).parent / "artisans.json")
    for key, value in artisans.items():
        if key == "Wine":
            for fruit in value:
                target_page = wiki.pages[fruit + "果酒"]
                new_text = f"{{{{:{fruit}|FlavoredArtisan/Wine}}}}"
                result = target_page.edit(text=new_text, summary="使用模板创建具体信息")
                print(result)
        if key == "Jelly":
            for fruit in value:
                target_page = wiki.pages[fruit + "果酱"]
                new_text = f"{{{{:{fruit}|FlavoredArtisan/Jelly}}}}"
                result = target_page.edit(text=new_text, summary="使用模板创建具体信息")
                print(result)
        if key == "Dried Fruit":
            for fruit in value:
                target_page = wiki.pages[fruit + "干"]
                new_text = f"{{{{:{fruit}|FlavoredArtisan/DriedFruit}}}}"
                result = target_page.edit(text=new_text, summary="使用模板创建具体信息")
                print(result)
        if key == "Juice":
            for vegetable in value:
                target_page = wiki.pages[vegetable + "果汁"]
                new_text = f"{{{{:{vegetable}|FlavoredArtisan/Juice}}}}"
                result = target_page.edit(text=new_text, summary="使用模板创建具体信息")
                print(result)
        if key == "Pickles":
            for vegetable in value:
                target_page = wiki.pages["腌制" + vegetable]
                new_text = f"{{{{:{vegetable}|FlavoredArtisan/Pickles}}}}"
                result = target_page.edit(text=new_text, summary="使用模板创建具体信息")
                print(result)
        if key == "Dried Mushrooms":
            for mushroom in value:
                target_page = wiki.pages[mushroom + "干"]
                new_text = f"{{{{:{mushroom}|FlavoredArtisan/DriedMushrooms}}}}"
                result = target_page.edit(text=new_text, summary="使用模板创建具体信息")
                print(result)


def include_transformer(**kwargs) -> str:
    parts = kwargs['text'].split(f"{{{{Infobox {kwargs['type']}")

    count = 0
    ptr = 0
    for letter in parts[-1]:
        ptr += 1

        if letter == "{":
            count += 1
        elif letter == "}":
            count -= 1
        else:
            continue

        if count < 0:
            ptr += 1
            break

    latter = parts[-1][0:ptr] + "</onlyinclude>" + parts[-1][ptr:]
    former = parts[0] if len(parts) == 2 else ""

    return former + f"<onlyinclude>{{{{{{{{{{1|Infobox {kwargs['type']}}}}}}}" + latter


if __name__ == "__main__":
    if not initialize(uid="385505154"):
        exit()

    # do something
