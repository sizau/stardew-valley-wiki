using StardewValley;

namespace WikiInGameTools.CalcFishesProb.Framework;

internal struct FishConditions
{
    public readonly string Location;
    public readonly string Season;
    public readonly string Weather;
    public readonly int Time;
    public readonly int Level;
    public readonly int Depth;

    public FishConditions(GameLocation location, string season, string weather, int time, int level, int depth)
    {
        Location = location.DisplayName;
        Season = season;
        Weather = weather;
        Time = time;
        Level = level;
        Depth = depth;
    }
}