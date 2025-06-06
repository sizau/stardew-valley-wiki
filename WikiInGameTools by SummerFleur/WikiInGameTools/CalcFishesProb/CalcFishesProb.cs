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
    public static CalcFishesProbModConfig CfpConfig { get; set; }
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
            () => "Enable");
        Api.AddBoolOption(ModEntry.Manifest, 
            () => ModEntry.Config.CalcFishesProbModConfig.CustomWaterDepth, 
            delegate(bool value) { ModEntry.Config.CalcFishesProbModConfig.CustomWaterDepth = value; }, 
            () => "Enable Custom Water Depth?");
        Api.AddNumberOption(ModEntry.Manifest, 
            () => ModEntry.Config.CalcFishesProbModConfig.WaterDepth, 
            delegate(int value) { ModEntry.Config.CalcFishesProbModConfig.WaterDepth = value; }, 
            () => "Water Depth", null, 0, 5);
    }
    
    public static void ReloadConfig()
        => CfpConfig = ModEntry.Config.CalcFishesProbModConfig;
}

