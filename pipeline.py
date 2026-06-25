# Pipeline is for organizing multi `_Task`
from typing import Optional
from task import TaskType
from itertools import groupby

from task import create_parallel_tasks_from_list, create_serial_tasks_from_list
from uuid import uuid4


class Pipeline:
    def __init__(
        self, procedures: list[TaskType], pipeline_name: Optional[str] = None
    ) -> None:
        self.pipeline_name = (
            pipeline_name if pipeline_name is not None else f"SomePipeline_{uuid4()}"
        )
        self.procedures = procedures

    def __repr__(self) -> str:
        task_count = len(self.procedures)
        info = f"{self.__class__.__name__} | {task_count} procedure(s)\n"
        for idx, tasks in enumerate(self.procedures):
            info += "\n" + "#" * 25 + "\n"
            info += f"procedure_{idx + 1}: {tasks.__class__.__name__}\n"
            info += repr(tasks)
        return info

    def run(self):
        for procedure in self.procedures:
            procedure.run()

    @classmethod
    def from_list(
        cls,
        cmds: list[str],
        tags: list[str],
        paralle_flag: list[bool],
        pipeline_name: Optional[str] = None,
    ):

        g = groupby(paralle_flag)
        current_index = 0
        tasks_list = []
        for k, group in g:
            tasks_len = len(list(group))
            group_cmds = cmds[current_index : current_index + tasks_len]
            group_tags = tags[current_index : current_index + tasks_len]
            print(group_cmds)
            if k:
                tasks = create_parallel_tasks_from_list(group_cmds, group_tags)
            else:
                tasks = create_serial_tasks_from_list(group_cmds, group_tags)
            tasks_list.append(tasks)

            current_index += tasks_len

        return cls(tasks_list, pipeline_name)
