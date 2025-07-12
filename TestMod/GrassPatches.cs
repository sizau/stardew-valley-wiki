using HarmonyLib;
using Microsoft.Xna.Framework;
using StardewModdingAPI;
using StardewValley;
using StardewValley.TerrainFeatures;
using System;

namespace TestMod
{
    /// <summary>包含针对 StardewValley.TerrainFeatures.Grass 类的Harmony补丁。</summary>
    internal class GrassPatches
    {
        private static IMonitor Monitor;
        private static IReflectionHelper Reflection;

        /// <summary>初始化补丁类，传入必要的SMAPI工具实例。</summary>
        internal static void Initialize(IMonitor monitor, IModHelper helper)
        {
            Monitor = monitor;
            Reflection = helper.Reflection;
        }

        /// <summary>一个前置补丁，用于完全替换原方法 Grass.TryDropItemsOnCut 的逻辑。</summary>
        internal static bool TryDropItemsOnCut_Prefix(Grass __instance, ref bool __result, Tool tool)
        {
            try
            {
                Vector2 tileLocation = __instance.Tile;
                GameLocation location = __instance.Location;

                if (__instance.numberOfWeeds.Value <= 0)
                {
                    if (__instance.grassType.Value != 1 && __instance.grassType.Value != 7)
                    {
                        Random grassRandom = (Game1.IsMultiplayer ? Game1.recentMultiplayerRandom : Utility.CreateRandom(Game1.uniqueIDForThisGame, (double)tileLocation.X * 1000.0, (double)tileLocation.Y * 11.0, Game1.CurrentMineLevel, Game1.player.timesReachedMineBottom));

                        // 核心修改：将掉落古代种子的概率从 0.005 (0.5%) 修改为 1.0 (100%)
                        if (grassRandom.NextDouble() < 1.0)
                        {
                            Game1.createObjectDebris("(O)114", (int)tileLocation.X, (int)tileLocation.Y, -1, 0, 1f, location);
                        }
                        else if (grassRandom.NextDouble() < 0.01)
                        {
                            Game1.createDebris(4, (int)tileLocation.X, (int)tileLocation.Y, grassRandom.Next(1, 2), location);
                        }
                        else if (grassRandom.NextDouble() < 0.02)
                        {
                            Game1.createObjectDebris("(O)92", (int)tileLocation.X, (int)tileLocation.Y, grassRandom.Next(2, 4), location);
                        }
                    }
                    else if (tool != null && tool.isScythe())
                    {
                        Farmer player = tool.getLastFarmerToUse() ?? Game1.player;
                        Random obj = (Game1.IsMultiplayer ? Game1.recentMultiplayerRandom : Utility.CreateRandom(Game1.uniqueIDForThisGame, (double)tileLocation.X * 1000.0, (double)tileLocation.Y * 11.0));
                        double chance = ((tool.ItemId == "66") ? 1.0 : ((tool.ItemId == "53") ? 0.75 : 0.5));
                        if (player.currentLocation.IsWinterHere())
                        {
                            chance *= 0.33;
                        }
                        if (obj.NextDouble() < chance)
                        {
                            int num = ((__instance.grassType.Value != 7) ? 1 : 2);
                            if (GameLocation.StoreHayInAnySilo(num, __instance.Location) == 0)
                            {
                                TemporaryAnimatedSprite tmpSprite = new TemporaryAnimatedSprite("Maps\\springobjects", Game1.getSourceRectForStandardTileSheet(Game1.objectSpriteSheet, 178, 16, 16), 750f, 1, 0, player.Position - new Vector2(0f, 128f), flicker: false, flipped: false, player.Position.Y / 10000f, 0.005f, Color.White, 4f, -0.005f, 0f, 0f);
                                tmpSprite.motion.Y = -3f + (float)Game1.random.Next(-10, 11) / 100f;
                                tmpSprite.acceleration.Y = 0.07f + (float)Game1.random.Next(-10, 11) / 1000f;
                                tmpSprite.motion.X = (float)Game1.random.Next(-20, 21) / 10f;
                                tmpSprite.layerDepth = 1f - (float)Game1.random.Next(100) / 10000f;
                                tmpSprite.delayBeforeAnimationStart = Game1.random.Next(150);
                                // 使用SMAPI的反射助手来调用内部(internal)成员 Game1.multiplayer
                                Reflection.GetField<Multiplayer>(typeof(Game1), "multiplayer").GetValue().broadcastSprites(__instance.Location, tmpSprite);
                                Game1.addHUDMessage(HUDMessage.ForItemGained(ItemRegistry.Create("(O)178"), num));
                            }
                        }
                    }
                    __result = true;
                }
                else
                {
                    __result = false;
                }

                // 返回 false，阻止游戏执行原版方法
                return false;
            }
            catch (Exception ex)
            {
                Monitor.Log($"在补丁 {nameof(TryDropItemsOnCut_Prefix)} 中发生错误:\n{ex}", LogLevel.Error);
                // 如果我们的补丁出错，返回 true 让原版方法执行，防止游戏崩溃
                return true;
            }
        }
    }
}