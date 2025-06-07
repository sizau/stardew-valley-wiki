using StardewModdingAPI.Events;
using StardewModdingAPI.Utilities;
using WikiInGameTools;
using WikiIngameTools.CalcFishesProb.Framework;
using WikiIngameTools.Framework;
using static WikiInGameTools.Framework.ConfigurationService.GenericModConfigMenuIntegration;

namespace WikiIngameTools.CalcFishesProb;

internal class CalcFishesProb : IModule
{
    /****
     ** 属性与字段
     ** Properties & Fields
     ****/
    public bool IsActive { get; private set; }
    
    /// <summary>
    /// 模块配置
    /// </summary>
    public static CalcFishesProbModConfig CfpConfig { get; set; }
    
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
    
    public static void ReloadConfig() => CfpConfig = ModEntry.Config.CalcFishesProbModConfig;
    
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

    public CalcFishesProb()
    {
        CfpConfig = ModEntry.Config.CalcFishesProbModConfig;

        Api.AddSectionTitle(ModEntry.Manifest, () => "计算钓鱼概率模块");
        Api.AddBoolOption(ModEntry.Manifest, 
            () => ModEntry.Config.CalcFishesProbModConfig.Enable, 
            delegate(bool value) { ModEntry.Config.CalcFishesProbModConfig.Enable = value; }, 
            () => "启用");
        Api.AddBoolOption(ModEntry.Manifest, 
            () => ModEntry.Config.CalcFishesProbModConfig.CustomWaterDepth, 
            delegate(bool value) { ModEntry.Config.CalcFishesProbModConfig.CustomWaterDepth = value; }, 
            () => "使用自定义水深");
        Api.AddNumberOption(ModEntry.Manifest, 
            () => ModEntry.Config.CalcFishesProbModConfig.WaterDepth, 
            delegate(int value) { ModEntry.Config.CalcFishesProbModConfig.WaterDepth = value; }, 
            () => "水深", null, 0, 5);
    }
}

