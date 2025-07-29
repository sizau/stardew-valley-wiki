本目录内主要包括一些在编写 Wiki 时能用到的自动化工具，通过读取游戏的解包数据，可以实现诸如数据解析等很多功能。

本目录内全部脚本使用的协议为 [GPL-3.0 license](LICENSE)，其中包含游戏数据的解包文件仅用作学习交流，不用做任何商业目的。

The scripts in this directory are licensed under the [GPL-3.0 license](LICENSE). Unpacked game data files included herein are solely for learning and exchange purposes, not for any commercial use.

## 准备工作

本目录内需要使用 [@ytloe](https://github.com/ytloe) 在本仓库内的 [calcScripts](../calcScripts%20by%20Ytloe) 作为前置。因此需要先安装其项目的全部依赖。

然后再安装本项目所需的依赖，已经写在 pyproject.toml 里了，如果使用了包管理器或者 PyCharm，那么应该可以很方便的安装依赖。

#### json 目录

这两个目录分别用于存放解包获得的游戏 json 文件和 sve 相关的 json 文件，若将来版本更新，只需要重新解包并导入即可。

需要放入的原版 json 文件有：
- `Data\BigCraftables.json`
- `Data\Crops.json`
- `Data\FruitTrees.json`
- `Data\Objects.json`
- `Strings\BigCraftables.zh-CN.json`
- `Strings\Objects.zh-CN.json`

#### json_sve 目录

sve 需要放入的内容则仅包括上面列出来的前四个位于 `Data` 目录下的文件，以及中文汉化文件。需要注意的是 sve 的数据需要进行手动处理，处理步骤大致为：

1. 由于 sve 的数据是写给 ContentPatcher 看的，因此要把 Changes 列表内第一个字典中 `Entries` 键所对应的值给取出来，其余部分全部舍弃；
2. 修改所有不符合 `json` 规范的语法，例如注释和尾随逗号，现代化的 IDE 或 VSC 的插件应该都能很方便的自动处理它们；
3. 放到 json_sve 目录下。

需要确保在 IDE 中查看 sve 相关的数据时没有标红，否则脚本无法解析。

## ItemService.py

本模块用于解析游戏内所有 `Object` 的基础数据，并自定义了一个 `Item` 类，提取了一些常用的数据字段和属性，对于农作物，还定义了一个 `Crop` 类和 ` FruitTree` 类用于存储农作物的常用数据。

具体使用方法已在文件注释里详细说明。

## Infobox_generator

该目录下的脚本主要用于自动生成 Wiki 内物品详情页面中的 Infobox。其原理非常简单：解析游戏 json 数据，获取 Wiki Infobox 所接受的数据，然后打印出来。

- 对于 `Infobox_craft_generator.py`，生成的是游戏内全部可打造物品的 Infobox；
- 对于 `Infobox_vfff_generator.py`，生成的是游戏内全部蔬菜（vegetables）、水果（fruits）、花（flowers）和采集品（forages）的 Infobox。

具体使用方法已在文件注释里详细说明，使用时只需要在 `if __name__ == "__main__":` 下更改相关参数即可。

## Picture_processor

该目录下仅有一个脚本，主要用于对图片进行处理，例如缩放、裁切、添加颜色遮罩等，这些功能应该都是在 Wiki 编写时时常会用到的。

具体使用方法也已在文件注释里详细说明。