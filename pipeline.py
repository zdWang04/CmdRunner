# this pipeline is for organizing multi `Task` & `Tasks`
from typing import Optional, List
from task import Task, ParallelTasks


class Pipeline:
    def __init__(self, pipeline_name: Optional[str] = None) -> None:
        self.pipeline = []
        self.pipeline_name = "pipeline_name" if pipeline_name is None else pipeline_name

    def append(
        self, task: Optional[Task] = None, tasks: Optional[ParallelTasks] = None
    ):
        self.pipeline.append(task)
        self.pipeline.append(tasks)

    def from_list(self, task_list: List[Task]):
        self.pipeline.extend(task_list)
