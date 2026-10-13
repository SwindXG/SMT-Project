from data_generator import (
    generate_machines,
    generate_jobs
)

from dispatching import schedule_fifo_edd

from objectives import (
    evaluate_schedule,
    calculate_objective
)


# 產生機台
machines = generate_machines(
    number_of_machines=5,
    seed=42
)

# 產生批次
jobs = generate_jobs(
    number_of_jobs=20,
    machines=machines,
    seed=42
)

# 執行 FIFO + EDD
schedule = schedule_fifo_edd(
    jobs,
    machines
)

# 計算指標
metrics = evaluate_schedule(
    jobs,
    schedule
)

# 計算綜合目標值
objective = calculate_objective(
    jobs,
    schedule
)

print("排程評估完成")
print("--------------------")
print(
    f"Makespan："
    f"{metrics['makespan']:.2f} 小時"
)
print(
    f"總設定時間："
    f"{metrics['total_setup_time']:.2f} 小時"
)
print(
    f"逾期批次數量："
    f"{metrics['tardy_batches']} 批"
)
print(
    f"總逾期時間："
    f"{metrics['total_tardiness']:.2f} 小時"
)
print(
    f"加權總完工時間："
    f"{metrics['weighted_completion_time']:.2f}"
)
print(
    f"綜合目標值："
    f"{objective:.2f}"
)