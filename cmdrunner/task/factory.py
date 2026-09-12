from .core import TaskType, _ParallelTasks, _SerialTasks, _Task


def create_single_task(cmd: str, tag: str | None = None) -> _Task:
    tag = tag if tag is not None else f"task_id_{id}"
    return _Task(cmd, tag)


def create_parallel_tasks_from_list(
    cmd_list: list[str], tag_list: list[str] | None = None
) -> _ParallelTasks:
    tag_list = (
        tag_list if tag_list is not None else [f"cmd_{i}" for i in range(len(cmd_list))]
    )
    assert len(cmd_list) == len(tag_list), (
        "length of `cmd_list` must equal to `tag_list`"
    )
    ptasks = []
    for idx, cmd in enumerate(cmd_list):
        task = create_single_task(cmd, tag_list[idx])
        ptasks.append(task)
    ptasks = _ParallelTasks(ptasks)
    return ptasks


def create_serial_tasks_from_list(
    cmd_list: list[str], tag_list: list[str] | None = None
) -> _SerialTasks:

    tag_list = (
        tag_list if tag_list is not None else [f"cmd_{i}" for i in range(len(cmd_list))]
    )

    assert len(cmd_list) == len(tag_list), (
        "length of `cmd_list` must equal to `tag_list`"
    )
    stasks = []
    for idx, cmd in enumerate(cmd_list):
        task = create_single_task(cmd, tag_list[idx])
        stasks.append(task)
    stasks = _SerialTasks(stasks)
    return stasks


def create_tasks_from_task(
    tasks: list[TaskType], parallel: bool = False
) -> _ParallelTasks | _SerialTasks:
    if parallel:
        return _ParallelTasks(tasks)
    else:
        return _SerialTasks(tasks)
