from dataclasses import dataclass, field
from typing import List


@dataclass
class Job:
    """
    代表一個待排程批次。
    """

    job_id: str
    issue_no: str
    device_type: str
    arrival_time: float
    due_date: float
    processing_time: float
    priority: int

    # 可以處理此批次的機台
    eligible_machines: List[str] = field(default_factory=list)

    # 以下欄位會在排程過程中更新
    status: str = "WAITING"
    assigned_machine: str = ""
    start_time: float = -1.0
    completion_time: float = -1.0


@dataclass
class Machine:
    """
    代表一台 SMT 機台。
    """

    machine_id: str
    machine_type: str

    # 這台機台可以處理哪些元件類型
    supported_device_types: List[str]

    # 機台優先級，之後可用於 HDGA 的機台選擇
    machine_priority: float

    status: str = "IDLE"
    available_time: float = 0.0
    current_device_type: str = ""


@dataclass
class FailureEvent:
    """
    代表一次機台故障事件。
    """

    machine_id: str
    failure_time: float
    repair_time: float
    repair_end_time: float


@dataclass
class ScheduleItem:
    """
    代表一個批次在排程中的結果。
    """

    job_id: str
    machine_id: str
    start_time: float
    completion_time: float
    setup_time: float