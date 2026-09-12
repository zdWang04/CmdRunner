# CmdRunner

## 本项目是什么？

一个`python3.12`标准库编写的、0依赖的脚本运行框架（目前还算不上框架），支持多进程批量运行shell命令，尤其适用于需要大量和shell交互的数据分析工作流。

## 初衷是什么？

- 因为生信分析常常涉及重复的批量运行 shell 脚本，奈何本人不太熟悉 shell，又不愿意去学 [`snakemake`](https://snakemake.readthedocs.io/en/stable/)、[`nf-core`](https://nf-co.re/)一类成熟的 pipeline 管理框架，所以简单的写一个mini-framework，自己开心最重要
- 因为本人痛恨无穷无尽且臃肿的依赖，所以这个项目会全程坚持 0 依赖的作风，完全使用标准库实现

## Quick Start

0.  克隆本仓库

    ```shell
    git clone --depth 1 https://github.com/zdWang04/CmdRunner.git path/to/some/folder
    ```

1.  永久加入路径（可选）

    - linux用户

      打开`~/.bashrc`或者`~/.zshrc`（linux用户）

    ```bash
    export PYTHONPATH="path/to/some/folder:$PYTHONPATH"
    ```

    - Windows用户

      `windows + R`呼出窗口，输入`cmd`，然后运行以下命令

    ```cmd
    setx PYTHONPATH "C:path/to/some/folder"
    ```

2.  制作脚本

    ```python
    # ur_script.py

    from cmdrunner import create_single_task, create_parallel_tasks_from_list, create_serial_tasks_from_list
    from cmdrunner import config as cfg


    # 首先进行一些配置
    cfg.dry_run = False
    cfg.max_workers = 16

    # 然后制作命令和任务标签
    single_cmd = "shell_cmd0"
    multi_cmd_list = ["shell_cmd1", "shell_cmd2", "shell_cmd3"]

    single_cmd_tag = "cmd0_tag" # （可选）
    multi_tag_list = ["cmd1_tag", "cmd2_tag", "cmd3_tag"] # (可选)

    # 然后创建任务

    ## 创建单个任务
    single_task = create_single_task(single_cmd, single_cmd_tag)

    ## 创建多进程并行任务
    parallel_tasks = create_parallel_tasks_from_list(cmd_list, tag_list)

    ## 创建单进程串行任务
    serial_tasks = create_serial_tasks_from_list(cmd_list, tag_list)

    ## 最后跑起来，run!!!
    single_task.run()
    parallel_tasks.run()
    serial_tasks.run()
    ```

3.  运行脚本
    - 如果已经永久加入路径
      ```shell
      python3 ./ur_script.py
      ```
    - 如果没有
      - linux用户
        ```bash
        PYTHONPATH="path/to/some/folder" python3 ./ur_script.py
        ```
      - Windows用户
        ```bash
        set PYTHONPATH=C:\path\to\some\folder && python user_script.py
        ```

## 需要注意什么？

- 需要注意这个项目只在`python3.12`解释器 + `ubuntu24.04` 上正常运行，并没有在其他版本python和环境下进行完全测试
- 需要注意作者可能会无期限的暂停开发，所以欢迎 fork
- 需要注意这个仓库远远不能用于生产使用

## TODO

- 编写 TaskMonitor 的逻辑
- 任务恢复与跳过
- 隐晦角落的 bug
- 对 Pipeline 的全面支持
- 添加类似`sankemake`中的`expand`

- 日志 | Done

## 警告

- **Pipeline 尚且不完善**
