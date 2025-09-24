using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.Xna.Framework;
using Newtonsoft.Json;

namespace StoneProbabilityCalculator;

public class CalcThread
{
    private const double ChanceForPurpleStone = 0.001;
    private const double ChanceForMysticStone = 0.00005;
    private const double GemStoneChance = 0.0015;

    private readonly Random _random = new();
    private readonly Random _game1Random = new();

    public readonly int AdditionalDifficulty;
    public readonly double AverageDailyLuck;
    public readonly int MineLevel;
    private readonly int _averageLuckLevel;
    private readonly int _averageMiningLevel;

    private readonly Dictionary<string, int> _stats = new();

    public CalcThread(double dailyLuck, int mineLevel, int luckLevel, int miningLevel, int difficulty=0)
    {
        AdditionalDifficulty = difficulty;
        AverageDailyLuck = dailyLuck;
        MineLevel = mineLevel;
        _averageLuckLevel = luckLevel;
        _averageMiningLevel = miningLevel;
    }

    public string Run(int x)
    {
        var percentage = 10;
        for (var i = 1; i <= 1000_0000 * x; i++)
        {
            var obj = GenerateRandomStone();
            _stats.IncrementValue(obj);
            if (i % (100_0000 * x) == 0)
            {
                Console.WriteLine($"{MineLevel},{AverageDailyLuck},{AdditionalDifficulty}: {percentage} %");
                percentage += 10;
            }
        }

        var newDict = _stats.ToDictionary(kvp => kvp.Key.ID2Name(), kvp => kvp.Value);
        return JsonConvert.SerializeObject(newDict, Formatting.Indented);
    }

    private string GenerateRandomStone()
    {
        var stoneColor = Color.White;
        if (AdditionalDifficulty > 0 && _random.NextDouble() <
            AdditionalDifficulty * 0.001 + MineLevel / 100000f +
            AverageDailyLuck / 13.0 + _averageLuckLevel * 0.00015)
            return "95";
        int whichStone;
        // 矿井 1~40 层
        if (GetMineArea() == 0 || GetMineArea() == 10)
        {
            whichStone = _random.Next(31, 42);
            if (!IsDarkArea() && whichStone is >= 33 and < 38)
                whichStone = _random.Choose(32, 38);
            else if (IsDarkArea()) 
                whichStone = _random.Choose(34, 36);
            if (AdditionalDifficulty > 0)
            {
                whichStone = _random.Next(33, 37);
                if (_game1Random.NextDouble() < 0.33)
                    whichStone = 846;
                else
                    stoneColor = new Color(_game1Random.Next(60, 90), _game1Random.Next(150, 200),
                        _game1Random.Next(190, 240));
                if (IsDarkArea())
                {
                    whichStone = _random.Next(32, 39);
                    var tone = _game1Random.Next(130, 160);
                    stoneColor = new Color(tone, tone, tone);
                }

                if (MineLevel != 1 && _random.NextDouble() < 0.029)
                    return "849";
                if (stoneColor.Equals(Color.White))
                    return whichStone.ToString();
            }
            else if (MineLevel != 1 &&  _random.NextDouble() < 0.029)
            {
                return "751";
            }
        }
        // 矿井 41~80 层
        else if (GetMineArea() == 40)
        {
            whichStone = _random.Next(47, 54);
            if (AdditionalDifficulty > 0 && !IsDarkArea())
            {
                whichStone = _random.Next(39, 42);
                stoneColor = new Color(170, 255, 160);
                if (IsDarkArea())
                {
                    whichStone = _random.Next(32, 39);
                    var tone2 = _game1Random.Next(130, 160);
                    stoneColor = new Color(tone2, tone2, tone2);
                }

                if (_random.NextDouble() < 0.15)
                    return (294 + _random.Choose(1, 0)).ToString();
                if (MineLevel != 1 && _random.NextDouble() < 0.029)
                    return "290";
                if (stoneColor.Equals(Color.White))
                    return whichStone.ToString();
            }
            else if (_random.NextDouble() < 0.029)
            {
                return "290";
            }
        }
        // 矿井 81~120 层
        else if (GetMineArea() == 80)
        {
            whichStone = _random.NextDouble() < 0.3 && !IsDarkArea() ? !_random.NextBool() ? 32 : 38 :
                _random.NextDouble() < 0.3 ? _random.Next(55, 58) :
                !_random.NextBool() ? 762 : 760;
            if (AdditionalDifficulty > 0)
            {
                whichStone = !_random.NextBool() ? 32 : 38;
                stoneColor = new Color(_game1Random.Next(140, 190), _game1Random.Next(90, 120),
                    _game1Random.Next(210, 255));
                if (IsDarkArea())
                {
                    whichStone = _random.Next(32, 39);
                    var tone3 = _game1Random.Next(130, 160);
                    stoneColor = new Color(tone3, tone3, tone3);
                }

                if (MineLevel != 1 && _random.NextDouble() < 0.029)
                    return "764";
                if (stoneColor.Equals(Color.White))
                    return whichStone.ToString();
            }
            else if (_random.NextDouble() < 0.029)
                return "764";
        }
        // 骷髅洞穴和采石场矿井
        else
        {
            // 采石场矿井，此处不考虑
            // if (GetMineArea() == 77377)
            // {
            //     var foundSomething = false;
            //     foreach (var v in Utility.getAdjacentTileLocations(tile))
            //         if (objects.ContainsKey(v))
            //         {
            //             foundSomething = true;
            //             break;
            //         }
            //
            //     if (!foundSomething && Random.NextDouble() < 0.45) return null;
            //     var brownSpot = false;
            //     for (var i = 0; i < brownSpots.Count; i++)
            //     {
            //         if (Vector2.Distance(tile, brownSpots[i]) < 4f)
            //         {
            //             brownSpot = true;
            //             break;
            //         }
            //
            //         if (Vector2.Distance(tile, brownSpots[i]) < 6f) return null;
            //     }
            //
            //     if (tile.X > 50f)
            //     {
            //         whichStone = Game1Random.Choose(668, 670);
            //         if (Random.NextDouble() < 0.09 + _averageDailyLuck / 2.0)
            //             return Game1Random.Choose("BasicCoalNode0", "BasicCoalNode1");
            //         if (Random.NextDouble() < 0.25) return null;
            //     }
            //     else if (brownSpot)
            //     {
            //         whichStone = Random.Choose(32, 38);
            //         if (Random.NextDouble() < 0.01)
            //             return "751";
            //     }
            //     else
            //     {
            //         whichStone = Random.Choose(34, 36);
            //         if (Random.NextDouble() < 0.01)
            //             return "290";
            //     }
            //
            //     return whichStone.ToString();
            // }

            whichStone = _random.NextBool() ? !_random.NextBool() ? 32 : 38 : !_random.NextBool() ? 42 : 40;
            var skullCavernMineLevel = MineLevel - 120;
            var chanceForOre = 0.02 + skullCavernMineLevel * 0.0005;

            if (MineLevel >= 130)
                chanceForOre += 0.01 * ((Math.Min(100, skullCavernMineLevel) - 10) / 10f);

            var iridiumBoost = 0.0;
            if (MineLevel >= 130) iridiumBoost += 0.001 * ((skullCavernMineLevel - 10) / 10f);
            iridiumBoost = Math.Min(iridiumBoost, 0.004);

            if (skullCavernMineLevel > 100)
                iridiumBoost += skullCavernMineLevel / 1000000.0;

            if (_random.NextDouble() < chanceForOre)
            {
                var chanceForIridium = Math.Min(100, skullCavernMineLevel) * (0.0003 + iridiumBoost);
                var chanceForGold = 0.01 + (MineLevel - Math.Min(150, skullCavernMineLevel)) * 0.0005;
                var chanceForIron = Math.Min(0.5, 0.1 + (MineLevel - Math.Min(200, skullCavernMineLevel)) * 0.005);

                if (_random.NextDouble() < chanceForIridium)
                    return "765";

                if (_random.NextDouble() < chanceForGold)
                    return "764";

                if (_random.NextDouble() < chanceForIron)
                    return "290";

                return "751";
            }
        }

        var chanceModifier = AverageDailyLuck + _averageMiningLevel * 0.005;
        // 钻石矿
        // 0.00025 * (1 + 每日运气 + 采矿等级 * 0.005) + 矿井层数 / 120000
        if (MineLevel > 50 && _random.NextDouble() < 0.00025 + MineLevel / 120000.0 + 0.0005 * chanceModifier / 2.0)
            whichStone = 2;

        //  0.0015 * (1 + 每日运气 + 采矿等级 * 0.005) + 矿井层数 / 24000，直接返回
        else if (_random.NextDouble() < GemStoneChance + GemStoneChance * chanceModifier + MineLevel / 24000.0)
            return GetRandomGemRichStoneForThisLevel(MineLevel);

        // 紫色宝石矿：
        // 0.0005 (1 + 每日运气 + 矿井层数 * 0.016) ≈ 0.13%
        if (_random.NextDouble() <
            ChanceForPurpleStone / 2.0 + ChanceForPurpleStone * _averageMiningLevel * 0.008 +
            ChanceForPurpleStone * (AverageDailyLuck / 2.0))
            whichStone = 44;

        // 神秘石：
        // 0.00005 (1 + 每日运气 / 2 + 矿井层数 * 0.008) ≈ 0.009%
        if (MineLevel > 100 && _random.NextDouble() <
            ChanceForMysticStone + ChanceForMysticStone * _averageMiningLevel * 0.008 +
            ChanceForMysticStone * (AverageDailyLuck / 2.0))
            whichStone = 46;

        whichStone += whichStone % 2;
        if (_random.NextDouble() < 0.1 && GetMineArea() != 40)
            return _random.Choose("668", "670");

        return whichStone.ToString();
    }

    private int GetMineArea() =>
        MineLevel switch
        {
            > 0 and <= 40 => 0,
            > 40 and <= 80 => 40,
            > 80 and <= 120 => 80,
            77377 => 77377,
            _ => -1
        };

    private bool IsDarkArea() => MineLevel % 40 >= 30;

    private string GetRandomGemRichStoneForThisLevel(int level, bool reachedMineBottom = true)
    {
        var whichGem = _random.Next(59, 70);
        whichGem += whichGem % 2;
        if (!reachedMineBottom)
        {
            if (level < 40 && whichGem != 66 && whichGem != 68)
                whichGem = _random.Choose(66, 68);
            else if (level < 80 && (whichGem == 64 || whichGem == 60))
                whichGem = _random.Choose(66, 70, 68, 62);
        }

        return whichGem switch
        {
            66 => "8",
            68 => "10",
            60 => "12",
            70 => "6",
            64 => "4",
            62 => "14",
            _ => 40.ToString()
        };
    }
}