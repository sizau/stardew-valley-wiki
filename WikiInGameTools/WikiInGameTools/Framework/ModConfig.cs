using System;
using WikiIngameTools.DebugModule;

namespace WikiIngameTools.Framework;

[Serializable]
internal class ModConfig
{
    public CalcFishesProb.CalcFishesProbModConfig CalcFishesProbModConfig { get; set; } = new();
    public DebugModuleConfig DebugModuleConfig { get; set; } = new();
    public GetNPCGiftTastes.GetNPCGiftTastesModConfig GetNPCGiftTastesModConfig { get; set; } = new();
    public VariableMonitor.VariableMonitorConfig VariableMonitorConfig { get; set; } = new();
}