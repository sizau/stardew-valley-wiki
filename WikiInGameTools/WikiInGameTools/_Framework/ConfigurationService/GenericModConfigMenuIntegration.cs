using System;
using StardewModdingAPI;

namespace WikiInGameTools._Framework.ConfigurationService;

internal static class GenericModConfigMenuIntegration
{
    public static void Register(IManifest manifest, IModRegistry modRegistry, Action reset, Action save)
    {
        var api = IntegrationHelper.GetGenericModConfigMenu(modRegistry);
        if (api == null)
            return;

        api.Register(manifest, reset, save);

        api.AddSectionTitle(ModEntry.Manifest, () => "计算钓鱼概率模块");
        api.AddBoolOption(ModEntry.Manifest,
            () => ModEntry.Config.CalcFishesProbModConfig.Enable,
            delegate(bool value) { ModEntry.Config.CalcFishesProbModConfig.Enable = value; },
            () => "启用");
        api.AddBoolOption(ModEntry.Manifest,
            () => ModEntry.Config.CalcFishesProbModConfig.CustomWaterDepth,
            delegate(bool value) { ModEntry.Config.CalcFishesProbModConfig.CustomWaterDepth = value; },
            () => "使用自定义水深");
        api.AddNumberOption(ModEntry.Manifest,
            () => ModEntry.Config.CalcFishesProbModConfig.WaterDepth,
            delegate(int value) { ModEntry.Config.CalcFishesProbModConfig.WaterDepth = value; },
            () => "水深", null, 0, 5);

        api.AddSectionTitle(ModEntry.Manifest, () => "Debug 模块");
        api.AddBoolOption(ModEntry.Manifest,
            () => ModEntry.Config.DebugModuleConfig.Enable,
            delegate(bool value) { ModEntry.Config.DebugModuleConfig.Enable = value; },
            () => "启用");

        api.AddSectionTitle(ModEntry.Manifest, () => "获取 NPC 礼物偏好模块");
        api.AddBoolOption(ModEntry.Manifest,
            () => ModEntry.Config.GetNPCGiftTastesModConfig.Enable,
            delegate(bool value) { ModEntry.Config.GetNPCGiftTastesModConfig.Enable = value; },
            () => "启用");

        api.AddSectionTitle(ModEntry.Manifest, () => "变量监控器模块");
        api.AddBoolOption(ModEntry.Manifest,
            () => ModEntry.Config.VariableMonitorConfig.Enable,
            delegate(bool value) { ModEntry.Config.VariableMonitorConfig.Enable = value; },
            () => "启用");
    }
}