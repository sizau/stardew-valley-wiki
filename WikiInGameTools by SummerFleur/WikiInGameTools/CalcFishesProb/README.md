## CalcFishesProb 模块

该模块主要用于获取当前位置下所有可能出现的鱼类列表。

### 使用方法

走到某个位置下，对着水面按 Q 键即可查询当前水域可能钓到的鱼种类。

### 注意事项

由于游戏内判断鱼类出现条件用的是一个专门的方法，因此在获取鱼类列表时，无法通过自己指定条件来获取到完整的鱼类列表，必须使用当前位置真实的季节天气信息。

例如传说之鱼在 Locations.json 中的生成条件为：

```
  "Condition": "!PLAYER_SPECIAL_ORDER_RULE_ACTIVE Current LEGENDARY_FAMILY, WEATHER Here Rain Storm GreenRain"
```

其中的 `WEATHER Here Rain Storm GreenRain` 条件要求当前的天气必须为雨天，因此通过自定义一个晴天的条件来获取鱼类列表时，传说之鱼将不会被包含在这个列表里面。

另外，当前玩家的位置会作为参数传入计算模块中，因此若玩家站在不正确的位置（例如未站在秋季鱼王和冬季鱼王的钓点），可能无法获取期望得到的鱼类列表。
