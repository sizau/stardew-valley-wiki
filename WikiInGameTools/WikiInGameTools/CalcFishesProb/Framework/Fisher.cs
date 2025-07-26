namespace WikiInGameTools.CalcFishesProb.Framework;

internal class Fisher
{
    public int FishingLevel { get; }
    public int LuckLevel { get; }
    public float DailyLuck { get; }

    public Fisher(int fishingLevel, int luckLevel=0, float dailyLuck=0)
    {
        FishingLevel = fishingLevel;
        LuckLevel = luckLevel;
        DailyLuck = dailyLuck;
    }
}