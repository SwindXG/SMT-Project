import random

from models import ScheduleItem
from objectives import evaluate_schedule


SETUP_TIME = 1.0


def schedule_by_order(job_order, machines):
    """
    根據指定的批次順序建立排程。

    這個函式和 FIFO + EDD 不同：
    它不重新排序，而是完全依照 GA 提供的順序排程。
    """

    machine_list = list(machines)

    available_time = {
        machine.machine_id: 0.0
        for machine in machine_list
    }

    previous_device_type = {
        machine.machine_id: ""
        for machine in machine_list
    }

    schedule = []

    for job in job_order:

        eligible_machines = [
            machine
            for machine in machine_list
            if machine.machine_id in job.eligible_machines
        ]

        if len(eligible_machines) == 0:
            raise ValueError(
                f"{job.job_id} 沒有可用機台"
            )

        candidates = []

        for machine in eligible_machines:
            machine_id = machine.machine_id

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

            candidates.append({
                "machine_id": machine_id,
                "start_time": start_time,
                "completion_time": completion_time,
                "setup_time": setup_time
            })

        selected = min(
            candidates,
            key=lambda candidate: (
                candidate["completion_time"],
                candidate["start_time"],
                candidate["machine_id"]
            )
        )

        machine_id = selected["machine_id"]

        available_time[machine_id] = (
            selected["completion_time"]
        )

        previous_device_type[machine_id] = (
            job.device_type
        )

        schedule.append(
            ScheduleItem(
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
        )

    return schedule


def create_initial_population(
    jobs,
    population_size,
    random_generator
):
    """
    建立初始族群。

    每個個體都是一種批次排列順序。
    """

    population = []

    for _ in range(population_size):
        chromosome = list(jobs)
        random_generator.shuffle(chromosome)
        population.append(chromosome)

    return population


def calculate_fitness(
    chromosome,
    machines
):
    """
    計算單一染色體的目標值。
    目標值越小越好。
    """

    schedule = schedule_by_order(
        chromosome,
        machines
    )

    metrics = evaluate_schedule(
        chromosome,
        schedule
    )

    objective_value = (
        metrics["weighted_completion_time"]
        + 10 * metrics["total_setup_time"]
        + 10 * metrics["total_tardiness"]
    )

    return objective_value, schedule


def tournament_selection(
    population,
    fitness_values,
    random_generator,
    tournament_size=3
):
    """
    使用競賽選擇法選出一個父代。
    """

    candidate_indices = random_generator.sample(
        range(len(population)),
        min(tournament_size, len(population))
    )

    best_index = min(
        candidate_indices,
        key=lambda index: fitness_values[index]
    )

    return list(population[best_index])


def order_crossover(
    parent_1,
    parent_2,
    random_generator
):
    """
    使用 Order Crossover 產生子代。
    """

    chromosome_length = len(parent_1)

    left, right = sorted(
        random_generator.sample(
            range(chromosome_length),
            2
        )
    )

    child = [None] * chromosome_length

    # 先複製 parent_1 的中間區段
    child[left:right] = parent_1[left:right]

    # 從 parent_2 補入尚未出現的批次
    remaining_jobs = [
        job
        for job in parent_2
        if job not in child
    ]

    remaining_index = 0

    for index in range(chromosome_length):
        if child[index] is None:
            child[index] = remaining_jobs[remaining_index]
            remaining_index += 1

    return child


def swap_mutation(
    chromosome,
    mutation_rate,
    random_generator
):
    """
    以交換兩個位置的方式進行突變。
    """

    mutated_chromosome = list(chromosome)

    if random_generator.random() < mutation_rate:
        index_1, index_2 = random_generator.sample(
            range(len(mutated_chromosome)),
            2
        )

        mutated_chromosome[index_1], mutated_chromosome[index_2] = (
            mutated_chromosome[index_2],
            mutated_chromosome[index_1]
        )

    return mutated_chromosome


def run_basic_ga(
    jobs,
    machines,
    population_size=30,
    generations=50,
    mutation_rate=0.2,
    seed=42
):
    """
    執行基本遺傳演算法。
    """

    random_generator = random.Random(seed)

    population = create_initial_population(
        jobs,
        population_size,
        random_generator
    )

    best_chromosome = None
    best_objective = float("inf")
    best_schedule = None

    for generation in range(generations):

        fitness_values = []
        schedules = []

        for chromosome in population:
            objective_value, schedule = calculate_fitness(
                chromosome,
                machines
            )

            fitness_values.append(objective_value)
            schedules.append(schedule)

            if objective_value < best_objective:
                best_objective = objective_value
                best_chromosome = list(chromosome)
                best_schedule = schedule

        # 精英保留：找出本代最佳個體
        elite_index = min(
            range(len(population)),
            key=lambda index: fitness_values[index]
        )

        elite = list(population[elite_index])

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

            child = swap_mutation(
                child,
                mutation_rate,
                random_generator
            )

            next_population.append(child)

        population = next_population

    return best_chromosome, best_schedule, best_objective