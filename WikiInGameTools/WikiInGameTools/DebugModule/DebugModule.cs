using HarmonyLib;
using StardewModdingAPI;
using StardewValley.TerrainFeatures;
using WikiInGameTools;
using WikiIngameTools.DebugModule.Patches;
using WikiIngameTools.Framework;
using WikiInGameTools.Framework.ConfigurationService;

namespace WikiIngameTools.DebugModule;

public class DebugModule : IModule
{
    private readonly Harmony _harmony = new (ModEntry.Manifest.UniqueID + ".DebugModule");
    public bool IsActive { get; private set; }
    public IConfig Config => ModEntry.Config.DebugModuleConfig;

    public void Activate()
    {
        IsActive = true;
        // 应用所有硬编码的C#补丁 (古代种子)
        ApplyCSharpPatches(_harmony);
    }

    public void Deactivate()
    {
        IsActive = false;
        _harmony.UnpatchAll(_harmony.Id);
        ModEntry.Log("已取消注入全部补丁", LogLevel.Info);
    }

    /// <summary>应用所有硬编码的C#补丁。</summary>
    private static void ApplyCSharpPatches(Harmony harmony)
    {
        // 初始化补丁类
        GrassPatches.Initialize();
        CosmeticPlantPatches.Initialize();

        // 应用 Grass 补丁
        var grassPatch = new HarmonyMethod(typeof(GrassPatches), nameof(GrassPatches.TryDropItemsOnCut_Prefix));
        harmony.Patch(
            original: AccessTools.Method(typeof(Grass), nameof(Grass.TryDropItemsOnCut)),
            prefix: grassPatch
        );
        ModEntry.Log($"已为 {typeof(Grass).FullName} 注入 {grassPatch.method.Name} 补丁", LogLevel.Info);

        // 应用 CosmeticPlant 补丁
        var cosmeticPatch = new HarmonyMethod(typeof(CosmeticPlantPatches), nameof(CosmeticPlantPatches.performToolAction_Prefix));
        harmony.Patch(
            original: AccessTools.Method(typeof(CosmeticPlant), nameof(CosmeticPlant.performToolAction)),
            prefix: cosmeticPatch
        );
        ModEntry.Log($"已为 {typeof(CosmeticPlant).FullName} 注入 {cosmeticPatch.method.Name} 补丁", LogLevel.Info);
    }
}