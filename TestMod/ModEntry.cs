using HarmonyLib;
using StardewModdingAPI;
using StardewValley.TerrainFeatures;
using TestMod.Config;

namespace TestMod
{
    /// <summary>Mod的主入口类，负责初始化所有功能。</summary>
    internal class ModEntry : Mod
    {
        private ModConfig _config;
        public static IMonitor StaticMonitor { get; private set; }

        /// <summary>Mod的入口点，在Mod被加载后由SMAPI调用。</summary>
        public override void Entry(IModHelper helper)
        {
            StaticMonitor = this.Monitor;

            // 1. 读取或创建变量监控器的配置文件
            this._config = this.Helper.ReadConfig<ModConfig>();
            this.Helper.WriteConfig(this._config);

            // 2. 初始化Harmony
            var harmony = new Harmony(this.ModManifest.UniqueID);

            // 3. 应用所有硬编码的C#补丁 (古代种子)
            this.ApplyCSharpPatches(helper, harmony);

            // 4. 应用变量监控功能
            var monitor = new VariableMonitor(this.Monitor, harmony);
            monitor.ApplyFromConfig(this._config);
        }

        /// <summary>应用所有硬编码的C#补丁。</summary>
        private void ApplyCSharpPatches(IModHelper helper, Harmony harmony)
        {
            // 初始化补丁类
            GrassPatches.Initialize(this.Monitor, helper);
            CosmeticPlantPatches.Initialize(this.Monitor, helper);

            // 应用 Grass 补丁
            var grassPatch = new HarmonyMethod(typeof(GrassPatches), nameof(GrassPatches.TryDropItemsOnCut_Prefix));
            harmony.Patch(
                original: AccessTools.Method(typeof(Grass), nameof(Grass.TryDropItemsOnCut)),
                prefix: grassPatch
            );
            this.Monitor.Log($"已为 {typeof(Grass).FullName} 注入 {grassPatch.method.Name} 补丁", LogLevel.Info);

            // 应用 CosmeticPlant 补丁
            var cosmeticPatch = new HarmonyMethod(typeof(CosmeticPlantPatches), nameof(CosmeticPlantPatches.performToolAction_Prefix));
            harmony.Patch(
                original: AccessTools.Method(typeof(CosmeticPlant), nameof(CosmeticPlant.performToolAction)),
                prefix: cosmeticPatch
            );
            this.Monitor.Log($"已为 {typeof(CosmeticPlant).FullName} 注入 {cosmeticPatch.method.Name} 补丁", LogLevel.Info);
        }
    }
}