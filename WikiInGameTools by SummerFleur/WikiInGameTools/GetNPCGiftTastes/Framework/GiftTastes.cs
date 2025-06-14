using System.Collections.Generic;

namespace WikiIngameTools.GetNPCGiftTastes.Framework;

internal readonly struct GiftTastes
{
    /// <summary>
    /// 最爱该物品的 NPC，或 NPC 最爱的物品列表
    /// </summary>
    public List<string> LoveThis { get; }
    
    /// <summary>
    /// 喜欢该物品的 NPC，或 NPC 喜欢的物品列表
    /// </summary>
    public List<string> LikeThis { get; }
    
    /// <summary>
    /// 对该物品态度中立的 NPC，或 NPC 态度中立的物品列表
    /// </summary>
    public List<string> NeutralThis { get; }
    
    /// <summary>
    /// 不喜欢该物品的 NPC，或 NPC 不喜欢的物品列表
    /// </summary>
    public List<string> DislikeThis { get; }
    
    /// <summary>
    /// 讨厌该物品的 NPC，或 NPC 讨厌的物品列表
    /// </summary>
    public List<string> HateThis { get; }

    public GiftTastes()
    {
        LoveThis = new List<string>();
        LikeThis = new List<string>();
        NeutralThis = new List<string>();
        DislikeThis= new List<string>();
        HateThis = new List<string>();
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
}