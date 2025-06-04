using JetBrains.Annotations; 
using StardewModdingAPI;
using StardewModdingAPI.Events;

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
    public static IManifest Manifest { get; private set; }
    public static IModHelper ModHelper { get; private set; }
    private static IMonitor ModMonitor { get; set; }
    public static void Log(string s, LogLevel l = LogLevel.Debug) => ModMonitor.Log(s, l);
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
    }
    
    /****
     ** 事件处理函数
     ** Event handlers
     ****/
    #region Event handlers
    /// <summary>
    /// 游戏存档载入事件。
    /// </summary>
    private static void OnGameLoaded(object sender, SaveLoadedEventArgs e) { }

    /// <summary>
    /// 游戏存档退出事件。
    /// </summary>
    private static void OnGameUnload(object sender, ReturnedToTitleEventArgs e) { }

    /// <summary>
    /// 游戏启动事件
    /// </summary>
    private static void OnGameLaunched(object sender, GameLaunchedEventArgs e) { }

    /// <summary>
    /// 游戏菜单变化事件。
    /// </summary>
    private static void OnMenuChanged(object sender, MenuChangedEventArgs e) { }

    /// <summary>
    /// 按下按键事件。
    /// </summary>
    private static void OnButtonChanged(object sender, ButtonsChangedEventArgs e) { }
    #endregion
}