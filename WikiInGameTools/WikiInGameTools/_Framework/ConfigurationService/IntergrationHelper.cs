﻿using StardewModdingAPI;

namespace WikiInGameTools._Framework.ConfigurationService;

/// <summary>Simplifies validated access to mod APIs.</summary>
internal static class IntegrationHelper
{
    /// <summary>Get a mod API if it's installed and valid.</summary>
    /// <param name="label">A human-readable name for the mod.</param>
    /// <param name="modId">The mod's unique ID.</param>
    /// <param name="minVersion">The minimum version of the mod that's supported.</param>
    /// <param name="modRegistry">An API for fetching metadata about loaded mods.</param>
    /// <returns>Returns the mod's API interface if valid, else null.</returns>
    private static TInterface GetValidatedApi<TInterface>(string label, string modId, string minVersion,
        IModRegistry modRegistry)
        where TInterface : class
    {
        // check mod installed
        var mod = modRegistry.Get(modId)?.Manifest;
        if (mod == null)
            return null;

        // check mod version
        if (mod.Version.IsOlderThan(minVersion))
        {
            ModEntry.Log(
                $"Detected {label} {mod.Version}, but need {minVersion} or later. Disabled integration with that mod.",
                LogLevel.Warn);
            return null;
        }

        // get API
        var api = modRegistry.GetApi<TInterface>(modId);
        if (api != null) return api;

        ModEntry.Log($"Detected {label}, but couldn't fetch its API. Disabled integration with that mod.",
            LogLevel.Warn);
        return null;
    }

    /// <summary>Get Generic Mod Config Menu's API if it's installed and valid.</summary>
    /// <param name="modRegistry">An API for fetching metadata about loaded mods.</param>
    /// <returns>Returns the API interface if valid, else null.</returns>
    public static IGenericModConfigMenuApi GetGenericModConfigMenu(IModRegistry modRegistry)
    {
        return GetValidatedApi<IGenericModConfigMenuApi>(
            "Generic Mod Config Menu",
            "spacechase0.GenericModConfigMenu",
            "1.6.0",
            modRegistry
        );
    }
}