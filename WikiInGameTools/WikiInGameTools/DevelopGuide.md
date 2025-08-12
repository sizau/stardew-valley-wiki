## 拓展指南

本工具主要采用模块式设计，因此在拓展模块时，请先新建一个新目录用于存放新的模块，然后按照以下步骤操作：

- [ ] 新建模块主类 `NewModule.cs`，实现 [`IModule`](_Framework/IModule.cs)，同时设置 `IsActive` 的 `setter` 和 `Config` 的 `getter` 如下所示
    ```csharp
    // NewModule.cs
    internal class NewModule : IModule 
    {
        public bool IsActive { get; private set; }
        
        public IConfig Config => ModEntry.Config.NewModuleConfig;
        
        public void Activate()
        {
            IsActive = true;
            // 模块注册时该做什么
        }
        
        public void Deactivate()
        {
            IsActive = false;
            // 模块注销时该做什么
        }
    }
    ```
- [ ] 新建 `NewModuleConfig.cs`, 实现 [`IConfig`](_Framework/ConfigurationService/IConfig.cs)，然后在 `ModConfig` 中注册 `NewModuleConfig`
    ```csharp
    // NewModuleConfig.cs
    internal class NewModuleConfig : IConfig { }
    ```
    ```csharp
    // ModConfig.cs
    public NewModuleConfig NewModuleConfig { get; set; } = new();
    ```
- [ ] 在 `ModEntry` 中注册新模块，然后在合适的时间点调用 `Activate()` 和 `Deactivate()`
- [ ] 在 [`GenericModConfigMenuIntegration`](_Framework/ConfigurationService/GenericModConfigMenuIntegration.cs) 中添加新模块的配置项，然后回到 `ModEntry` 中，在最下方的 `Reload()` 方法中添加 `NewModule.Reload()`

### 提示
- 在 `ModEntry` 中提供了一个静态的 `Log`，可以在模块中直接使用 `ModEntry.Log(message)` 来输出日志，默认 `LogLevel` 为 `Debug`
- 若使用 `Harmony`，切记要在对应模块中自定义一个 `UniqueID` 来创建一个 `Harmony` 实例，否则可能会导致其他模块的 `Harmony` 冲突，建议为：
    ```csharp
    // NewModule.cs
    private readonly Harmony _harmony = new (ModEntry.Manifest.UniqueID + ".NewModule");
    ```
