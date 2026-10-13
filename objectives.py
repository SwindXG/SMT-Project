def evaluate_schedule(jobs, schedule):
    """
    計算一份排程的主要績效指標。
    """

    # 建立 job_id 對應 Job 的字典
    job_dict = {
        job.job_id: job
        for job in jobs
    }

    # 建立 job_id 對應完成時間的字典
    completion_times = {
        item.job_id: item.completion_time
        for item in schedule
    }

    # 確認每個批次都有排程結果
    missing_jobs = set(job_dict.keys()) - set(
        completion_times.keys()
    )

    if len(missing_jobs) > 0:
        raise ValueError(
            f"以下批次沒有排程結果：{missing_jobs}"
        )

    # 1. Makespan
    makespan = max(
        item.completion_time
        for item in schedule
    )

    # 2. 總設定時間
    total_setup_time = sum(
        item.setup_time
        for item in schedule
    )

    # 3. 每個批次的逾期時間
    tardiness = {}

    for job in jobs:
        completion_time = completion_times[job.job_id]

        tardiness[job.job_id] = max(
            completion_time - job.due_date,
            0
        )

    # 4. 逾期批次數量
    tardy_batches = sum(
        value > 0
        for value in tardiness.values()
    )

    # 5. 總逾期時間
    total_tardiness = sum(
        tardiness.values()
    )

    # 6. 加權總完工時間
    weighted_completion_time = sum(
        job.priority
        * completion_times[job.job_id]
        for job in jobs
    )

    return {
        "makespan": makespan,
        "total_setup_time": total_setup_time,
        "tardy_batches": tardy_batches,
        "total_tardiness": total_tardiness,
        "weighted_completion_time": (
            weighted_completion_time
        )
    }


def calculate_objective(
    jobs,
    schedule,
    alpha=1.0,
    beta=10.0,
    gamma=10.0
):
    """
    計算後續 GA 可以使用的單一目標值。

    目標值越小越好。
    """

    metrics = evaluate_schedule(
        jobs,
        schedule
    )

    objective_value = (
        alpha
        * metrics["weighted_completion_time"]
        + beta
        * metrics["total_setup_time"]
        + gamma
        * metrics["total_tardiness"]
    )

    return objective_value