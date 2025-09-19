using System.Collections.Generic;
using System.Linq;
using StardewValley;

namespace WikiInGameTools.getItemInfo.Framework;

public struct ItemInfo
{
    public readonly string QualifiedItemID;
    public readonly string Name;
    public readonly string DisplayName;
    public readonly string Description;
    public readonly List<string> Tags = new();

    public ItemInfo(Item item)
    {
        
        QualifiedItemID = item.QualifiedItemId;
        Name = item.Name;
        DisplayName = item.DisplayName;
        Description = ItemRegistry.GetDataOrErrorItem(item.QualifiedItemId).Description;
        Tags = item.GetContextTags().ToList();
    }
}