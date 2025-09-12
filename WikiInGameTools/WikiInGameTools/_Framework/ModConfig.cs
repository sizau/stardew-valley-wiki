using System;
using WikiInGameTools.DebugModule;
using WikiInGameTools.GetItemInfo;

namespace WikiInGameTools._Framework;

[Serializable]
internal class ModConfig
{
    public CalcFishesProb.CalcFishesProbModConfig CalcFishesProbModConfig { get; set; } = new();
    public DebugModuleConfig DebugModuleConfig { get; set; } = new();
    public GetItemInfoModConfig GetItemInfoModConfig { get; set; } = new();
    public GetNPCGiftTastes.GetNPCGiftTastesModConfig GetNPCGiftTastesModConfig { get; set; } = new();
    public VariableMonitor.VariableMonitorConfig VariableMonitorConfig { get; set; } = new();
}