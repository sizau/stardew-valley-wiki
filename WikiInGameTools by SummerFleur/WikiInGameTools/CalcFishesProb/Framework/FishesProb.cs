using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Microsoft.Xna.Framework;
using StardewValley;
using StardewValley.Extensions;
using StardewValley.GameData.Locations;
using WikiInGameTools;
using WikiIngameTools.Framework;

namespace WikiIngameTools.CalcFishesProb.Framework;

internal static class FishesProb
{
    /// <summary>
    /// 鱼类的原始数据。
    /// </summary>
    /// <remarks>
    /// 该数组存储了鱼类相关的各种属性，具体索引含义如下：
    /// <list type="table">
    ///   <item><term>[0]</term><description>英文名称：鱼的英文名称。</description></item>
    ///   <item><term>[1]</term><description>难度：捕获该鱼的难度值，若是蟹笼鱼类，则为 trap。</description></item>
    ///   <item><term>[2]</term><description>类型：鱼的分类（例如淡水鱼、海水鱼等）。</description></item>
    ///   <item><term>[3]</term><description>最小英寸：鱼的最小尺寸（单位：英寸）。</description></item>
    ///   <item><term>[4]</term><description>最大英寸：鱼的最大尺寸（单位：英寸）。</description></item>
    ///   <item><term>[5]</term><description>出没时间范围：鱼出现的时间段。</description></item>
    ///   <item><term>[6]</term><description>出没季节：鱼出现的季节。</description></item>
    ///   <item><term>[7]</term><description>出没天气：鱼出现的天气条件。</description></item>
    ///   <item><term>[8]</term><description>已弃用的地点概率数值：某些地点的弃用概率值。</description></item>
    ///   <item><term>[9]</term><description>最深浮标距离：鱼上钩所需的最深浮标距离。</description></item>
    ///   <item><term>[10]</term><description>基础概率：鱼的基础出现概率。</description></item>
    ///   <item><term>[11]</term><description>距离衰减率：鱼出现概率随距离的变化率。</description></item>
    ///   <item><term>[12]</term><description>需求钓鱼等级：捕获该鱼所需的最低钓鱼等级。</description></item>
    ///   <item><term>[13]</term><description>是否为教程鱼：指示该鱼是否用于教程。</description></item>
    /// </list>
    /// </remarks>
    private static string[] SpecificFishData { get; set; }
    
    /// <summary>
    /// 计算鱼的咬钩概率。
    /// </summary>
    /// <param name="fish">当前鱼。</param>
    /// <param name="location">正在钓鱼的地点。</param>
    /// <param name="player">正在钓鱼的玩家。</param>
    /// <param name="spawn">当前鱼的生成数据。</param>
    /// <param name="waterDepth">钓鱼浮标当前的水深。</param>
    /// <param name="localWeather">当前位置的天气</param>
    /// <param name="time">当前时间</param>
    /// <param name="usingMagicBait">玩家是否装备了魔法鱼饵。</param>
    /// <param name="usingTargetBait">玩家是否装备了针对性鱼饵。</param>
    /// <param name="usingCuriosityLure">玩家是否装备了珍稀诱钩。</param>
    /// <param name="usingTrainingRod">玩家是否使用训练用钓竿。</param>
    /// <param name="isTutorialCatch">玩家是否是第一次钓鱼。</param>
    /// <returns></returns>
    private static float HookProbability(Item fish, GameLocation location, Fisher player, string localWeather,
        int time, SpawnFishData spawn, int waterDepth, bool usingMagicBait=false, bool usingTargetBait=false, 
        bool usingCuriosityLure=false, bool usingTrainingRod=false, bool isTutorialCatch=false)
	{
        // 加载 Data/Fish 数据
        var allFishData = DataLoader.Fish(Game1.content);
        
        // 若钓到了秘密物品或垃圾，则一定上钩
		if (!fish.HasTypeObject() || !allFishData.TryGetValue(fish.ItemId, out var rawSpecificFishData))
            return 1;
        
        // 拆分从 fish.json 中获取的原始数据
		SpecificFishData = rawSpecificFishData.Split('/');
        
        // 判断是否是蟹笼鱼类，若是蟹笼鱼类，则上钩失败 （注：原代码为一定上钩）
		if (ArgUtility.Get(SpecificFishData, 1) == "trap")
            return 0;
        
        // 判断使用训练钓鱼竿能否钓上当前的鱼
		if (usingTrainingRod)
		{
            // 若当前鱼不能够使用训练用鱼竿钓上，则上钩失败
			var canUseTrainingRod = spawn.CanUseTrainingRod;
            if (canUseTrainingRod.HasValue && !canUseTrainingRod.Value) 
                return 0;
            
            // 若未能获取难度数据，则上钩失败
            if (!ArgUtility.TryGetInt(SpecificFishData, 1, out var difficulty, out _))
                return 0;
            
            // 若当前鱼的难度大于 50，则上钩失败
            if (difficulty >= 50)
                return 0;
		}
        
        // 判断第一次钓鱼时能否钓上当前的鱼
		if (isTutorialCatch)
		{
            // 若未能获取当前鱼是否是教程鱼类的数据，则上钩失败
			if (!ArgUtility.TryGetOptionalBool(SpecificFishData, 13, out var isTutorialFish, out _))
                return 0;
            
            // 若当前鱼不是教程鱼类，则上钩失败
            if (!isTutorialFish)
                return 0;
        }
        
        // 判断当前鱼是否忽略其他条件生成
		if (spawn.IgnoreFishDataRequirements) 
            return 1;
		
        // 判断未使用魔法鱼饵时，是否满足时间要求
		if (!usingMagicBait)
		{
            // 若未能获取出没时间数据，则上钩失败
			if (!ArgUtility.TryGet(SpecificFishData, 5, out var rawTimeSpans, out _))
				return 0;
			
            // 拆分出没时间数据，得到开始时间与结束时间
			var timeSpans = ArgUtility.SplitBySpace(rawTimeSpans);
			var found = false;
			for (var i = 0; i < timeSpans.Length; i += 2)
			{
                // 若出没时间数据解析有误，则上钩失败
				if (!ArgUtility.TryGetInt(timeSpans, i, out var startTime, out _) || 
                    !ArgUtility.TryGetInt(timeSpans, i + 1, out var endTime, out _))
					return 0;
				
                // 若出没时间满足条件，将 found 设为 true
				if (time >= startTime && time < endTime)
				{
					found = true;
					break;
				}
			}
            
            // 若出没时间不满足条件，则上钩失败
			if (!found)
                return 0;
		}
        
        // 判断未使用魔法鱼饵时，是否满足天气要求
		if (!usingMagicBait)
		{
            // 若未能获取出没天气数据，则上钩失败
			if (!ArgUtility.TryGet(SpecificFishData, 7, out var weather, out _))
                return 0;
            
            // 若天气不满足要求，则上钩失败
            switch (weather)
            {
                case "sunny" when localWeather == "rainy":
                case "rainy" when localWeather == "sunny":
                    return 0;
            }
		}
        
        // 若未能获取钓鱼等级要求数据，则上钩失败
		if (!ArgUtility.TryGetInt(SpecificFishData, 12, out var minFishingLevel, out _))
		    return 0;
        
        // 若玩家钓鱼等级不满足要求，则上钩失败
        if (player.FishingLevel < minFishingLevel)
            return 0;
		
        // 若未能获取水深、基础概率和距离衰减率数据，则上钩失败
		if (!ArgUtility.TryGetInt(SpecificFishData, 9, out var maxDepth, out _) || 
            !ArgUtility.TryGetFloat(SpecificFishData, 10, out var chance, out _) || 
            !ArgUtility.TryGetFloat(SpecificFishData, 11, out var depthMultiplier, out _))
            return 0;
        
        // 根据当前浮标位置的水深，降低上钩概率
		chance -= Math.Max(0, maxDepth - waterDepth) * depthMultiplier * chance;
        
        // 根据玩家当前钓鱼等级，提升上钩概率
		chance += player.FishingLevel / 50f;
        
        // 若使用使用训练用钓竿，提升上钩概率
		if (usingTrainingRod) 
            chance *= 1.1f;
		
        // 限制咬钩概率最大不超过 0.9
		chance = Math.Min(chance, 0.9f);
        
        // 若当前鱼上钩概率小于 0.25，且装备了珍稀诱钩
		if (chance < 0.25 && usingCuriosityLure)
		{
            // 若当前鱼上钩概率受珍稀诱钩影响，直接提升固定数值的上钩概率
			if (spawn.CuriosityLureBuff > -1f)
                chance += spawn.CuriosityLureBuff;
            
            // 若当前鱼上钩概率不受到珍稀诱钩影像，按公式计算提升的上钩概率
			else
                chance = 0.17f / 0.25f * chance + 0.17f / 2f;
		}
        
        // 若使用了针对性鱼饵，提升上钩概率
		if (usingTargetBait) 
            chance *= 1.66f;
		
        // 根据当前鱼上钩概率是否受每日运气影响，调整上钩概率
		if (spawn.ApplyDailyLuck) 
            chance += player.DailyLuck;
		
        // 特殊物品的概率修饰器，仅适用于《林景》、绿叶画和松鼠雕像
		var chanceModifiers = spawn.ChanceModifiers;
		if (chanceModifiers is { Count: > 0 })
            chance = Utility.ApplyQuantityModifiers(chance, spawn.ChanceModifiers, spawn.ChanceModifierMode, location);

        return chance;
    }
    
    /// <summary>
    /// 计算鱼的存活概率。
    /// </summary>
    /// <param name="player">正在钓鱼的玩家。</param>
    /// <param name="spawn">当前鱼的生成数据。</param>
    /// <param name="usingCuriosityLure">玩家是否装备了珍稀诱钩。</param>
    /// <param name="usingTargetBait">玩家是否装备了针对性鱼饵。</param>
    /// <returns>当前鱼的存活概率</returns>
    private static float SurvivalProbability(Fisher player, SpawnFishData spawn, 
        bool usingCuriosityLure=false, bool usingTargetBait=false)
    {
        // 读取当前鱼的基础存活概率
        var chance = spawn.Chance;
        
        // 若当前鱼的上钩概率受珍稀诱钩影响，增加概率
        if (usingCuriosityLure && spawn.CuriosityLureBuff > 0f)
            chance += spawn.CuriosityLureBuff;
        
        // 若当前鱼的上钩概率受玩家的每日运气影响，增加概率
        if (spawn.ApplyDailyLuck)
            chance += player.DailyLuck;
        
        // 若当前鱼的上钩概率存在概率修饰器，则应用概率修饰器
        var chanceModifiers = spawn.ChanceModifiers;
        if (chanceModifiers is { Count: > 0 })
            chance = Utility.ApplyQuantityModifiers(chance, spawn.ChanceModifiers, spawn.ChanceModifierMode);
        
        // 若使用了针对性鱼饵，增加概率
        if (usingTargetBait)
            chance = chance * spawn.SpecificBaitMultiplier + spawn.SpecificBaitBuff;
        
        return chance + spawn.ChanceBoostPerLuckLevel * player.LuckLevel;
    }

    /// <summary>
    /// 获取当前地点所有可能的鱼类数据。
    /// </summary>
    /// <returns></returns>
    private static IEnumerable<SpawnFishData> GetPossibleFish(Fisher player, GameLocation location, Vector2 bobberTile, 
        Season season, int waterDepth, bool usingMagicBait=false, bool isInherited=false)
    {
        var farmer = Game1.player;
        var standPoint = farmer.TilePoint;
        
        // 获取当前浮标位置的钓鱼区信息
        var locationData = location.GetData();
        if (!location.TryGetFishAreaForTile(bobberTile, out var fishAreaId, out _))
            fishAreaId = null;
        
        // 若当前位置不存在任何钓鱼信息，返回空值
        if (locationData is { Fish.Count: 0 }) return null;
        
        // 从游戏数据中加载默认鱼类数据
        var spawnFishData = new List<SpawnFishData>()
            .Concat(Game1.locationData["Default"].Fish)
            .Concat(locationData.Fish)
            .OrderBy(p => p.Precedence)
            .ToList();

        var possibleFish = new List<SpawnFishData>();
        
        foreach (var spawn in spawnFishData)
        {
            // 排除当前钓鱼区域与季节不满足条件的情况
            if ((isInherited && !spawn.CanBeInherited) || 
                (spawn.FishAreaId != null && fishAreaId != spawn.FishAreaId) || 
                (spawn.Season.HasValue && spawn.Season != season))
                continue;
            
            // 排除当前玩家所站位置不满足条件的情况
            var playerPosition = spawn.PlayerPosition;
            if (playerPosition?.Contains(standPoint.X, standPoint.Y) == false)
                continue;
            
            // 排除浮标位置不满足要求、钓鱼等级不满足要求、水深不满足要求的情况
            var bobberPosition = spawn.BobberPosition;
            if (bobberPosition?.Contains((int)bobberTile.X, (int)bobberTile.Y) == false || 
                player.FishingLevel < spawn.MinFishingLevel || 
                waterDepth < spawn.MinDistanceFromShore || 
                (spawn.MaxDistanceFromShore > -1 && waterDepth > spawn.MaxDistanceFromShore))
                continue;
            
            // 排除不满足指定条件的情况
            var ignoreQueryKeys = usingMagicBait ? GameStateQuery.MagicBaitIgnoreQueryKeys : null;
            if (spawn.Condition != null && 
                !GameStateQuery.CheckConditions(spawn.Condition, location, null, null, null, null, ignoreQueryKeys))
                continue;
            
            // var item = ItemQueryResolver.TryResolveRandomItem(spawn, null, avoidRepeat: false, null, 
            //     query => query
            //         .Replace("BOBBER_X", ((int)bobberTile.X).ToString())
            //         .Replace("BOBBER_Y", ((int)bobberTile.Y).ToString())
            //         .Replace("WATER_DEPTH", waterDepth.ToString()));
            // if (item == null)
            //     continue;

            possibleFish.Add(spawn);
        }

        return possibleFish;
    }

    /// <summary>
    /// 将鱼类数据序列化为 Json。
    /// </summary>
    /// <param name="fishes">当前地点可能出现的所有鱼类数据</param>
    /// <param name="c">所有外部条件，包括季节、天气、水深等</param>
    private static void ConvertToJson(List<Fish> fishes, FishConditions c)
    {
        // 将当前钓鱼等级情况下，所有水深可钓到的鱼类数据序列化为 json
        var savePath = Path.Combine("output", c.Location, $"{c.Season},{c.Weather},{c.Time},{c.Level},{c.Depth}.json");
        var absolutePath = Path.Combine(ModEntry.ModHelper.DirectoryPath, savePath);
        try
        {
            ModEntry.ModHelper.Data.WriteJsonFile(savePath, fishes);
        }
        catch (Exception ex)
        {
            ModEntry.Log($"无法导出数据至 {absolutePath}");
            ModEntry.Log(ex.ToString());
        }
    }
    
    /// <summary>
    /// 获取当前地点、当前浮标位置下可能钓到的所有鱼类列表，然后转化为 Json
    /// 文件存储到 output 文件夹下，其中浮标位置使用的是光标所在位置。
    /// </summary>
    public static void GetAllFishData()
    {
        // 获取当前位置和鼠标所在区域的地块坐标
        var location = Game1.currentLocation;
        var bobberTile = Utilities.GetTile();
        var season = Game1.GetSeasonForLocation(location);
        var weather = Game1.IsRainingHere(location)
            ? "rainy"
            : "sunny";

        // 获取当前水深，由于未找到合适的计算方法，因此默认为 5，部分地点根据其最大水深做调整
        // 对于其它需要调整水深的情况，需使用 config
        var depth = ModEntry.Config.CalcFishesProbModConfig.CustomWaterDepth 
            ? ModEntry.Config.CalcFishesProbModConfig.WaterDepth 
            : location.Name switch 
            {
                "Secret Woods" => 3,
                "Calico Desert" => 2,
                "IslandNorth" => 1,
                _ => 5
            };

        // 遍历游戏内所有的时间段
        for (var time = 630; time < 2630; time += 100)
        {
            /* 因为时间复杂度太高而弃用
            // 遍历原版游戏内所有可能出现的钓鱼等级
            for (var level = 0; level <= 19; level++)
            {
                // 新建渔夫实例，默认不考虑任何运气等级
                var fisher = new Fisher(level);

                // 遍历原版游戏内所有可能出现的水深
                for (var depth = 0; depth <= 5; depth++)
                {
                    // 新建列表用于存储所有可能出现的鱼
                    var fishes = new List<Fish>();

                    // 获取所有可能出现的鱼类
                    var fishData = GetPossibleFish(fisher, location, bobberTile, season, depth);
                    foreach (var spawn in fishData)
                    {
                        // 新建 Fish 实例并加入至 fishes 列表
                        var fish = new Fish(GetFishName(spawn), spawn.Precedence,
                            SurvivalProbability(fisher, spawn),
                            HookProbability(GetFish(spawn), location, fisher, weather, time, spawn, depth));
                        fishes.Add(fish);
                    }

                    var conditions = new Conditions(location, season.ToString(), weather, time, level, depth);
                    ConvertToJson(fishes, conditions);
                }
            }*/
            
            // 新建渔夫实例，默认不考虑任何运气等级
            var fisher = new Fisher(10);
            
            // 新建列表用于存储所有可能出现的鱼
            var fishes = new List<Fish>();

            // 获取所有可能出现的鱼类
            var fishData = GetPossibleFish(fisher, location, bobberTile, season, depth);
            foreach (var spawn in fishData)
            {
                // 新建 Fish 实例并加入至 fishes 列表
                var fish = new Fish(spawn.GetFishName(), spawn.Precedence,
                    SurvivalProbability(fisher, spawn),
                    HookProbability(spawn.GetFish(), location, fisher, weather, time, spawn, depth));
                
                // 剔除不满足条件的情况
                if (fish.SurvivalProb > 0 && fish.HookProb > 0)
                    fishes.Add(fish);
            }

            var conditions = new FishConditions(location, season.ToString(), weather, time, 10, depth);
            ConvertToJson(fishes, conditions);
        }
    }
}