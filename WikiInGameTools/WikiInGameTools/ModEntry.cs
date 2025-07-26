using JetBrains.Annotations;
using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewValley;
using WikiIngameTools.CalcFishesProb;
using WikiIngameTools.DebugModule;
using WikiIngameTools.Framework;
using WikiInGameTools.Framework.ConfigurationService;
using WikiIngameTools.GetNPCGiftTastes;
using WikiIngameTools.VariableMonitor;

namespace WikiInGameTools;

/// <summary>
/// The mod entry class loaded by SMAPI.
/// </summary>
[UsedImplicitly]
internal class ModEntry : Mod
{
    /****
     ** 属性
     ** Properties
     ****/
    #region Properties
    public static ModConfig Config { get; private set; }
    public static IManifest Manifest { get; private set; }
    public static IModHelper ModHelper { get; private set; }
    private static IMonitor ModMonitor { get; set; }
    public static void Log(string s, LogLevel l = LogLevel.Debug) => ModMonitor.Log(s, l);
    #endregion

    /****
     ** 模块
     ** Modules
     ****/
    #region Modules
    private static CalcFishesProb CalcFishesProb { get; set; }
    private static DebugModule DebugModule { get; set; }
    private static GetNPCGiftTastes GetNPCGiftTastes { get; set; }
    private static VariableMonitor VariableMonitor { get; set; }
    #endregion
    
    /// <summary>
    /// 模组入口点，在模组首次加载后调用。
    /// </summary>
    public override void Entry(IModHelper helper)
    {
        Manifest = ModManifest;
        ModMonitor = Monitor;
        ModHelper = Helper;

        helper.Events.GameLoop.GameLaunched += OnGameLaunched;
        helper.Events.GameLoop.ReturnedToTitle += OnGameUnload;
        helper.Events.GameLoop.SaveLoaded += OnGameLoaded;
        helper.Events.Display.MenuChanged += OnMenuChanged;
        helper.Events.Input.ButtonsChanged += OnButtonChanged;

        Config = helper.ReadConfig<ModConfig>();
    }
    
    /****
     ** 事件处理函数
     ** Event handlers
     ****/
    #region Event handlers

    /// <summary>
    /// 游戏存档载入事件。
    /// </summary>
    private static void OnGameLoaded(object sender, SaveLoadedEventArgs e)
    {
        CalcFishesProb = new CalcFishesProb();
        if (Config.CalcFishesProbModConfig.Enable)
            CalcFishesProb.Activate();

        DebugModule = new DebugModule();
        if (Config.DebugModuleConfig.Enable)
            DebugModule.Activate();

        VariableMonitor = new VariableMonitor();
        if (Config.VariableMonitorConfig.Enable)
            VariableMonitor.Activate();

        // 语句 GetNPCGiftTastes = new GetNPCGiftTastes();
        // 需要在 OnGameLaunched 中执行
        if (Config.GetNPCGiftTastesModConfig.Enable)
            GetNPCGiftTastes.Activate();
    }

    /// <summary>
    /// 游戏存档退出事件。
    /// </summary>
    private static void OnGameUnload(object sender, ReturnedToTitleEventArgs e)
    {
        CalcFishesProb.Deactivate();
        CalcFishesProb = null;

        DebugModule.Deactivate();
        DebugModule = null;

        VariableMonitor.Deactivate();
        VariableMonitor = null;

        GetNPCGiftTastes.Deactivate();
    }

    /// <summary>
    /// 游戏启动事件
    /// </summary>
    private static void OnGameLaunched(object sender, GameLaunchedEventArgs e)
    {
        GenericModConfigMenuIntegration.Register(Manifest, ModHelper.ModRegistry,
            () => Config = new ModConfig(),
            ReloadConfig
        );

        GetNPCGiftTastes = new GetNPCGiftTastes();
    }

    /// <summary>
    /// 游戏菜单变化事件。
    /// </summary>
    private static void OnMenuChanged(object sender, MenuChangedEventArgs e) { }

    /// <summary>
    /// 按下按键事件。
    /// </summary>
    private static void OnButtonChanged(object sender, ButtonsChangedEventArgs e) { }
    #endregion

    /****
     ** 私有方法
     ** Private Methods
     ****/
    #region Private Methods
    /// <summary>
    /// 读取模组配置更新并重新载入配置。
    /// </summary>
    private static void ReloadConfig()
    {
        ModHelper.WriteConfig(Config);
        Config = ModHelper.ReadConfig<ModConfig>();
        GetNPCGiftTastes.Reload();

        if (!Game1.hasLoadedGame) return;

        CalcFishesProb.Reload();
        DebugModule.Reload();
        VariableMonitor.Reload();
    }
    #endregion
}