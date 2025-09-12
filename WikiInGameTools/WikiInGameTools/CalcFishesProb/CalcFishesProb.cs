using System.Collections.Generic;
using System.IO;
using System.Linq;
using StardewModdingAPI;
using StardewModdingAPI.Events;
using StardewModdingAPI.Utilities;
using StardewValley;
using StardewValley.GameData.Locations;
using WikiInGameTools._Framework;
using WikiInGameTools._Framework.ConfigurationService;
using WikiInGameTools.CalcFishesProb.Framework;

namespace WikiInGameTools.CalcFishesProb;

internal class CalcFishesProb : IModule
{
    /****
     ** 属性与字段
     ** Properties & Fields
     ****/
    public bool IsActive { get; private set; }
    public IConfig Config => ModEntry.Config.CalcFishesProbModConfig;

    /// <summary>
    /// 查询按钮
    /// </summary>
    private static KeybindList QueryKey { get; } = KeybindList.Parse("Q");

    /****
     ** 公有方法
     ** Public methods
     ****/
    public void Activate()
    {
        IsActive = true;
        ModEntry.ModHelper.Events.Input.ButtonsChanged += OnButtonChanged;
    }

    public void Deactivate()
    {
        IsActive = false;
        ModEntry.ModHelper.Events.Input.ButtonsChanged -= OnButtonChanged;
    }

    /****
     ** 事件处理函数
     ** Event handlers
     ****/
    /// <summary>
    /// 按下 <see cref="QueryKey"/> 按钮时，调用 <see cref="FishesProb.GetAllFishData()"/>
    /// 方法获取当前地点全部鱼类数据。
    /// </summary>
    private static void OnButtonChanged(object sender, ButtonsChangedEventArgs e)
    {
        if (QueryKey.JustPressed())
            FishesProb.GetAllFishData();
    }

    private void GetAllPossibleFishFromLocationData(string command, string[] args)
    {
        if (!IsActive)
        {
            ModEntry.Log("模块未被启用！", LogLevel.Error);
            return;
        }

        var locationsFishData = new Dictionary<string, List<string>>();

        foreach (var location in Game1.locations)
        {
            var locationData = location.GetData();
            if (locationData is { Fish.Count: 0} ) continue;
            
            var spawnFishData = new List<SpawnFishData>()
                .Concat(locationData.Fish)
                .Select(f => f.ItemId)
                .ToList();
            
            locationsFishData.Add(location.DisplayName, spawnFishData);
        }

        var savePath = Path.Combine("output", "Fishes.json");
        ModEntry.ModHelper.Data.WriteJsonFile(savePath, locationsFishData);
        ModEntry.Log("已输出全部鱼类地点数据！");
    }

    public CalcFishesProb()
    {
        ModEntry.ModHelper.ConsoleCommands.Add("Get_All_Location_Fish",
            "输出所有地点下的鱼类数据。",
            GetAllPossibleFishFromLocationData);
    }
}