namespace TestMod.Config
{
    /// <summary>代表在config.json中定义的单个变量监控目标。</summary>
    public class MonitorTarget
    {
        // ... 其他属性不变 ...
        public bool Enabled { get; set; } = true;
        public string FullMethodName { get; set; }
        public TargetStrategy Strategy { get; set; }

        /// <summary>
        /// 要监控的变量名或路径。
        /// 对于InstanceField: "fieldName" 或 "field.nestedField"
        /// 对于ReturnValue: "" (监控返回值本身) 或 "field.nestedField" (监控返回值的属性)
        /// 对于LocalVariable: "variableName.FieldName"，例如 "r.Width"。
        /// </summary>
        public string VariablePath { get; set; }
    }

    /// <summary>定义了用于查找要监控变量的不同策略。</summary>
    public enum TargetStrategy
    {
        /// <summary>监控一个实例的字段或属性（在方法执行后）。</summary>
        InstanceField,

        /// <summary>监控方法的返回值或其属性（在方法执行后）。</summary>
        ReturnValue,

        /// <summary>监控一个局部变量的字段/属性（需要Transpiler）。</summary>
        LocalVariable
    }
}