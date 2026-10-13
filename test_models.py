from models import Job, Machine, FailureEvent, ScheduleItem


job = Job(
    job_id="J0001",
    issue_no="I0001",
    device_type="A",
    arrival_time=0.0,
    due_date=20.0,
    processing_time=5.0,
    priority=1,
    eligible_machines=["M01", "M02"],
)


machine = Machine(
    machine_id="M01",
    machine_type="SMT-1",
    supported_device_types=["A", "B"],
    machine_priority=1.0,
)


failure = FailureEvent(
    machine_id="M01",
    failure_time=10.0,
    repair_time=4.0,
    repair_end_time=14.0,
)


schedule_item = ScheduleItem(
    job_id="J0001",
    machine_id="M01",
    start_time=0.0,
    completion_time=5.0,
    setup_time=1.0,
)


print("批次資料：")
print(job)

print("\n機台資料：")
print(machine)

print("\n故障事件：")
print(failure)

print("\n排程資料：")
print(schedule_item)

print("\n第 1 步完成")