using System.Collections.Generic;
using System.IO;
using System.Linq;
using StardewModdingAPI;
using StardewValley;
using StardewValley.Extensions;
using WikiInGameTools._Framework;
using WikiInGameTools._Framework.ConfigurationService;
using WikiInGameTools.getItemInfo.Framework;

namespace WikiInGameTools.GetItemInfo;

internal class GetItemInfo : IModule 
{
    public bool IsActive { get; private set; }
    private List<ItemInfo> ItemInfos { get; set; }

    public IConfig Config => ModEntry.Config.GetItemInfoModConfig;

    public void Activate()
    {
        IsActive = true;
        ItemInfos = ItemRegistry.ItemTypes
            .SelectMany(r => r.GetAllData().Select(r.CreateItem))
            .Select(i => new ItemInfo(i))
            .ToList();
    }

    public void Deactivate()
    {
        IsActive = false;
        ItemInfos = null;
    }

    private void SerializeAll(string command, string[] args)
    {
        if (!IsActive)
        {
            ModEntry.Log("模块未被启用！", LogLevel.Error);
            return;
        }

        var dictId2Desc = ItemInfos
            .Where(i => i.QualifiedItemID.StartsWith("(O)"))
            .DistinctBy(i => i.QualifiedItemID[3..])
            .ToDictionary(i => i.QualifiedItemID[3..], i => i.Description);

        var dictEn2Desc = ItemInfos
            .DistinctBy(i => i.Name)
            .ToDictionary(i => i.Name, i => i.Description);

        var dictZh2Desc = ItemInfos
            .DistinctBy(i => i.DisplayName)
            .ToDictionary(i => i.DisplayName, i => i.QualifiedItemID);

        var dictEn2Name = ItemInfos
            .DistinctBy(i => i.Name)
            .ToDictionary(i => i.Name, i => i.DisplayName);

        var dictId2Tags = ItemInfos
            .ToDictionary(i => i.QualifiedItemID, i => i.Tags.Where(t => !t.StartsWith("id_")));

        ModEntry.ModHelper.Data.WriteJsonFile(Path.Combine("output", "dictId2Desc.json"), dictId2Desc);
        ModEntry.ModHelper.Data.WriteJsonFile(Path.Combine("output", "dictEn2Desc.json"), dictEn2Desc);
        ModEntry.ModHelper.Data.WriteJsonFile(Path.Combine("output", "dictZh2Desc.json"), dictZh2Desc);
        ModEntry.ModHelper.Data.WriteJsonFile(Path.Combine("output", "dictEn2Name.json"), dictEn2Name);
        ModEntry.ModHelper.Data.WriteJsonFile(Path.Combine("output", "dictId2Tags.json"), dictId2Tags);
    }

    public GetItemInfo()
    {
        ModEntry.ModHelper.ConsoleCommands.Add("Get_All_Item_Info",
            "输出所有物品相关数据。", SerializeAll);
    }
}