using System;
using System.Collections.Generic;

namespace StoneProbabilityCalculator;

/// <summary>Provides utility extension methods on framework types.</summary>
public static class Extensions
{
    public static void IncrementValue<TKey>(this Dictionary<TKey, int> dict, TKey key, int amount=1) 
    {
        if (dict.TryGetValue(key, out int value)) dict[key] = value + amount;
        else dict[key] = amount;
    }

    public static string ID2Name(this string id)
    {
        return id switch
        {
            "2" => "Diamond Stone",
            "4" => "Ruby Stone",
            "6" => "Jade Stone",
            "8" => "Amethyst Stone",
            "10" => "Topaz Stone",
            "12" => "Emerald Stone",
            "14" => "Aquamarine Stone",
            "44" => "Gem Stone",	
            "46" => "Mystic Stone",
            "751" => "Copper Stone",
            "849" => "Copper Stone",
            "290" => "Iron Stone",
            "764" => "Gold Stone",	
            "765" => "Iridium Stone",
            "95" => "Radioactive Stone",
            _ => $"Stone{id}"
        };
    }

    /// <summary>Randomly choose one of the given options.</summary>
    /// <typeparam name="T">The option type.</typeparam>
    /// <param name="random">The random instance with which to check.</param>
    /// <param name="optionA">The first option, which has a 50% chance of being selected.</param>
    /// <param name="optionB">The second option, which has a 50% chance of being selected.</param>
    public static T Choose<T>(this Random random, T optionA, T optionB)
    {
        if (!(random.NextDouble() < 0.5)) return optionB;
        return optionA;
    }

    /// <summary>Randomly choose one of the given options.</summary>
    /// <typeparam name="T">The option type.</typeparam>
    /// <param name="random">The random instance with which to check.</param>
    /// <param name="optionA">The first option, which has a 33.3% chance of being selected.</param>
    /// <param name="optionB">The second option, which has a 33.3% chance of being selected.</param>
    /// <param name="optionC">The third option, which has a 33.3% chance of being selected.</param>
    public static T Choose<T>(this Random random, T optionA, T optionB, T optionC) =>
        random.Next(3) switch
        {
            0 => optionA,
            1 => optionB,
            _ => optionC
        };

    /// <summary>Randomly choose one of the given options.</summary>
    /// <typeparam name="T">The option type.</typeparam>
    /// <param name="random">The random instance with which to check.</param>
    /// <param name="optionA">The first option, which has a 25% chance of being selected.</param>
    /// <param name="optionB">The second option, which has a 25% chance of being selected.</param>
    /// <param name="optionC">The third option, which has a 25% chance of being selected.</param>
    /// <param name="optionD">The fourth option, which has a 25% chance of being selected.</param>
    public static T Choose<T>(this Random random, T optionA, T optionB, T optionC, T optionD) =>
        random.Next(4) switch
        {
            0 => optionA,
            1 => optionB,
            2 => optionC,
            _ => optionD
        };

    /// <summary>Get a random boolean value (i.e., a 50% chance).</summary>
    /// <param name="random">The random instance with which to check.</param>
    public static bool NextBool(this Random random) => random.NextDouble() < 0.5;

    /// <summary>Get a random boolean value with a weighted chance.</summary>
    /// <param name="random">The random instance with which to check.</param>
    /// <param name="chance">The probability of returning true, as a value between 0 (never) and 1 (always).</param>
    public static bool NextBool(this Random random, double chance)
    {
        if (!(chance >= 1.0)) return random.NextDouble() < chance;
        return true;
    }
}