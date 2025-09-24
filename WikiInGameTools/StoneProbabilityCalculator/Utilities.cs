using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;

namespace StoneProbabilityCalculator;

public static class Utilities
{
    /// <summary>
    /// 获取当前计算机线程数。
    /// </summary>
    private static readonly int MaxDegree = Environment.ProcessorCount;

    /// <summary>
    /// 以并行方式对集合中的每个元素执行指定操作，最大线程数基于处理器线程数。
    /// 若任意元素操作的退出值为 99 或 -1，则停止整个操作并记录错误。
    /// </summary>
    /// <param name="items">需要并行处理的元素集合</param>
    /// <param name="action">元素的操作函数</param>
    public static void ParallelRun(IEnumerable<CalcThread> items, Func<CalcThread, string> action)
    {
        Parallel.ForEach(
            items,
            new ParallelOptions { MaxDegreeOfParallelism = MaxDegree },
            item =>
            {
                var json = action(item);
                File.WriteAllText($"{item.MineLevel},{item.AverageDailyLuck},{item.AdditionalDifficulty}.json", json);
            }
        );
    }
}