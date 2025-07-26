using System;
using WikiInGameTools.DebugModule;

namespace WikiInGameTools._Framework;

[Serializable]
internal class ModConfig
{
    public CalcFishesProb.CalcFishesProbModConfig CalcFishesProbModConfig { get; set; } = new();
    public DebugModuleConfig DebugModuleConfig { get; set; } = new();
    public GetNPCGiftTastes.GetNPCGiftTastesModConfig GetNPCGiftTastesModConfig { get; set; } = new();
    public VariableMonitor.VariableMonitorConfig VariableMonitorConfig { get; set; } = new();
}