namespace WikiIngameTools.Framework;

internal class ModConfig
{
    public CalcFishesProb.CalcFishesProbModConfig CalcFishesProbModConfig { get; set; } = new();
    public GetNPCGiftTastes.GetNPCGiftTastesModConfig GetNPCGiftTastesModConfig { get; set; } = new();
}