using System;

namespace WikiIngameTools.Framework;

[Serializable]
internal class ModConfig
{
    public CalcFishesProb.CalcFishesProbModConfig CalcFishesProbModConfig { get; set; } = new();
    public GetNPCGiftTastes.GetNPCGiftTastesModConfig GetNPCGiftTastesModConfig { get; set; } = new();
}