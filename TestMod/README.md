部署事项

- 千万记得在 TestMod.csproj 里面修改<GamePath>，不然会报很多错误，示例：<GamePath>F:\SteamLibrary\steamapps\common\Stardew Valley</GamePath>
- 理论上应该不用 NuGet 重新安装 PathosChild.Stardew.ModBuildConfig，但是如果打开项目就报一堆红大概率就是没安装这个的原因

简介：

测试用 mod，可以在这个 mod 里添加各种对原版调试用的代码（增加补丁类记得在 ModEntry 里注册）

变量监控器（VariableMonitor）使用方法参考 CONFIG_GUIDE.md

未来画饼：加入在 config.json 中直接开关对应补丁的配置项，对调试补丁进行分类
