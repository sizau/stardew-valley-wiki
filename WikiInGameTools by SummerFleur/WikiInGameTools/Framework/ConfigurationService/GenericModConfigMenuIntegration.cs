using System;
using StardewModdingAPI;

namespace WikiInGameTools.Framework.ConfigurationService;

internal static class GenericModConfigMenuIntegration
{
    public static IGenericModConfigMenuApi Api { get; set; }
    
	public static void Register(IManifest manifest, IModRegistry modRegistry, Action reset, Action save)
	{
		Api = IntegrationHelper.GetGenericModConfigMenu(modRegistry);
		Api?.Register(manifest, reset, save);
	}
}
