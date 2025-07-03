using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using StardewModdingAPI;
using StardewValley;
using WikiInGameTools;
using static WikiIngameTools.GetNPCGiftTastes.Framework.ItemData;
using static WikiIngameTools.GetNPCGiftTastes.Framework.NPCData;

namespace WikiIngameTools.GetNPCGiftTastes.Framework;

/// <summary>
/// 用于获取礼物偏好的静态类。
/// </summary>
internal static class TastesGetter
{
    /// <summary>
    /// 游戏内函数获取 NPC 对物品态度的返回值为 int，此数组用于将 int 转为文字。
    /// </summary>
    /// <value>
    /// <list type="table">
    ///   <item>0 = 最爱 Love</item>
    ///   <item>2 = 喜欢 Like</item>
    ///   <item>4 = 不喜欢 Dislike</item>
    ///   <item>6 = 讨厌 Hate</item>
    ///   <item>7 = 星之果茶 Stardrop Tea</item>
    ///   <item>8 = 中立 Neutral</item>
    /// </list>
    /// </value>
    private static readonly string[] Taste2String =
        { "Love", "", "Like", "", "Dislike", "", "Hate", "Stardrop Tea", "Neutral" };

    /// <summary>
    /// 指定某种物品，获取所有 NPC 对该物品的态度。
    /// </summary>
    /// <param name="itemName">物品的 ID、英文名或当前语言环境下的显示名</param>
    /// <param name="langCode">指定显示的语言 id</param>
    /// <returns>所有 NPC 对该物品的态度</returns>
    public static GiftTastes GetAllNPCTasteToItem(string itemName, string langCode)
    {
        // 获取输出的语言
        if (!Enum.TryParse<LocalizedContentManager.LanguageCode>(langCode.ToLower(), out var languageCode))
        {
            languageCode = LocalizedContentManager.LanguageCode.en;
        }

        // 从 itemName 获取物品实例
        var item = AllItems
            .FirstOrDefault(o =>
                o.QualifiedItemId == itemName ||
                string.Equals(o.Name, itemName, StringComparison.OrdinalIgnoreCase) ||
                string.Equals(o.DisplayName, itemName, StringComparison.OrdinalIgnoreCase));

        var npcTaste = new GiftTastes(Status.Normal);
        // 物品为空，返回 Null；物品不可获取或不正常，返回 Blacklisted
        if (item == null)
        {
            item = BlackListedItems
                .FirstOrDefault(o =>
                    o.QualifiedItemId == itemName ||
                    string.Equals(o.Name, itemName, StringComparison.OrdinalIgnoreCase) ||
                    string.Equals(o.DisplayName, itemName, StringComparison.OrdinalIgnoreCase));
            if (item == null) return new GiftTastes(Status.Null);
            npcTaste.Status = Status.Blacklisted;
        }

        // 暂时将语言切为所选语言，然后获取偏好
        var originalLanguage = LocalizedContentManager.CurrentLanguageCode;
        LocalizedContentManager.CurrentLanguageCode = languageCode;
        foreach (var npc in AllSocializableVillagers)
        {
            var taste = npc.getGiftTasteForThisItem(item);
            npcTaste.Add(npc.displayName, Taste2String[taste]);
        }
        LocalizedContentManager.CurrentLanguageCode = originalLanguage;

        // 写入并返回偏好
        npcTaste.Organize();
        return npcTaste;
    }

    /// <summary>
    /// 指定某 NPC，获取其对游戏内所有物品的态度。
    /// </summary>
    /// <param name="npcName">NPC 的英文名或当前语言环境下的显示名</param>
    /// <param name="langCode">指定显示的语言 id</param>
    /// <returns>该 NPC 对全部物品的态度</returns>
    public static GiftTastes GetNPCTasteToAllItem(string npcName, string langCode)
    {
        // 获取输出的语言
        if (!Enum.TryParse<LocalizedContentManager.LanguageCode>(langCode.ToLower(), out var languageCode))
            languageCode = LocalizedContentManager.LanguageCode.en;

        // 从 npcName 获取 NPC 实例
        var npc = AllSocializableVillagers
            .FirstOrDefault(n =>
                string.Equals(n.Name, npcName, StringComparison.OrdinalIgnoreCase) ||
                string.Equals(n.displayName, npcName, StringComparison.OrdinalIgnoreCase));

        // npc 为空，返回 Null
        if (npc == null) return new GiftTastes(Status.Null);

        var npcTaste = new GiftTastes(Status.Normal);

        // 暂时将语言切为所选语言，然后获取偏好
        var originalLanguage = LocalizedContentManager.CurrentLanguageCode;
        LocalizedContentManager.CurrentLanguageCode = languageCode;
        foreach (var item in AllItems)
        {
            var taste = npc.getGiftTasteForThisItem(item);
            npcTaste.Add(item.DisplayName, Taste2String[taste]);
        }
        LocalizedContentManager.CurrentLanguageCode = originalLanguage;

        // 写入并返回偏好
        npcTaste.Organize();
        return npcTaste;
    }

    /// <summary>
    /// 获取获取所有 NPC 对游戏内所有物品的态度。
    /// </summary>
    /// <returns>全部的 NPC 对全部物品的态度</returns>
    public static void GetAllGiftTastes()
    {

        // 新建数组存储全部的礼物偏好
        var allGiftTastes = new Dictionary<string, GiftTastes>();

        // 遍历全部物品与npc，获取偏好
        foreach (var item in AllItems)
        {
            var npcTaste = new GiftTastes(Status.Normal);
            foreach (var npc in AllSocializableVillagers)
            {
                var taste = npc.getGiftTasteForThisItem(item);
                npcTaste.Add(npc.displayName, Taste2String[taste]);
            }
            npcTaste.Organize();

            var displayName = item.ItemId switch
            {
                "126" => "诡异玩偶（绿）",
                "127" => "诡异玩偶（黄）",
                "SpecificBait" => "针对性鱼饵",
                "Smoked" => "熏鱼",
                "DriedFruit" => "果干",
                "DriedMushrooms" => "蘑菇干",
                _ => item.DisplayName
            };

            if (!allGiftTastes.TryAdd(displayName, npcTaste))
                ModEntry.Log($"键冲突：Key={displayName}，ID={item.ItemId}。", LogLevel.Warn);
        }

        // 返回全部礼物偏好
        ConvertToJson(allGiftTastes);
    }

    private static void ConvertToJson(Dictionary<string, GiftTastes> tastes)
    {
        var savePath = Path.Combine("output", "AllGiftTastes.json");
        var absolutePath = Path.Combine(ModEntry.ModHelper.DirectoryPath, savePath);

        try
        {
            ModEntry.ModHelper.Data.WriteJsonFile(savePath, tastes);
        }
        catch (Exception ex)
        {
            ModEntry.Log($"无法导出数据至 {absolutePath}");
            ModEntry.Log(ex.ToString());
        }
    }
}