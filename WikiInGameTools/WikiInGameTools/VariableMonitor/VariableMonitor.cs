using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using StardewModdingAPI;
using WikiInGameTools._Framework;
using WikiInGameTools._Framework.ConfigurationService;

namespace WikiInGameTools.VariableMonitor;

/// <summary>
/// 负责根据配置动态应用变量监控补丁的类。
/// 所有日志输出均通过SMAPI日志系统。
/// </summary>
internal class VariableMonitor : IModule
{
    // 静态字段，用于在补丁方法中访问上下文
    private static Dictionary<string, MonitorTarget> _configsByMethodKey = new();
    private static MonitorTarget _currentTranspilerTarget;
    private readonly Harmony _harmony = new (ModEntry.Manifest.UniqueID + ".VariableMonitor");
    public bool IsActive { get; private set; }
    public IConfig Config => ModEntry.Config.VariableMonitorConfig;

    public void Activate()
    {
        IsActive = true;
        // 应用变量监控功能
        ApplyFromConfig();
    }

    public void Deactivate()
    {
        IsActive = false;
        _harmony.UnpatchAll(_harmony.Id);
        ModEntry.Log("已取消监控所有变量。", LogLevel.Info);
    }

    /// <summary>
    /// 读取配置并应用所有已启用的监控补丁。
    /// </summary>
    private void ApplyFromConfig()
    {
        // 获取由用户在 Data/MonitorTarget.json 中定义的、需要监控的变量目标列表。
        var variableMonitors = ModEntry.ModHelper.Data
            .ReadJsonFile<List<MonitorTarget>>(Utilities.GetDataFilePath("MonitorTarget.json"));
        if (variableMonitors is null || variableMonitors.Count == 0)
        {
            ModEntry.Log("未能发现任何数据！", LogLevel.Warn);
            return;
        }
        // 应用监控补丁
        foreach (var target in variableMonitors)
        {
            if (!target.Enabled) continue;

            try
            {
                ApplySingleTarget(target);
            }
            catch (Exception ex)
            {
                ModEntry.Log($"为 '{target.VariablePath}' 应用监控补丁时失败: {ex}", LogLevel.Error);
            }
        }
    }

    /// <summary>
    /// 为单个监控目标应用补丁。
    /// </summary>
    private void ApplySingleTarget(MonitorTarget target)
    {
        MethodBase originalMethod = AccessTools.Method(target.FullMethodName);
        if (originalMethod == null)
        {
            ModEntry.Log($"监控器错误: 找不到方法 '{target.FullMethodName}'。", LogLevel.Warn);
            return;
        }

        var methodKey = $"{originalMethod.DeclaringType?.FullName}.{originalMethod.Name}";
        _configsByMethodKey[methodKey] = target;

        var strategyDescription = "";

        switch (target.Strategy)
        {
            case TargetStrategy.InstanceField:
                _harmony.Patch(originalMethod,
                    postfix: new HarmonyMethod(typeof(VariableMonitor), nameof(InstanceFieldPostfix)));
                strategyDescription = "实例变量";
                break;

            case TargetStrategy.ReturnValue:
                _harmony.Patch(originalMethod,
                    postfix: new HarmonyMethod(typeof(VariableMonitor), nameof(ReturnValuePostfix)));
                strategyDescription = "返回值";
                break;

            case TargetStrategy.LocalVariable:
                _currentTranspilerTarget = target;
                _harmony.Patch(originalMethod,
                    transpiler: new HarmonyMethod(typeof(VariableMonitor), nameof(LocalVariableTranspiler)));
                _currentTranspilerTarget = null;
                strategyDescription = "局部变量 (Transpiler)";
                break;
        }

        ModEntry.Log($"已成功监控 {target.FullMethodName} 的 '{target.VariablePath}' {strategyDescription}",
            LogLevel.Info);
    }

    /// <summary>
    /// 【Transpiler】用于监控局部变量。
    /// </summary>
    public static IEnumerable<CodeInstruction> LocalVariableTranspiler(IEnumerable<CodeInstruction> instructions,
        MethodBase __originalMethod, ILGenerator generator)
    {
        var config = _currentTranspilerTarget;
        if (config == null) return instructions;

        string[] pathParts = config.VariablePath.Split('.');
        if (pathParts.Length != 2)
        {
            ModEntry.Log($"局部变量监控错误: VariablePath '{config.VariablePath}' 格式不正确。", LogLevel.Error);
            return instructions;
        }

        var localVariableTypeNameHint = "Rectangle";
        var fieldName = pathParts[1];

        var methodBody = __originalMethod.GetMethodBody();
        if (methodBody == null) return instructions;

        var localVariable = methodBody.LocalVariables
                .FirstOrDefault(v => v.LocalType?.Name == localVariableTypeNameHint);
        if (localVariable == null)
        {
            ModEntry.Log($"监控器警告: 在 '{config.FullMethodName}' 中找不到类型为 '{localVariableTypeNameHint}' 的局部变量。",
                LogLevel.Warn);
            return instructions;
        }

        var varIndex = localVariable.LocalIndex;

        var codes = new List<CodeInstruction>(instructions);
        var patched = false;

        for (var i = 0; i < codes.Count - 1; i++)
        {
            // 手动实现 LoadsLocal() 的逻辑
            var loadsTargetLocal = false;
            var instruction = codes[i];
            if (instruction.opcode == OpCodes.Ldloc || instruction.opcode == OpCodes.Ldloc_S ||
                instruction.opcode == OpCodes.Ldloca || instruction.opcode == OpCodes.Ldloca_S)
            {
                if (instruction.operand is LocalBuilder lb && lb.LocalIndex == varIndex) loadsTargetLocal = true;
                else if (instruction.operand is int index && index == varIndex) loadsTargetLocal = true;
            }
            else if (varIndex == 0 && instruction.opcode == OpCodes.Ldloc_0)
            {
                loadsTargetLocal = true;
            }
            else if (varIndex == 1 && instruction.opcode == OpCodes.Ldloc_1)
            {
                loadsTargetLocal = true;
            }
            else if (varIndex == 2 && instruction.opcode == OpCodes.Ldloc_2)
            {
                loadsTargetLocal = true;
            }
            else if (varIndex == 3 && instruction.opcode == OpCodes.Ldloc_3)
            {
                loadsTargetLocal = true;
            }

            if (loadsTargetLocal)
                if (codes[i + 1].opcode == OpCodes.Ldfld && codes[i + 1].operand is FieldInfo field &&
                    field.Name == fieldName)
                {
                    var logInstructions = new List<CodeInstruction>
                    {
                        new(OpCodes.Dup),
                        // 注入一个统一的标识符
                        new(OpCodes.Ldstr, $"[监控] {config.FullMethodName} -> {config.VariablePath}: "),
                        // 调用统一的SMAPI日志方法
                        new(OpCodes.Call,
                            AccessTools.Method(typeof(VariableMonitor), nameof(LogValueFromTranspiler))
                                .MakeGenericMethod(field.FieldType))
                    };

                    codes.InsertRange(i + 2, logInstructions);
                    patched = true;
                    i += logInstructions.Count;
                }
        }

        if (!patched)
            ModEntry.Log($"监控器警告: 未能在 '{config.FullMethodName}' 中找到对 '{config.VariablePath}' 的访问点。",
                LogLevel.Warn);

        return codes;
    }

    /// <summary>
    /// Postfix补丁，用于监控实例字段。
    /// </summary>
    public static void InstanceFieldPostfix(object __instance, MethodBase __originalMethod)
    {
        if (__instance == null) return;
        var methodKey = $"{__originalMethod.DeclaringType?.FullName}.{__originalMethod.Name}";
        if (_configsByMethodKey.TryGetValue(methodKey, out var config))
        {
            var value = GetValueFromPath(__instance, config.VariablePath);
            LogValue(config, value);
        }
    }

    /// <summary>
    /// Postfix补丁，用于监控返回值。
    /// </summary>
    public static void ReturnValuePostfix(object __result, MethodBase __originalMethod)
    {
        if (__result == null) return;
        var methodKey = $"{__originalMethod.DeclaringType?.FullName}.{__originalMethod.Name}";
        if (_configsByMethodKey.TryGetValue(methodKey, out var config))
        {
            var value = GetValueFromPath(__result, config.VariablePath);
            LogValue(config, value);
        }
    }

    /// <summary>
    /// 通过反射获取一个对象深层嵌套的值。
    /// </summary>
    private static object GetValueFromPath(object root, string path)
    {
        if (root == null) return null;
        if (string.IsNullOrEmpty(path)) return root;
        var current = root;
        var parts = path.Split('.');
        foreach (var part in parts)
        {
            if (current == null) return null;
            var currentType = current.GetType();
            var field = AccessTools.Field(currentType, part);
            if (field != null)
            {
                current = field.GetValue(current);
                continue;
            }

            var property = AccessTools.Property(currentType, part);
            if (property != null)
            {
                current = property.GetValue(current);
                continue;
            }

            ModEntry.Log($"无法在 '{currentType.Name}' 上找到字段或属性 '{part}' (完整路径: '{path}')。", LogLevel.Warn);
            return null;
        }

        return current;
    }

    /// <summary>
    /// 将通过Postfix获取到的变量值格式化并输出到SMAPI控制台。
    /// </summary>
    private static void LogValue(MonitorTarget config, object value)
    {
        var valueStr = value?.ToString() ?? "null";
        ModEntry.Log($"[监控] {config.FullMethodName} -> {config.VariablePath}: {valueStr}");
    }

    /// <summary>
    /// 由Transpiler调用的日志方法，使用SMAPI日志系统。
    /// </summary>
    public static void LogValueFromTranspiler<T>(T value, string identifier)
    {
        var valueStr = value?.ToString() ?? "null";
        // 使用 SMAPI 的日志系统，它会自动添加前缀并处理缓冲
        ModEntry.Log($"{identifier}{valueStr}");
    }
}