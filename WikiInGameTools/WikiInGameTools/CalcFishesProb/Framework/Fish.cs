using System;

namespace WikiIngameTools.CalcFishesProb.Framework;

[Serializable]
internal class Fish
{
    public string ID { get; }
    public int Precedence { get; }
    public double SurvivalProb { get; }
    public double HookProb { get; }
    
    public Fish() { }

    public Fish(string id, int precedence, double survivalProb, double hookProb)
    {
        ID = id;
        Precedence = precedence;
        SurvivalProb = survivalProb;
        HookProb = hookProb;
    }

    public override bool Equals(object obj)
    {
        if (obj == null || GetType() != obj.GetType())
            return false;

        var other = (Fish)obj;
        return ID == other.ID &&
               Precedence == other.Precedence &&
               SurvivalProb.ToString("F10") == other.SurvivalProb.ToString("F10") &&
               HookProb.ToString("F10") == other.HookProb.ToString("F10");
    }

    public override int GetHashCode()
    {
        var hash = 17;
        hash = hash * 23 + (ID?.GetHashCode() ?? 0);
        hash = hash * 23 + Precedence.GetHashCode();
        hash = hash * 23 + SurvivalProb.GetHashCode();
        hash = hash * 23 + HookProb.GetHashCode();
        return hash;
    }
}