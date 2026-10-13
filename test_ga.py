from data_generator import (
    generate_machines,
    generate_jobs
)

from dispatching import schedule_fifo_edd

from objectives import (
    evaluate_schedule,
    calculate_objective
)

from genetic_algorithm import run_basic_ga


# 建立機台
machines = generate_machines(
    number_of_machines=5,
    seed=42
)

# 建立批次
jobs = generate_jobs(
    number_of_jobs=20,
    machines=machines,
    seed=42
)

# 先執行 FIFO + EDD
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

# 執行基本 GA
best_chromosome, ga_schedule, ga_objective = run_basic_ga(
    jobs=jobs,
    machines=machines,
    population_size=30,
    generations=50,
    mutation_rate=0.2,
    seed=42
)

ga_metrics = evaluate_schedule(
    jobs,
    ga_schedule
)

print("基本 GA 執行完成")
print("--------------------")

print("FIFO + EDD")
print(
    f"目標值：{fifo_objective:.2f}"
)
print(
    f"Makespan："
    f"{fifo_metrics['makespan']:.2f}"
)
print(
    f"設定時間："
    f"{fifo_metrics['total_setup_time']:.2f}"
)
print(
    f"逾期批次："
    f"{fifo_metrics['tardy_batches']}"
)

print("\n基本 GA")
print(
    f"目標值：{ga_objective:.2f}"
)
print(
    f"Makespan："
    f"{ga_metrics['makespan']:.2f}"
)
print(
    f"設定時間："
    f"{ga_metrics['total_setup_time']:.2f}"
)
print(
    f"逾期批次："
    f"{ga_metrics['tardy_batches']}"
)

print("\nGA 最佳批次順序：")

for job in best_chromosome[:10]:
    print(job.job_id, end=" ")

print()