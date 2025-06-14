using System.Collections.Generic;
using System.Linq;
using StardewValley;
using StardewValley.Objects.Trinkets;

namespace WikiIngameTools.GetNPCGiftTastes.Framework;

internal static class ItemData
{
    public static IEnumerable<Item> AllItems { get; private set; }
    
    public static void Init()
    {
        var allObjects = ItemRegistry
            .GetTypeDefinition("(O)")
            .GetAllIds()
            .Select(id => new Object(id, 1));
        
        var allTrinkets = ItemRegistry
            .GetTypeDefinition("(TR)")
            .GetAllIds()
            .Select(id => new Trinket(id, 1));

        AllItems = allObjects
            .Concat(allTrinkets)
            .ToList();
    }

    public static void Disposal()
    {
        AllItems = null;
    }
}