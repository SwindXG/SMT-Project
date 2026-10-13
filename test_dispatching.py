from data_generator import (
    generate_machines,
    generate_jobs
)

from dispatching import schedule_fifo_edd


machines = generate_machines(
    number_of_machines=5,
    seed=42
)

jobs = generate_jobs(
    number_of_jobs=20,
    machines=machines,
    seed=42
)

schedule = schedule_fifo_edd(
    jobs,
    machines
)

print("FIFO + EDD 排程完成")
print(f"批次數量：{len(jobs)}")
print(f"排程項目數量：{len(schedule)}")

print("\n前 5 個排程結果：")

for item in schedule[:5]:
    print(
        f"批次 {item.job_id} | "
        f"機台 {item.machine_id} | "
        f"開始 {item.start_time:.2f} | "
        f"完成 {item.completion_time:.2f} | "
        f"設定 {item.setup_time:.2f}"
    )

makespan = max(
    item.completion_time
    for item in schedule
)

total_setup_time = sum(
    item.setup_time
    for item in schedule
)

print("\n排程統計")
print(f"Makespan：{makespan:.2f} 小時")
print(f"總設定時間：{total_setup_time:.2f} 小時")