# CmdRunner

## 本项目是什么？

一个`python3.12`标准库编写的、0依赖的脚本运行框架（目前还算不上框架），支持多进程批量运行shell命令，尤其适用于需要大量和shell交互的数据分析工作流。

## 初衷是什么？

- 因为生信分析常常涉及重复的批量运行 shell 脚本，奈何本人不太熟悉 shell，又不愿意去学 [`snakemake`](https://snakemake.readthedocs.io/en/stable/)、[`nf-core`](https://nf-co.re/)一类成熟的 pipeline 管理框架，所以简单的写一个mini-framework，自己开心最重要
- 因为本人痛恨无穷无尽且臃肿的依赖，所以这个项目会全程坚持 0 依赖的作风，完全使用标准库实现

## Quick Start

0.  克隆本仓库

    ```shell
    git clone --depth 1 https://github.com/zdWang04/cmd_runner.git path/to/some/folder
    ```

1.  编辑器支持（仅 vscode）

    `ctrl+shift+P`，输入`setting.json`打开配置文件，将

    ```json
    "python.analysis.extraPaths": ["path/to/some/folder"],
    ```

    写入到配置中

2.  制作脚本

    ```python
    import sys
    sys.path.append("path/to/some/folder") # 很重要，换为克隆时指定的文件夹
    from run import Task, Tasks
    from config import GLOBAL_CONFIG as cfg

    # 首先进行一些配置
    cfg.dry_run = False
    cfg.max_workers = 16

    # 然后制作命令和任务标签
    single_cmd = "single_cmd"
    single_cmd_tag = "single_cmd_tag"
    cmd_list = ["shell_cmd1", "shell_cmd2", "shell_cmd3"]
    tag_list = ["cmd1_tag", "cmd2_tag", "cmd3_tag"] # (可选)，没有的话默认为task_{i}，i 为cmd_list中的索引

    # 然后创建任务
    single_task = Task(single_cmd, single_cmd_tag)
    list_tasks = Tasks(cmd_list, tag_list)

    # 最后跑起来，run!!!
    single_task.run()
    list_tasks.run()
    ```

3.  运行脚本

    ```shell
    python3 ./ur_script.py || python ./ur_script.py
    ```

## 需要注意什么？

- 需要注意这个项目只在`python3.12`解释器 + `ubuntu24.04` 上正常运行，并没有在其他版本python和环境下进行完全测试
- 需要注意作者可能会无期限的暂停开发，所以欢迎 fork
- 需要注意这个狗屎仓库远远不能用于生产使用

## TODO

- 日志
- 更干净的输出
- 隐晦角落的 bug
