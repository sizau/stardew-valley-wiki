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
