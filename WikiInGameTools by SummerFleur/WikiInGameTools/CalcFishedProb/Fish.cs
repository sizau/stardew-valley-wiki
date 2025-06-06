using System;

namespace WikiInGameTools.CalcFishedProb;

[Serializable]
internal class Fish
{
    public string ID { get; set; }
    public int Precedence { get; set; }
    public double SurvivalProb { get; set; }
    public double HookProb { get; set; }
    
    public Fish() { }
    
    public Fish(string id, int precedence, double survivalProb, double hookProb)
    {
        ID = id;
        Precedence = precedence;
        SurvivalProb = survivalProb;
        HookProb = hookProb;
    }
}