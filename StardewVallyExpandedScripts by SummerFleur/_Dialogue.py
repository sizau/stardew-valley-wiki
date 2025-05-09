import json


def character_dialogue(name):
    with open(f"Characters/{name}/Dialogue.json") as f:
        f = json.load(f)
    with open("zh.json") as zh:
        zh = json.load(zh)
    with open("en.json") as en:
        en = json.load(en)

    f_keys = f.keys()
    for desc in f_keys:
        ID = f.get(desc)
        ID = ID.replace("{{", "").replace("}}", "").replace("i18n:", "")
        print(f"//{desc}")
        print(f'"{ID}": \n{en.get(ID)}\n')


if __name__ == "__main__":
    character_dialogue("Lance")
