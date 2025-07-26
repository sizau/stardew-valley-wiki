using System.Collections.Generic;
using System.Linq;
using StardewValley;
using StardewValley.Objects.Trinkets;

namespace WikiInGameTools.GetNPCGiftTastes.Framework;

/// <summary>
/// 用于获取所有可以作为礼物送出的物品列表的静态类。
/// </summary>
internal static class ItemData
{
    /// <summary>
    /// 所有可以作为礼物送出的物品列表，未使用时应当及时释放。
    /// </summary>
    public static IEnumerable<Item> AllItems { get; private set; }

    /// <summary>
    /// 所有不能作为礼物送出的物品列表，用于提示用户输入了错误值，未使用时应当及时释放。
    /// </summary>
    public static IEnumerable<Item> BlackListedItems { get; private set; }

    /// <summary>
    /// 使用 <see cref="ItemRegistry"/> 获取游戏内所有可以作为礼物送出的物品列表。
    /// </summary>
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

        // AllItems = allObjects
        //     .Concat(allTrinkets)
        //     .ToList();
        
        var all = allObjects
            .Concat(allTrinkets)
            .ToList();
        
        AllItems = all.Where(o => !o.Blacklisted());
        BlackListedItems = all.Where(o => o.Blacklisted());
    }

    /// <summary>
    /// 释放物品数据。
    /// </summary>
    public static void Disposal()
    {
        AllItems = null;
        BlackListedItems = null;
    }
}