using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using StardewValley;
using static WikiIngameTools.GetNPCGiftTastes.Framework.ItemData;
using static WikiIngameTools.GetNPCGiftTastes.Framework.NPCData;

namespace WikiIngameTools.GetNPCGiftTastes.Framework;

internal static class TastesGetter
{
    /// <summary>
    /// 游戏内函数获取 NPC 对物品态度的返回值为 int，此数组用于将 int 转为文字。
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
    /// </summary>
    private static readonly string[] Taste2String = 
        { "Love", "", "Like", "", "Dislike", "", "Hate", "Stardrop Tea", "Neutral" };

    /// <summary>
    /// 指定某种物品，获取所有 NPC 对该物品的态度
    /// </summary>
    /// <param name="itemName">物品的 ID、英文名或当前语言环境下的显示名</param>
    /// <param name="langCode">指定显示的语言 id</param>
    /// <returns>所有 NPC 对该物品的态度</returns>
    public static string GetAllNPCTasteToItem(string itemName, string langCode)
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

        // 物品为空，返回 “null”
        if (item == null) return "null";

        var npcTaste = new GiftTastes();
        var sb = new StringBuilder();

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
        if (item.Blacklisted()) sb.AppendLine("blacklisted");
        sb.AppendLine($"|love={npcTaste.LoveThis.Tostring()}");
        sb.AppendLine($"|like={npcTaste.LikeThis.Tostring()}");
        sb.AppendLine($"|neutral={npcTaste.NeutralThis.Tostring()}");
        sb.AppendLine($"|dislike={npcTaste.DislikeThis.Tostring()}");
        sb.AppendLine($"|hate={npcTaste.HateThis.Tostring()}");

        return sb.ToString();
    }

    /// <summary>
    /// 指定某 NPC，获取其对游戏内所有物品的态度
    /// </summary>
    /// <param name="npcName">NPC 的英文名或当前语言环境下的显示名</param>
    /// <param name="langCode">指定显示的语言 id</param>
    /// <returns>该 NPC 对全部物品的态度</returns>
    public static string GetNPCTasteToAllItem(string npcName, string langCode)
    {
        if (!Enum.TryParse<LocalizedContentManager.LanguageCode>(langCode.ToLower(), out var languageCode))
        {
            languageCode = LocalizedContentManager.LanguageCode.en;
        }

        var npc = AllSocializableVillagers
            .FirstOrDefault(n => 
                string.Equals(n.Name, npcName, StringComparison.OrdinalIgnoreCase) || 
                string.Equals(n.displayName, npcName, StringComparison.OrdinalIgnoreCase));

        if (npc == null) return "null";

        var npcTaste = new GiftTastes();
        var sb = new StringBuilder();

        var originalLanguage = LocalizedContentManager.CurrentLanguageCode;
        LocalizedContentManager.CurrentLanguageCode = languageCode;
        foreach (var item in AllItems)
        {
            if (item.Blacklisted()) continue;
            var taste = npc.getGiftTasteForThisItem(item);
            npcTaste.Add(item.DisplayName, Taste2String[taste]);
        }
        LocalizedContentManager.CurrentLanguageCode = originalLanguage;

        npcTaste.Organize();
        sb.AppendLine($"love={npcTaste.LoveThis.Tostring()}");
        sb.AppendLine($"like={npcTaste.LikeThis.Tostring()}");
        sb.AppendLine($"neutral={npcTaste.NeutralThis.Tostring()}");
        sb.AppendLine($"dislike={npcTaste.DislikeThis.Tostring()}");
        sb.AppendLine($"hate={npcTaste.HateThis.Tostring()}");

        return sb.ToString();
    }

    private static string Tostring(this List<string> s)
    {
        return s == null || s.Count == 0 
            ? "" 
            : string.Join(",", s);
    }
}