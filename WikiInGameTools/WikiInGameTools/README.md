## Wiki 游戏内工具

此项目主要包含了几个编写 Wiki 时会用到的实用工具。

本模组计划采用模块化设计，因此理论上在制作时所有模块均应实现 `Framework.IModule`，同时存放于独立的文件夹中。若考虑将工具内的模块发布为模组，请新建一个项目，然后弃用模块化设计即可。

- **CalcFishesProb** ([文档](CalcFishesProb/README.md))  
  此模块用于将指定地点、天气、时间的条件下所有可能出现的鱼类列表导出为 `.json`，然后将这些文件作为原始数据传入 [@ytloe](https://github.com/ytloe) 开发的 [calcFishesProb.py](../../calcScripts%20by%20Ytloe/src/calcFishesProb.py) 脚本进行后续具体概率的计算。
- **DebugModule** ([文档](DebugModule/README.md))  
  测试用模块，可以在这个模块里添加各种对原版调试用的代码（增加补丁类记得在 DebugModule 里注册）
- **GetNPCGiftTastes** ([文档](GetNPCGiftTastes/README.md))  
  此模块添加了三个控制台命令，用于获取所有 NPC 对指定物品的态度，或指定的 NPC 对所有物品的态度，并将结果输出为 Wiki 可用的格式。
- **VariableMonitor** ([文档](VariableMonitor/README.md))  
  本模块允许您通过编辑 `Data/MonitorTarget.json` 文件，在游戏运行时动态监控特定方法中的变量值，并将结果输出到 SMAPI 控制台。这对于 Mod 开发、调试或深入了解游戏机制非常有用。

> [!CAUTION]
> **写给非 Wiki 编辑者：**
> 
> 该模组仅用于内部测试，功能可能不稳定，且内部的所有内容未考虑任何易用性设计，及与其他模组的兼容性设计，若自行编译使用，作者不对使用此模组或其源代码所导致的任何后果承担责任。