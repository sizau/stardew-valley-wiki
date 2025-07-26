using WikiInGameTools._Framework.ConfigurationService;

namespace WikiInGameTools.CalcFishesProb;

internal class CalcFishesProbModConfig : IConfig
{
    public bool Enable { get; set; }
    public bool CustomWaterDepth { get; set; }
    public int WaterDepth { get; set; } = 5;
}