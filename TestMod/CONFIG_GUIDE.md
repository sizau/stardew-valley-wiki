# TestMod 变量监控器 `config.json` 使用指南

本功能允许您通过编辑 `config.json` 文件，在游戏运行时动态监控特定方法中的变量值，并将结果输出到 SMAPI 控制台。这对于 Mod 开发、调试或深入了解游戏机制非常有用。

## 文件结构

`config.json` 文件包含一个名为 `VariableMonitor` 的数组。数组中的每一个对象都代表一个独立的监控任务。

当您首次运行本 Mod 时，会在 Mod 文件夹下自动生成一个空的配置文件，如下所示。您需要手动在 `[]` 中添加您想要监控的目标对象。

```json
{
  "VariableMonitor": []
}
```

## 监控对象参数详解

每个监控对象都由以下 4 个参数组成，请确保每个参数都正确填写。

---

### 1. `Enabled`

- **类型**: `布尔值` (true / false)
- **作用**: 控制此条监控规则是否生效。
- **`true`**: Mod 会尝试为这个目标应用监控补丁。
- **`false`**: Mod 会完全忽略这个目标。这对于临时禁用某个监控任务非常方便，而无需删除整段配置。

---

### 2. `FullMethodName`

- **类型**: `字符串`
- **作用**: 指定您想“进入”并监控其中变量的那个方法的**完整路径**。
- **格式**: `"命名空间.类名:方法名"`。
  - **关键**: 请务必使用**冒号（`:`）**来分隔类名和方法名。
- **如何查找**: 使用 dnSpy 或 ILSpy 等 C#反编译工具打开 `StardewValley.dll`，在程序集浏览器中找到目标方法，其完整路径通常会显示出来。此方法对私有方法同样有效。

**示例**:

- `"StardewValley.Tools.FishingRod:DoFunction"`
- `"StardewValley.GameLocation:getFish"`

---

### 3. `Strategy`

- **类型**: `字符串`
- **作用**: 告诉监控器使用哪种策略来获取变量的值。不同的变量类型和监控时机需要不同的策略。
- **可选值**:
  - `"InstanceField"`: 用于监控一个**实例的字段或属性**。补丁会在指定方法执行**完毕后**运行，并从该方法的对象实例（`this`）上读取变量值。这是最常用、最稳定的策略之一。
  - `"ReturnValue"`: 用于监控指定方法的**返回值**。补丁会在方法执行**完毕后**运行，并捕获其返回的对象或值。
  - `"LocalVariable"`: 用于监控方法内部的**局部变量**。由于局部变量在方法结束后即被销毁，此策略会使用高级的`Transpiler`技术在方法执行**中途**注入代码来读取变量值。这非常强大，但请确保 `VariablePath` 的格式正确。

---

### 4. `VariablePath`

- **类型**: `字符串`
- **作用**: 指定要监控的变量名或其深层嵌套的属性/字段路径。
- **格式**: 使用**点（`.`）**来分隔路径。
- **用法**:
  - 当 `Strategy` 是 `"InstanceField"` 时:
    - `"fieldName"`: 读取实例上的 `fieldName` 字段。
    - `"Property.NestedField"`: 读取实例上 `Property` 属性的值，然后再读取该值对象的 `NestedField` 字段。
  - 当 `Strategy` 是 `"ReturnValue"` 时:
    - `""` (空字符串): 监控返回值本身。
    - `"scale.X"`: 监控返回值的 `scale` 字段，然后再读取 `scale` 对象的 `X` 字段。
  - 当 `Strategy` 是 `"LocalVariable"` 时:
    - 格式必须为 `"variableName.FieldName"`，例如 `"r.Width"`。
    - `variableName` 目前仅作为提示，框架会通过硬编码的类型（当前为`Rectangle`）来智能定位局部变量。`FieldName` 则是要访问的字段名。

## 完整示例

以下是一个配置了三个监控任务的完整 `config.json` 文件示例：

```json
{
  "VariableMonitor": [
    {
      "Enabled": true,
      "FullMethodName": "StardewValley.Tools.FishingRod:DoFunction",
      "Strategy": "InstanceField",
      "VariablePath": "clearWaterDistance"
    },
    {
      "Enabled": true,
      "FullMethodName": "StardewValley.Tools.FishingRod:distanceToLand",
      "Strategy": "LocalVariable",
      "VariablePath": "r.Width"
    },
    {
      "Enabled": true,
      "FullMethodName": "StardewValley.GameLocation:getFish",
      "Strategy": "ReturnValue",
      "VariablePath": "scale.X"
    }
  ]
}
```

### 示例解释:

1.  **第一个任务 (InstanceField)**: 在 `DoFunction` 方法执行完毕后，监控 `FishingRod` 实例的 `clearWaterDistance` 字段。
2.  **第二个任务 (LocalVariable)**: 在 `distanceToLand` 方法执行过程中，实时监控其内部名为 `r` 的 `Rectangle` 局部变量的 `Width` 字段。
3.  **第三个任务 (ReturnValue)**: 在 `getFish` 方法返回一个值后，监控这个返回对象的 `scale.X` 字段。

**重要提示**: 所有监控日志的级别均为 `DEBUG`。请确保您的 SMAPI 控制台配置允许显示 `DEBUG` 级别的消息，才能看到变量值的输出。所有日志都将通过 SMAPI 的标准日志系统输出，并会被记录在 `SMAPI-latest.log` 文件中。
