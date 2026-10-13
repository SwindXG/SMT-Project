import random

from models import ScheduleItem
from objectives import evaluate_schedule

from dispatching import (
    fifo_edd_order,
    schedule_fifo_edd
)

SETUP_TIME = 1.0

def gene_for_machine(
    job,
    target_machine_id,
    machines
):
    """
    找出一個 machine gene，
    使 choose_machine() 選到指定機台。
    """

    eligible_machines = [
        machine
        for machine in machines
        if machine.machine_id in job.eligible_machines
    ]

    eligible_machines.sort(
        key=lambda machine: machine.machine_id
    )

    total_priority = sum(
        machine.machine_priority
        for machine in eligible_machines
    )

    cumulative = 0.0

    for machine in eligible_machines:

        interval_start = (
            cumulative / total_priority
        )

        cumulative += machine.machine_priority

        interval_end = (
            cumulative / total_priority
        )

        if machine.machine_id == target_machine_id:
            # 取該機台選擇區間的中間值
            return (
                interval_start
                + interval_end
            ) / 2

    raise ValueError(
        f"{job.job_id} 找不到指定機台 "
        f"{target_machine_id}"
    )


def create_baseline_chromosome(
    jobs,
    machines
):
    """
    將 FIFO + EDD 的結果轉換成一個 HDGA 染色體。

    這個染色體會放入初始族群，
    讓 HDGA 一開始至少擁有基準解。
    """

    baseline_schedule = schedule_fifo_edd(
        jobs,
        machines
    )

    assignment = {
        item.job_id: item.machine_id
        for item in baseline_schedule
    }

    machine_genes = {}

    for job in jobs:
        machine_genes[job.job_id] = (
            gene_for_machine(
                job=job,
                target_machine_id=assignment[job.job_id],
                machines=machines
            )
        )

    return {
        "sequence": fifo_edd_order(jobs),
        "machine_genes": machine_genes
    }


def copy_chromosome(chromosome):
    """
    複製一個 HDGA 染色體。
    """

    return {
        "sequence": list(chromosome["sequence"]),
        "machine_genes": dict(
            chromosome["machine_genes"]
        )
    }


def choose_machine(job, machines, gene_value):
    """
    根據 machine gene 選擇機台。

    gene_value 的範圍是 0 到 1。
    機台優先級越高，被選到的區間越大。
    """

    eligible_machines = [
        machine
        for machine in machines
        if machine.machine_id in job.eligible_machines
    ]

    if len(eligible_machines) == 0:
        raise ValueError(
            f"{job.job_id} 沒有合格機台"
        )

    eligible_machines.sort(
        key=lambda machine: machine.machine_id
    )

    total_priority = sum(
        machine.machine_priority
        for machine in eligible_machines
    )

    target = gene_value * total_priority
    cumulative = 0.0

    for machine in eligible_machines:
        cumulative += machine.machine_priority

        if target <= cumulative:
            return machine

    return eligible_machines[-1]


def decode_chromosome(chromosome, machines):
    """
    將 HDGA 染色體轉換成實際排程。

    步驟：
    1. 依 machine gene 分配機台。
    2. 同一台機台內使用 FIFO + EDD 排序。
    3. 計算開始時間、完成時間與設定時間。
    """

    machine_list = list(machines)

    assigned_jobs = {
        machine.machine_id: []
        for machine in machine_list
    }

    sequence_position = {
        job.job_id: position
        for position, job in enumerate(
            chromosome["sequence"]
        )
    }

    # 第一階段：根據基因分配機台
    for job in chromosome["sequence"]:
        gene_value = chromosome["machine_genes"][
            job.job_id
        ]

        selected_machine = choose_machine(
            job,
            machine_list,
            gene_value
        )

        assigned_jobs[
            selected_machine.machine_id
        ].append(job)

    # 第二階段：每台機台內套用 FIFO + EDD
    for machine_id in assigned_jobs:
        assigned_jobs[machine_id].sort(
            key=lambda job: (
                job.arrival_time,
                job.due_date,
                -job.priority,
                sequence_position[job.job_id]
            )
        )

    available_time = {
        machine.machine_id: 0.0
        for machine in machine_list
    }

    previous_device_type = {
        machine.machine_id: ""
        for machine in machine_list
    }

    schedule = []

    # 第三階段：計算每個批次的時間
    for machine in machine_list:
        machine_id = machine.machine_id

        for job in assigned_jobs[machine_id]:

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
                start_time
                + job.processing_time
            )

            schedule.append(
                ScheduleItem(
                    job_id=job.job_id,
                    machine_id=machine_id,
                    start_time=round(
                        start_time,
                        2
                    ),
                    completion_time=round(
                        completion_time,
                        2
                    ),
                    setup_time=round(
                        setup_time,
                        2
                    )
                )
            )

            available_time[machine_id] = (
                completion_time
            )

            previous_device_type[machine_id] = (
                job.device_type
            )

    return schedule


def create_initial_population(
    jobs,
    population_size,
    random_generator
):
    """
    建立 HDGA 初始族群。

    每個個體包含：
    1. sequence：批次排列順序
    2. machine_genes：每個批次的機台選擇基因
    """

    population = []

    for _ in range(population_size):

        sequence = list(jobs)

        random_generator.shuffle(
            sequence
        )

        machine_genes = {
            job.job_id: random_generator.random()
            for job in jobs
        }

        chromosome = {
            "sequence": sequence,
            "machine_genes": machine_genes
        }

        population.append(chromosome)

    return population


def calculate_fitness(
    chromosome,
    machines
):
    """
    計算 HDGA 個體的目標值。
    目標值越小越好。
    """

    schedule = decode_chromosome(
        chromosome,
        machines
    )

    metrics = evaluate_schedule(
        chromosome["sequence"],
        schedule
    )

    objective_value = (
        metrics["weighted_completion_time"]
        + 10 * metrics["total_setup_time"]
        + 10 * metrics["total_tardiness"]
    )

    return objective_value, schedule

def local_search(
    chromosome,
    machines,
    max_rounds=3
):
    """
    對目前染色體進行局部搜尋。

    鄰域包含：
    1. 將某個批次改分配到其他合格機台。
    2. 交換相鄰批次順序。

    只接受能改善目標值的鄰近解。
    """

    current = copy_chromosome(
        chromosome
    )

    current_objective, current_schedule = (
        calculate_fitness(
            current,
            machines
        )
    )

    for _ in range(max_rounds):

        best_candidate = copy_chromosome(
            current
        )

        best_objective = current_objective
        best_schedule = current_schedule

        # -----------------------------
        # 鄰域一：嘗試重新分配機台
        # -----------------------------
        for job in current["sequence"]:

            eligible_machines = [
                machine
                for machine in machines
                if machine.machine_id
                in job.eligible_machines
            ]

            for machine in eligible_machines:

                candidate = copy_chromosome(
                    current
                )

                candidate["machine_genes"][
                    job.job_id
                ] = gene_for_machine(
                    job=job,
                    target_machine_id=machine.machine_id,
                    machines=machines
                )

                candidate_objective, candidate_schedule = (
                    calculate_fitness(
                        candidate,
                        machines
                    )
                )

                if candidate_objective < best_objective:
                    best_candidate = candidate
                    best_objective = (
                        candidate_objective
                    )
                    best_schedule = (
                        candidate_schedule
                    )

        # -----------------------------
        # 鄰域二：交換相鄰批次順序
        # -----------------------------
        for index in range(
            len(current["sequence"]) - 1
        ):

            candidate = copy_chromosome(
                current
            )

            sequence = candidate["sequence"]

            sequence[index], sequence[index + 1] = (
                sequence[index + 1],
                sequence[index]
            )

            candidate_objective, candidate_schedule = (
                calculate_fitness(
                    candidate,
                    machines
                )
            )

            if candidate_objective < best_objective:
                best_candidate = candidate
                best_objective = (
                    candidate_objective
                )
                best_schedule = (
                    candidate_schedule
                )

        # -----------------------------
        # 更新目前解
        # -----------------------------
        if best_objective < current_objective:
            current = best_candidate
            current_objective = best_objective
            current_schedule = best_schedule
        else:
            break

    return (
        current,
        current_schedule,
        current_objective
    )

def tournament_selection(
    population,
    fitness_values,
    random_generator,
    tournament_size=3
):
    """
    使用競賽選擇法選取父代。
    """

    candidate_indices = random_generator.sample(
        range(len(population)),
        min(
            tournament_size,
            len(population)
        )
    )

    best_index = min(
        candidate_indices,
        key=lambda index: fitness_values[index]
    )

    return copy_chromosome(
        population[best_index]
    )


def order_crossover(
    parent_1,
    parent_2,
    random_generator
):
    """
    對 sequence 使用 Order Crossover。
    對 machine genes 使用均勻交叉。
    """

    sequence_1 = parent_1["sequence"]
    sequence_2 = parent_2["sequence"]

    chromosome_length = len(sequence_1)

    left, right = sorted(
        random_generator.sample(
            range(chromosome_length),
            2
        )
    )

    child_sequence = [None] * chromosome_length

    child_sequence[left:right] = (
        sequence_1[left:right]
    )

    remaining_jobs = [
        job
        for job in sequence_2
        if job not in child_sequence
    ]

    remaining_index = 0

    for index in range(chromosome_length):
        if child_sequence[index] is None:
            child_sequence[index] = (
                remaining_jobs[remaining_index]
            )
            remaining_index += 1

    child_machine_genes = {}

    for job in sequence_1:
        if random_generator.random() < 0.5:
            child_machine_genes[job.job_id] = (
                parent_1["machine_genes"][job.job_id]
            )
        else:
            child_machine_genes[job.job_id] = (
                parent_2["machine_genes"][job.job_id]
            )

    return {
        "sequence": child_sequence,
        "machine_genes": child_machine_genes
    }


def mutate_chromosome(
    chromosome,
    mutation_rate,
    random_generator
):
    """
    對批次順序與機台基因進行突變。
    """

    mutated = copy_chromosome(
        chromosome
    )

    sequence = mutated["sequence"]

    # 批次順序交換突變
    if (
        len(sequence) >= 2
        and random_generator.random()
        < mutation_rate
    ):
        index_1, index_2 = random_generator.sample(
            range(len(sequence)),
            2
        )

        sequence[index_1], sequence[index_2] = (
            sequence[index_2],
            sequence[index_1]
        )

    # 機台選擇基因突變
    for job_id in mutated["machine_genes"]:
        if (
            random_generator.random()
            < mutation_rate
        ):
            mutated["machine_genes"][job_id] = (
                random_generator.random()
            )

    return mutated


def run_hdga(
    jobs,
    machines,
    population_size=30,
    generations=50,
    mutation_rate=0.2,
    local_search_interval=15,
    seed=42
):
    """
    執行簡化版 HDGA。
    """

    random_generator = random.Random(seed)

    population = create_initial_population(
        jobs,
        population_size,
        random_generator
    )

    # 將 FIFO + EDD 基準解放入初始族群
    baseline_chromosome = (
        create_baseline_chromosome(
        jobs,
        machines
        )
    )

    population[0] = baseline_chromosome

    best_chromosome = None
    best_schedule = None
    best_objective = float("inf")

    stagnant_generations = 0

    for generation in range(generations):

        previous_best_objective = best_objective

        fitness_values = []

        for chromosome in population:

            objective_value, schedule = (
                calculate_fitness(
                    chromosome,
                    machines
                )
            )

            fitness_values.append(
                objective_value
            )

            if objective_value < best_objective:
                best_objective = (
                    objective_value
                )
                best_chromosome = (
                    copy_chromosome(
                        chromosome
                    )
                )
                best_schedule = schedule

        elite_index = min(
            range(len(population)),
            key=lambda index: fitness_values[index]
        )

        elite = copy_chromosome(
            population[elite_index]
        )

        next_population = [elite]

        while len(next_population) < population_size:

            parent_1 = tournament_selection(
                population,
                fitness_values,
                random_generator
            )

            parent_2 = tournament_selection(
                population,
                fitness_values,
                random_generator
            )

            child = order_crossover(
                parent_1,
                parent_2,
                random_generator
            )

            child = mutate_chromosome(
                child,
                mutation_rate,
                random_generator
            )

            next_population.append(child)

        population = next_population

                # 檢查本世代是否改善
        if best_objective < previous_best_objective:
            stagnant_generations = 0
        else:
            stagnant_generations += 1

        # 長時間沒有改善時，執行局部搜尋
        if (
            best_chromosome is not None
            and stagnant_generations
            >= local_search_interval
        ):
            (
                local_chromosome,
                local_schedule,
                local_objective
            ) = local_search(
                chromosome=best_chromosome,
                machines=machines
            )

            if local_objective < best_objective:
                best_chromosome = (
                    local_chromosome
                )
                best_schedule = (
                    local_schedule
                )
                best_objective = (
                    local_objective
                )

            stagnant_generations = 0

    return (
        best_chromosome,
        best_schedule,
        best_objective
    )