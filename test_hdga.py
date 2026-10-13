from data_generator import (
    generate_machines,
    generate_jobs
)

from dispatching import schedule_fifo_edd

from objectives import (
    evaluate_schedule,
    calculate_objective
)

from hdga import run_hdga


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

# FIFO + EDD
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

# HDGA
best_chromosome, hdga_schedule, hdga_objective = (
    run_hdga(
        jobs=jobs,
        machines=machines,
        population_size=50,
        generations=100,
        mutation_rate=0.2,
        local_search_interval=10,
        seed=42
    )
)

hdga_metrics = evaluate_schedule(
    jobs,
    hdga_schedule
)

print("HDGA 執行完成")
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

print("\nHDGA")
print(
    f"目標值：{hdga_objective:.2f}"
)
print(
    f"Makespan："
    f"{hdga_metrics['makespan']:.2f}"
)
print(
    f"設定時間："
    f"{hdga_metrics['total_setup_time']:.2f}"
)
print(
    f"逾期批次："
    f"{hdga_metrics['tardy_batches']}"
)

print("\nHDGA 前 10 個批次順序：")

for job in best_chromosome["sequence"][:10]:
    print(job.job_id, end=" ")

print()