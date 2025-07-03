using StardewModdingAPI;
using WikiInGameTools;
using WikiIngameTools.Framework;
using WikiInGameTools.Framework.ConfigurationService;
using WikiIngameTools.GetNPCGiftTastes.Framework;

namespace WikiIngameTools.GetNPCGiftTastes;

internal class GetNPCGiftTastes : IModule
{
    /****
     ** 属性与字段
     ** Properties & Fields
     ****/
    public bool IsActive { get; private set; }
    public IConfig Config => ModEntry.Config.GetNPCGiftTastesModConfig;

    public void Activate()
    {
        IsActive = true;
        ItemData.Init();
        NPCData.Init();
    }

    public void Deactivate()
    {
        IsActive = false;
        ItemData.Disposal();
        NPCData.Disposal();
    }

    /// <summary>
    /// 输出所有 NPC 对指定物品的态度，支持使用物品 ID，英文名或中文名。
    /// </summary>
    private void NPCTasteTo(string command, string[] args)
    {
        if (!IsActive)
        {
            ModEntry.Log("模块未被启用！", LogLevel.Error);
            return;
        }

        if (args.Length == 0)
        {
            ModEntry.Log("未输入物品名称！", LogLevel.Error);
            return;
        }

        var lang = args.Length > 1 && !string.IsNullOrEmpty(args[1]) ? args[1] : "en";
        var result = TastesGetter.GetAllNPCTasteToItem(args[0], lang);

        switch (result.Status)
        {
            case Status.Null:
                ModEntry.Log("未找到物品信息，请检查输入值是否有误。", LogLevel.Warn);
                return;
            case Status.Blacklisted:
                ModEntry.Log("该物品似乎是非常规物品，因此解析可能不正确。", LogLevel.Alert);
                break;
        }

        ModEntry.Log("具体信息如下：\n" + result);
    }

    /// <summary>
    /// 输出指定 NPC 对所有物品的态度，支持使用 NPC 的英文名或中文名。
    /// </summary>
    private void TastesOfNPC(string command, string[] args)
    {
        if (!IsActive)
        {
            ModEntry.Log("模块未被启用！", LogLevel.Error);
            return;
        }

        if (args.Length == 0)
        {
            ModEntry.Log("未输入 NPC 的名字！", LogLevel.Error);
            return;
        }

        var lang = args.Length > 1 && !string.IsNullOrEmpty(args[1]) ? args[1] : "en";
        var result = TastesGetter.GetNPCTasteToAllItem(args[0], lang);

        if (result.Status == Status.Null)
        {
            ModEntry.Log("未找到 NPC 信息，请检查输入值是否有误。", LogLevel.Warn);
            return;
        }

        ModEntry.Log("具体信息如下：\n" + result);
    }

    /// <summary>
    /// 获取所有 NPC 对所有物品的态度，并导出为 json。
    /// </summary>
    private void GetAll(string command, string[] args)
    {
        if (!IsActive)
        {
            ModEntry.Log("模块未被启用！", LogLevel.Error);
            return;
        }

        TastesGetter.GetAllGiftTastes();
        ModEntry.Log("已将全部结果导出至：output/AllGiftTastes.json");
    }

    public GetNPCGiftTastes()
    {
        ModEntry.ModHelper.ConsoleCommands.Add("NPC_Taste_To",
            "输出所有 NPC 对指定物品的态度，支持使用物品 ID，英文名或中文名。\n" +
            "使用示例：NPC_Taste_To 防风草\n" +
            "若物品名称错误，或给予了一个不正确的物品，会给出警告。",
            NPCTasteTo);
        
        ModEntry.ModHelper.ConsoleCommands.Add("Tastes_Of_NPC",
            "输出指定 NPC 对所有物品的态度，支持使用 NPC 的英文名或中文名。\n" +
            "使用示例：Tastes_Of_NPC 阿比盖尔\n" +
            "若 NPC 名称错误，会给出警告。",
            TastesOfNPC);

        ModEntry.ModHelper.ConsoleCommands.Add("All_Gift_Tastes",
            "获取所有 NPC 对所有物品的态度，并导出为 json。\n" +
            "使用示例：All_Gift_Tastes\n",
            GetAll);
    }
}