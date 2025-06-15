using System.Collections.Generic;
using System.Text;
using WikiIngameTools.Framework;

namespace WikiIngameTools.GetNPCGiftTastes.Framework;

internal struct GiftTastes
{
    /// <summary>
    /// 最爱该物品的 NPC，或 NPC 最爱的物品列表
    /// </summary>
    private List<string> LoveThis { get; } = new ();

    /// <summary>
    /// 喜欢该物品的 NPC，或 NPC 喜欢的物品列表
    /// </summary>
    private List<string> LikeThis { get; } = new ();

    /// <summary>
    /// 对该物品态度中立的 NPC，或 NPC 态度中立的物品列表
    /// </summary>
    private List<string> NeutralThis { get; } = new ();

    /// <summary>
    /// 不喜欢该物品的 NPC，或 NPC 不喜欢的物品列表
    /// </summary>
    private List<string> DislikeThis { get; } = new ();

    /// <summary>
    /// 讨厌该物品的 NPC，或 NPC 讨厌的物品列表
    /// </summary>
    private List<string> HateThis { get; } = new ();

    /// <summary>
    /// 解析状态
    /// </summary>
    /// <value>
    /// <list type="table">
    ///   <item><term>Normal</term><description>正常物品</description></item>
    ///   <item><term>Null</term><description>空物品</description></item>
    ///   <item><term>Blacklisted</term><description>非常规物品</description></item>
    /// </list>
    /// </value>
    public Status Status { get; set; }

    public GiftTastes(Status status)
    {
        Status = status;
    }

    /// <summary>
    /// 向结构中加入物品
    /// </summary>
    /// <param name="name">NPC 的名字或物品的名字，英文</param>
    /// <param name="taste">NPC 对该物品的态度</param>
    public void Add(string name, string taste)
    {
        switch (taste)
        {
            case "Love":
                LoveThis.Add(name);
                break;
            case "Like":
                LikeThis.Add(name);
                break;
            case "Neutral":
                NeutralThis.Add(name);
                break;
            case "Dislike":
                DislikeThis.Add(name);
                break;
            case "Hate":
                HateThis.Add(name);
                break;
        }
    }

    /// <summary>
    /// 按字母顺序排序各个属性。
    /// </summary>
    public void Organize()
    {
        LoveThis.Sort();
        LikeThis.Sort();
        NeutralThis.Sort();
        DislikeThis.Sort();
        HateThis.Sort();
    }

    public override string ToString()
    {        
        var sb = new StringBuilder();
        sb.AppendLine($"|love={LoveThis.Tostring()}");
        sb.AppendLine($"|like={LikeThis.Tostring()}");
        sb.AppendLine($"|neutral={NeutralThis.Tostring()}");
        sb.AppendLine($"|dislike={DislikeThis.Tostring()}");
        sb.AppendLine($"|hate={HateThis.Tostring()}");

        return sb.ToString();
    }
}

internal enum Status
{
    Normal,
    Blacklisted,
    Null
}