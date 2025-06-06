using StardewValley;
using StardewValley.GameData.Locations;

namespace WikiIngameTools.CalcFishesProb.Framework;

internal static class FishUtilities
{
    public static string GetFishName(SpawnFishData spawn)
    {
        var id = spawn.Id;
        switch (id)
        {
            case "SECRET_NOTE_OR_ITEM":
                return "秘密纸条";
            
            case "(O)167|(O)168|(O)169|(O)170|(O)171|(O)172":
                return "六种垃圾";
            
            default:
                var item = GetFish(spawn);
                return item == null ? "" : item.DisplayName;
        }
    }

    public static Item GetFish(SpawnFishData spawn)
    {
        var id = spawn.Id;
        return ItemRegistry.Create(id);
    }
}