﻿using System.Collections.Generic;
using StardewValley;

namespace WikiIngameTools.GetNPCGiftTastes.Framework;

internal static class ItemBlackList
{
    /// <summary>
    /// Check whether a given item is blacklisted.
    /// </summary>
    /// <returns>Whether the item is blacklisted.</returns>
    /// <param name="item">Item to check.</param>
    public static bool Blacklisted(this Item item) => BlacklistedItemIDs.Contains(item.QualifiedItemId);
    
    private static readonly HashSet<string> BlacklistedItemIDs = new()
    {
        // stones
        "(O)2",
        "(O)4",
        "(O)6",
        "(O)8",
        "(O)10",
        "(O)12",
        "(O)14",
        "(O)25",
        "(O)32",
        "(O)34",
        "(O)36",
        "(O)38",
        "(O)40",
        "(O)42",
        "(O)44",
        "(O)46",
        "(O)48",
        "(O)50",
        "(O)52",
        "(O)54",
        "(O)56",
        "(O)58",
        "(O)75",
        "(O)76",
        "(O)77",
        "(O)95",
        "(O)290",
        "(O)343",
        "(O)450",
        "(O)668",
        "(O)670",
        "(O)751",
        "(O)760",
        "(O)762",
        "(O)764",
        "(O)765",
        "(O)816",
        "(O)817",
        "(O)818",
        "(O)819",
        "(O)843",
        "(O)844",
        "(O)845",
        "(O)846",
        "(O)847",
        "(O)849",
        "(O)850",
        "(O)BasicCoalNode0",
        "(O)BasicCoalNode1",
        "(O)CalicoEggStone_0",
        "(O)CalicoEggStone_1",
        "(O)CalicoEggStone_2",
        "(O)PotOfGold",
        "(O)VolcanoGoldNode",
        "(O)VolcanoCoalNode0",
        "(O)VolcanoCoalNode1",

        // weeds
        "(O)0",
        "(O)313",
        "(O)314",
        "(O)315",
        "(O)316",
        "(O)317",
        "(O)318",
        "(O)319",
        "(O)320",
        "(O)321",
        "(O)452",
        "(O)674",
        "(O)675",
        "(O)676",
        "(O)677",
        "(O)678",
        "(O)679",
        "(O)750",
        "(O)784",
        "(O)785",
        "(O)786",
        "(O)792",
        "(O)793",
        "(O)794",
        "(O)882",
        "(O)883",
        "(O)884",
        "(O)GreenRainWeeds0",
        "(O)GreenRainWeeds1",
        "(O)GreenRainWeeds2",
        "(O)GreenRainWeeds3",
        "(O)GreenRainWeeds4",
        "(O)GreenRainWeeds5",
        "(O)GreenRainWeeds6",
        "(O)GreenRainWeeds7",

        // twigs
        "(O)294",
        "(O)295",

        // quest items
        "(O)71", // Trimmed Lucky Purple Shorts
        "(O)191", // Ornate Necklace
        "(O)742", // Haley's Lost Bracelet
        "(O)788", // Lost Axe
        "(O)790", // Berry Basket
        "(O)864", // War Memento
        "(O)865", // Gourmet Tomato Salt
        "(O)866", // Stardew Valley Rose
        "(O)867", // Advanced TV Remote
        "(O)868", // Arctic Shard
        "(O)869", // Wriggling Worm
        "(O)870", // Pirate's Locket
        "(O)875", // Ectoplasm
        "(O)876", // Prismatic Jelly
        "(O)897", // Pierre's Missing Stocklist
        "(O)GoldenBobber",

        // unstorable items (used on pickup)
        "(O)73", // Golden Walnut
        "(O)434", // Stardrop
        "(O)803", // Iridium Milk
        "(O)858", // Qi Gem
        "(O)930", // Red Heart
        "(O)GoldCoin", // Gold Coin

        // supply crates
        "(O)922",
        "(O)923",
        "(O)924",
        "(O)925", // Slime Crate

        // why u want categorize them???
        "(O)460",
        "(O)808",

        // unobtainable
        "(O)30", // Lumber
        "(O)94", // Spirit Torch
        "(O)102", // Lost Book
        "(O)449", // Stone Base
        "(O)461", // Decorative Pot
        "(O)528", // Jukebox Ring
        "(O)590", // Artifact Spot
        "(O)892", // Warp Totem: Qi's Arena
        "(O)927", // Camping Stove
        "(O)929", // Hedge
        
        "(T)Lantern",
        "(O)SeedSpot"
    };
}