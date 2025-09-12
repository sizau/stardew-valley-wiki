using StardewValley;

namespace WikiInGameTools.getItemInfo.Framework;

public struct ItemInfo
{
    public readonly string QualifiedItemID;
    public readonly string Name;
    public readonly string DisplayName;
    public readonly string Description;

    public ItemInfo(Item item)
    {
        
        QualifiedItemID = item.QualifiedItemId;
        Name = item.Name;
        DisplayName = item.DisplayName;
        Description = ItemRegistry.GetDataOrErrorItem(item.QualifiedItemId).Description;
    }
}