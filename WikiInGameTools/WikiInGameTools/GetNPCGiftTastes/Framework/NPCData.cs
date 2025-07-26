using System;
using System.Collections.Generic;
using StardewValley;

namespace WikiInGameTools.GetNPCGiftTastes.Framework;

/// <summary>
/// 用于获取所有可社交的 NPC 列表的静态类。
/// </summary>
internal static class NPCData
{
    /// <summary>
    /// 所有可社交的 NPC 的列表，未使用时应当及时释放。
    /// </summary>
    public static IEnumerable<NPC> AllSocializableVillagers { get; private set; }

    /// <summary>
    /// 从 Data/Characters 处读取并筛选出所有可社交的 NPC。
    /// </summary>
    /// <remarks>
    /// 以下两种 NPC 将被排除
    /// <list type="table">
    ///   <item>(a) 不包含 Character 数据</item>
    ///   <item>(b) CanSocialize 属性为 "FALSE".</item>
    /// </list>
    /// </remarks>
    public static void Init()
    {
        var characterNames = Game1.characterData.Keys;
        var possiblySocializableVillagers = new List<NPC>();

        // 暂时解锁未认识的 NPC，例如雷欧、肯特
        foreach (var characterName in characterNames)
        {
            if (!NPC.TryGetData(characterName, out var data) || data == null) continue;

            if (data.CanSocialize != null &&
                string.Equals(data.CanSocialize.Trim(), "FALSE", StringComparison.OrdinalIgnoreCase))
                continue;

            // DO NOT delete the conditional statements above and use try-catch here;
            // For exceptions here cannot be catched correctly.
            Game1.AddCharacterIfNecessary(characterName, true);
        }

        // 将可社交的 NPC 置入列表中
        foreach (var characterName in characterNames)
        {
            if (!NPC.TryGetData(characterName, out var data)) continue;

            if (data.CanSocialize != null &&
                string.Equals(data.CanSocialize.Trim(), "FALSE", StringComparison.OrdinalIgnoreCase))
                continue;

            possiblySocializableVillagers.Add(Game1.getCharacterFromName(characterName));
        }

        AllSocializableVillagers = possiblySocializableVillagers;
    }

    /// <summary>
    /// 释放 NPC 数据。
    /// </summary>
    public static void Disposal()
    {
        AllSocializableVillagers = null;
    }
}