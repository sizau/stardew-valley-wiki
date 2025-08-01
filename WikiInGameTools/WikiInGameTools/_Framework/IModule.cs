﻿using WikiInGameTools._Framework.ConfigurationService;

namespace WikiInGameTools._Framework;

internal interface IModule
{
    /// <summary>
    /// 模块启用状态。
    /// </summary>
    public bool IsActive { get; }

    /// <summary>
    /// 模块配置
    /// </summary>
    public IConfig Config { get; }

    /// <summary>
    /// 启用模块时的操作。
    /// </summary>
    public void Activate();

    /// <summary>
    /// 禁用模块时的操作。
    /// </summary>
    public void Deactivate();
}