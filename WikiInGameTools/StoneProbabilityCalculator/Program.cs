using System.Collections.Generic;

namespace StoneProbabilityCalculator;

public static class Program
{
    private static readonly List<CalcThread> Threads = new ();

    public static void Main()
    {
        int[] mineLevels = { 20, 40, 60, 80, 100, 120 };
        // int[] mineLevels = { 121, 220, 320, 520 };
        // int[] mineLevels = { 920, 1720, 3320 };
        double[] dailyLucks = { -0.1, 0.125 };
        
        foreach (var mineLevel in mineLevels)
        foreach (var dailyLuck in dailyLucks)
        {
            Threads.Add(new CalcThread(dailyLuck, mineLevel, 0, 10));
            Threads.Add(new CalcThread(dailyLuck, mineLevel, 0, 10, 1));
            Threads.Add(new CalcThread(dailyLuck, mineLevel, 0, 10, 2));
        }

        Utilities.ParallelRun(Threads, t => t.Run(50));
    }
}