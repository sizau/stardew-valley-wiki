import math


def growth_days(grow_chance: float, simulate_time: int = 100) -> None:
    accu_chance = 0.0
    avg_days = 0.0
    for i in range(4, simulate_time):
        comb_num = math.comb(i, 4)
        chance = comb_num * (grow_chance ** 5) * ((1 - grow_chance) ** (i - 4))
        accu_chance += chance
        avg_days += chance * (i + 1)
        print(f"树木在 {i + 1} 天内成熟的几率为 {chance:.02%}，累积概率为 {accu_chance:.02%}")

    print(f"平均天数为 {avg_days:.02f}")


if __name__ == "__main__":
    growth_days(grow_chance=0.2, simulate_time=100)
