﻿using StardewValley;
using StardewValley.GameData.Locations;

namespace WikiInGameTools.CalcFishesProb.Framework;

internal static class FishUtilities
{
    public static string GetFishName(this SpawnFishData spawn)
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

    public static Item GetFish(this SpawnFishData spawn)
    {
        var id = spawn.Id;
        return ItemRegistry.Create(id);
    }
}