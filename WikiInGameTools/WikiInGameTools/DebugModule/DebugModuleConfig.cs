using System.Collections.Generic;
using WikiIngameTools.DebugModule.Framework;
using WikiInGameTools.Framework.ConfigurationService;

namespace WikiIngameTools.DebugModule;

public class DebugModuleConfig : IConfig
{
    public bool Enable { get; set; }

    /// <summary>一个由用户在config.json中定义的、需要监控的变量目标列表。</summary>
    public List<MonitorTarget> VariableMonitor { get; set; } = new ();
}