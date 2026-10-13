import statistics

from data_generator import (
    generate_machines,
    generate_jobs
)

from dispatching import (
    schedule_fifo_edd
)

from objectives import (
    evaluate_schedule,
    calculate_objective
)

from genetic_algorithm import (
    run_basic_ga
)

from hdga import (
    run_hdga
)


def run_one_experiment(seed):
    """
    使用同一個 seed，
    同時測試 FIFO + EDD、基本 GA、HDGA。
    """

    # -----------------------------
    # 建立同一份測試資料
    # -----------------------------
    machines = generate_machines(
        number_of_machines=5,
        seed=seed
    )

    jobs = generate_jobs(
        number_of_jobs=20,
        machines=machines,
        seed=seed
    )

    results = []

    # -----------------------------
    # 方法一：FIFO + EDD
    # -----------------------------
    fifo_schedule = schedule_fifo_edd(
        jobs,
        machines
    )

    fifo_metrics = evaluate_schedule(
        jobs,
        fifo_schedule
    )

    fifo_objective = calculate_objective(
        jobs,
        fifo_schedule
    )

    results.append({
        "method": "FIFO_EDD",
        "objective": fifo_objective,
        "makespan": fifo_metrics["makespan"],
        "setup_time": fifo_metrics[
            "total_setup_time"
        ],
        "tardy_batches": fifo_metrics[
            "tardy_batches"
        ]
    })

    # -----------------------------
    # 方法二：基本 GA
    # -----------------------------
    _, ga_schedule, ga_objective = (
        run_basic_ga(
            jobs=jobs,
            machines=machines,
            population_size=30,
            generations=50,
            mutation_rate=0.2,
            seed=seed
        )
    )

    ga_metrics = evaluate_schedule(
        jobs,
        ga_schedule
    )

    results.append({
        "method": "Basic_GA",
        "objective": ga_objective,
        "makespan": ga_metrics["makespan"],
        "setup_time": ga_metrics[
            "total_setup_time"
        ],
        "tardy_batches": ga_metrics[
            "tardy_batches"
        ]
    })

    # -----------------------------
    # 方法三：HDGA + 局部搜尋
    # -----------------------------
    _, hdga_schedule, hdga_objective = (
        run_hdga(
            jobs=jobs,
            machines=machines,
            population_size=50,
            generations=100,
            mutation_rate=0.2,
            local_search_interval=10,
            seed=seed
        )
    )

    hdga_metrics = evaluate_schedule(
        jobs,
        hdga_schedule
    )

    results.append({
        "method": "HDGA",
        "objective": hdga_objective,
        "makespan": hdga_metrics["makespan"],
        "setup_time": hdga_metrics[
            "total_setup_time"
        ],
        "tardy_batches": hdga_metrics[
            "tardy_batches"
        ]
    })

    return results


def summarize_results(all_results):
    """
    計算每個方法的平均值與標準差。
    """

    methods = [
        "FIFO_EDD",
        "Basic_GA",
        "HDGA"
    ]

    metrics = [
        "objective",
        "makespan",
        "setup_time",
        "tardy_batches"
    ]

    for method in methods:

        method_results = [
            result
            for result in all_results
            if result["method"] == method
        ]

        print("\n" + "=" * 50)
        print(f"方法：{method}")
        print("=" * 50)

        for metric in metrics:

            values = [
                result[metric]
                for result in method_results
            ]

            average = statistics.mean(values)

            if len(values) >= 2:
                standard_deviation = (
                    statistics.stdev(values)
                )
            else:
                standard_deviation = 0.0

            print(
                f"{metric:20s} "
                f"平均={average:.2f} "
                f"標準差={standard_deviation:.2f}"
            )


def main():
    """
    使用 10 組亂數種子進行重複實驗。
    """

    all_results = []

    seeds = range(42, 52)

    for seed in seeds:

        print(
            f"正在執行 seed={seed} ..."
        )

        results = run_one_experiment(
            seed
        )

        all_results.extend(results)

    summarize_results(
        all_results
    )


if __name__ == "__main__":
    main()