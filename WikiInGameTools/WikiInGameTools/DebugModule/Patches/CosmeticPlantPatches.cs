using System;
using Microsoft.Xna.Framework;
using StardewModdingAPI;
using StardewValley;
using StardewValley.Extensions;
using StardewValley.TerrainFeatures;
using StardewValley.Tools;
using WikiInGameTools;

namespace WikiIngameTools.DebugModule.Patches;

/// <summary>包含针对 StardewValley.TerrainFeatures.CosmeticPlant 类的Harmony补丁。</summary>
internal class CosmeticPlantPatches
{
    private static IReflectionHelper ReflectionHelper;

    /// <summary>初始化补丁类，传入必要的SMAPI工具实例。</summary>
    internal static void Initialize()
        => ReflectionHelper = ModEntry.ModHelper.Reflection;

    /// <summary>一个前置补丁，用于完全替换原方法 CosmeticPlant.performToolAction 的逻辑。</summary>
    internal static bool performToolAction_Prefix(CosmeticPlant __instance, ref bool __result, 
        Tool t, int explosion, Vector2 tileLocation)
    {
        try
        {
            var location = __instance.Location;

            if ((t is MeleeWeapon weapon && weapon.type.Value != 2) || explosion > 0)
            {
                // 使用反射调用基类的受保护(protected)方法 shake
                ReflectionHelper.GetMethod(__instance, "shake")
                    .Invoke((float)Math.PI * 3f / 32f, (float)Math.PI / 40f, Game1.random.NextBool());

                var numberOfWeedsToDestroy = explosion > 0 
                    ? Math.Max(1, explosion + 2 - Game1.random.Next(2)) 
                    : t.UpgradeLevel == 3 ? 3 : t.UpgradeLevel + 1;

                Game1.createRadialDebris(location, __instance.textureName(),
                    new Rectangle(__instance.grassType.Value * 16, 6, 7, 6), 
                    (int)tileLocation.X, (int)tileLocation.Y, Game1.random.Next(6, 14));
                __instance.numberOfWeeds.Value -= numberOfWeedsToDestroy;

                if (__instance.numberOfWeeds.Value <= 0)
                {
                    var grassRandom = Utility.CreateRandom(
                        Game1.uniqueIDForThisGame, 
                        tileLocation.X * 7.0,
                        tileLocation.Y * 11.0, 
                        Game1.CurrentMineLevel, 
                        Game1.player.timesReachedMineBottom);

                    // 核心修改：将掉落古代种子的概率从 0.005 (0.5%) 修改为 1.0 (100%)
                    if (grassRandom.NextDouble() < 1.0)
                        Game1.createObjectDebris("(O)114", (int)tileLocation.X, (int)tileLocation.Y, 
                            -1, 0, 1f, location);
                    else if (grassRandom.NextDouble() < 0.01)
                        Game1.createDebris(4, (int)tileLocation.X, (int)tileLocation.Y, 
                            grassRandom.Next(1, 2), location);
                    else if (grassRandom.NextDouble() < 0.02)
                        Game1.createDebris(92, (int)tileLocation.X, (int)tileLocation.Y, 
                            grassRandom.Next(2, 4), location);
                    __result = true;
                    return false;
                }
            }

            __result = false;
            return false;
        }
        catch (Exception ex)
        {
            ModEntry.Log($"在补丁 {nameof(performToolAction_Prefix)} 中发生错误:\n{ex}", LogLevel.Error);
            return true;
        }
    }
}