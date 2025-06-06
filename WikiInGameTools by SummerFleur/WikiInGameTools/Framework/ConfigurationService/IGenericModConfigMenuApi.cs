using System;
using StardewModdingAPI;

namespace WikiInGameTools.Framework.ConfigurationService;

public interface IGenericModConfigMenuApi
{
	void Register(IManifest manifest, Action reset, Action save, bool titleScreenOnly = false);
    
    void AddSectionTitle(IManifest manifest, Func<string> text, Func<string> tooltip = null);

	void AddBoolOption(IManifest manifest, Func<bool> getValue, Action<bool> setValue, Func<string> name, Func<string> tooltip = null, string fieldId = null);

	void AddNumberOption(IManifest manifest, Func<int> getValue, Action<int> setValue, Func<string> name, Func<string> tooltip = null, int? min = null, int? max = null, int? interval = null, Func<int, string> formatValue = null, string fieldId = null);
}
