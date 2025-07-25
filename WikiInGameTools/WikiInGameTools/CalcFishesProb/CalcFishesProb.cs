using StardewModdingAPI.Events;
using StardewModdingAPI.Utilities;
using WikiInGameTools;
using WikiIngameTools.CalcFishesProb.Framework;
using WikiIngameTools.Framework;
using WikiInGameTools.Framework.ConfigurationService;

namespace WikiIngameTools.CalcFishesProb;

internal class CalcFishesProb : IModule
{
    /****
     ** 属性与字段
     ** Properties & Fields
     ****/
    public bool IsActive { get; private set; }
    public IConfig Config => ModEntry.Config.CalcFishesProbModConfig;

    /// <summary>
    /// 查询按钮
    /// </summary>
    private static KeybindList QueryKey { get; } = KeybindList.Parse("Q");

    /****
     ** 公有方法
     ** Public methods
     ****/
    public void Activate()
    {
        IsActive = true;
        ModEntry.ModHelper.Events.Input.ButtonsChanged += OnButtonChanged;
    }

    public void Deactivate()
    {
        IsActive = false;
        ModEntry.ModHelper.Events.Input.ButtonsChanged -= OnButtonChanged;
    }

    /****
     ** 事件处理函数
     ** Event handlers
     ****/
    /// <summary>
    /// 按下 <see cref="QueryKey"/> 按钮时，调用 <see cref="FishesProb.GetAllFishData()"/>
    /// 方法获取当前地点全部鱼类数据。
    /// </summary>
    private static void OnButtonChanged(object sender, ButtonsChangedEventArgs e)
    {
        if (QueryKey.JustPressed())
            FishesProb.GetAllFishData();
    }
}