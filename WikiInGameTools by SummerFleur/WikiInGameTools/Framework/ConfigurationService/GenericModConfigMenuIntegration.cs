using System;
using StardewModdingAPI;
using WikiIngameTools.Framework;

namespace WikiInGameTools.Framework.ConfigurationService;

internal static class GenericModConfigMenuIntegration
{
	public static void Register(IManifest manifest, IModRegistry modRegistry, Func<ModConfig> getConfig, Action reset, Action save)
	{
		IGenericModConfigMenuApi api = IntegrationHelper.GetGenericModConfigMenu(modRegistry);
		if (api != null)
		{
			api.Register(manifest, reset, save);
			api.AddBoolOption(manifest, () => getConfig().CustomWaterDepth, delegate(bool value)
			{
				getConfig().CustomWaterDepth = value;
			}, () => "Enable Custom Water Depth?");
			api.AddNumberOption(manifest, () => getConfig().WaterDepth, delegate(int value)
			{
				getConfig().WaterDepth = value;
			}, () => "Water Depth", null, 0, 5);
		}
	}
}
