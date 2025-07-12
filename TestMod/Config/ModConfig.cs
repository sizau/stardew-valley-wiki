using System.Collections.Generic;
using TestMod.Config;

namespace TestMod
{
    /// <summary>定义了Mod的配置文件 (config.json) 的结构。</summary>
    internal class ModConfig
    {
        /// <summary>一个由用户在config.json中定义的、需要监控的变量目标列表。</summary>
        public List<MonitorTarget> VariableMonitor { get; set; } = new List<MonitorTarget>();
    }
}