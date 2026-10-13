import random
import csv
from pathlib import Path

from models import Job, Machine, FailureEvent


DEVICE_TYPES = ["A", "B", "C"]


def generate_machines(
    number_of_machines=5,
    seed=42
):
    """
    建立 SMT 機台資料。
    """

    random.seed(seed)

    machines = []

    for index in range(number_of_machines):
        machine_id = f"M{index + 1:02d}"

        supported_types = []

        for device_type in DEVICE_TYPES:
            # 75% 機率支援某種元件類型
            if random.random() < 0.75:
                supported_types.append(device_type)

        # 確保每台機台至少支援一種元件
        if len(supported_types) == 0:
            supported_types.append(random.choice(DEVICE_TYPES))

        machine = Machine(
            machine_id=machine_id,
            machine_type=f"SMT-{(index % 2) + 1}",
            supported_device_types=supported_types,
            machine_priority=round(
                random.uniform(0.8, 1.2),
                2
            )
        )

        machines.append(machine)

    # 確保 A、B、C 三種元件都有至少一台機台可以處理
    for device_type in DEVICE_TYPES:
        supported_machine_exists = any(
            device_type in machine.supported_device_types
            for machine in machines
        )

        if not supported_machine_exists:
            machines[0].supported_device_types.append(device_type)

    return machines


def generate_jobs(
    number_of_jobs=20,
    machines=None,
    seed=42
):
    """
    建立批次資料。
    """

    if machines is None:
        machines = generate_machines(seed=seed)

    random.seed(seed + 1)

    jobs = []

    for index in range(number_of_jobs):
        device_type = random.choice(DEVICE_TYPES)

        eligible_machines = [
            machine.machine_id
            for machine in machines
            if device_type in machine.supported_device_types
        ]

        arrival_time = round(
            random.uniform(0, 72),
            2
        )

        processing_time = round(
            random.uniform(1, 8),
            2
        )

        priority = random.randint(1, 5)

        # 優先級越高，這裡讓交期稍微緊一些
        due_date = round(
            arrival_time
            + processing_time
            + random.uniform(12, 36) / priority,
            2
        )

        job = Job(
            job_id=f"J{index + 1:04d}",
            issue_no=f"I{(index // 3) + 1:04d}",
            device_type=device_type,
            arrival_time=arrival_time,
            due_date=due_date,
            processing_time=processing_time,
            priority=priority,
            eligible_machines=eligible_machines
        )

        jobs.append(job)

    # 依照到達時間排序
    jobs.sort(
        key=lambda job: (
            job.arrival_time,
            job.job_id
        )
    )

    return jobs


def generate_failures(
    machines,
    horizon=160,
    mtbf=40,
    mttr=4,
    seed=42
):
    """
    使用指數分佈產生隨機機台故障。
    """

    random.seed(seed + 2)

    failure_events = []

    for machine in machines:
        current_time = 0.0

        while True:
            # 產生下一次故障時間
            time_to_failure = random.expovariate(
                1 / mtbf
            )

            current_time += time_to_failure

            if current_time >= horizon:
                break

            repair_time = random.expovariate(
                1 / mttr
            )

            failure_event = FailureEvent(
                machine_id=machine.machine_id,
                failure_time=round(current_time, 2),
                repair_time=round(repair_time, 2),
                repair_end_time=round(
                    current_time + repair_time,
                    2
                )
            )

            failure_events.append(failure_event)

            # 修復期間不再計算新的故障
            current_time += repair_time

    failure_events.sort(
        key=lambda event: event.failure_time
    )

    return failure_events


def save_jobs_to_csv(jobs, file_path):
    """
    將批次資料輸出成 CSV。
    """

    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.writer(file)

        writer.writerow([
            "job_id",
            "issue_no",
            "device_type",
            "arrival_time",
            "due_date",
            "processing_time",
            "priority",
            "eligible_machines"
        ])

        for job in jobs:
            writer.writerow([
                job.job_id,
                job.issue_no,
                job.device_type,
                job.arrival_time,
                job.due_date,
                job.processing_time,
                job.priority,
                ";".join(job.eligible_machines)
            ])


def save_machines_to_csv(machines, file_path):
    """
    將機台資料輸出成 CSV。
    """

    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.writer(file)

        writer.writerow([
            "machine_id",
            "machine_type",
            "supported_device_types",
            "machine_priority"
        ])

        for machine in machines:
            writer.writerow([
                machine.machine_id,
                machine.machine_type,
                ";".join(machine.supported_device_types),
                machine.machine_priority
            ])


def save_failures_to_csv(failures, file_path):
    """
    將故障資料輸出成 CSV。
    """

    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.writer(file)

        writer.writerow([
            "machine_id",
            "failure_time",
            "repair_time",
            "repair_end_time"
        ])

        for event in failures:
            writer.writerow([
                event.machine_id,
                event.failure_time,
                event.repair_time,
                event.repair_end_time
            ])


def generate_dataset(output_folder="data"):
    """
    一次產生所有資料並輸出成 CSV。
    """

    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True)

    machines = generate_machines(
        number_of_machines=5,
        seed=42
    )

    jobs = generate_jobs(
        number_of_jobs=20,
        machines=machines,
        seed=42
    )

    failures = generate_failures(
        machines=machines,
        horizon=160,
        mtbf=40,
        mttr=4,
        seed=42
    )

    save_jobs_to_csv(
        jobs,
        output_path / "jobs.csv"
    )

    save_machines_to_csv(
        machines,
        output_path / "machines.csv"
    )

    save_failures_to_csv(
        failures,
        output_path / "failures.csv"
    )

    return jobs, machines, failures


if __name__ == "__main__":
    jobs, machines, failures = generate_dataset()

    print("資料生成完成")
    print(f"批次數量：{len(jobs)}")
    print(f"機台數量：{len(machines)}")
    print(f"故障事件數量：{len(failures)}")
    print("資料已儲存至 data 資料夾")