from models import Job, Machine, ScheduleItem


# 不同元件類型切換時，假設需要 1 小時設定時間
SETUP_TIME = 1.0


def fifo_edd_order(jobs):
    """
    使用 FIFO + EDD 排序批次。

    第一優先：到達時間較早
    第二優先：到期日較早
    第三優先：優先級較高
    第四優先：批次編號較小
    """

    sorted_jobs = sorted(
        jobs,
        key=lambda job: (
            job.arrival_time,
            job.due_date,
            -job.priority,
            job.job_id
        )
    )

    return sorted_jobs


def schedule_fifo_edd(jobs, machines):
    """
    使用 FIFO + EDD 產生排程。
    """

    # 每台機台目前可使用的時間
    available_time = {
        machine.machine_id: 0.0
        for machine in machines
    }

    # 每台機台上一個加工的元件類型
    previous_device_type = {
        machine.machine_id: ""
        for machine in machines
    }

    schedule = []

    ordered_jobs = fifo_edd_order(jobs)

    for job in ordered_jobs:

        # 找出可以處理此批次的機台
        eligible_machines = [
            machine
            for machine in machines
            if machine.machine_id in job.eligible_machines
        ]

        if len(eligible_machines) == 0:
            raise ValueError(
                f"{job.job_id} 沒有可用的合格機台"
            )

        candidates = []

        for machine in eligible_machines:
            machine_id = machine.machine_id

            # 如果前一個元件類型不同，需要設定時間
            if previous_device_type[machine_id] == "":
                setup_time = 0.0
            elif previous_device_type[machine_id] == job.device_type:
                setup_time = 0.0
            else:
                setup_time = SETUP_TIME

            start_time = max(
                job.arrival_time,
                available_time[machine_id]
            ) + setup_time

            completion_time = (
                start_time + job.processing_time
            )

            candidates.append({
                "machine_id": machine_id,
                "start_time": start_time,
                "completion_time": completion_time,
                "setup_time": setup_time
            })

        # 選擇預計完成時間最早的機台
        selected = min(
            candidates,
            key=lambda candidate: (
                candidate["completion_time"],
                candidate["start_time"],
                candidate["machine_id"]
            )
        )

        machine_id = selected["machine_id"]

        # 更新該機台狀態
        available_time[machine_id] = (
            selected["completion_time"]
        )

        previous_device_type[machine_id] = (
            job.device_type
        )

        # 儲存排程結果
        schedule_item = ScheduleItem(
            job_id=job.job_id,
            machine_id=machine_id,
            start_time=round(
                selected["start_time"],
                2
            ),
            completion_time=round(
                selected["completion_time"],
                2
            ),
            setup_time=round(
                selected["setup_time"],
                2
            )
        )

        schedule.append(schedule_item)

    return schedule