import argparse
from pathlib import Path


def mk_argparser():
    parser = argparse.ArgumentParser(description="创建默认CmdRunner模板")
    parser.add_argument("input_file", help="待创建模板路径")
    args = parser.parse_args()

    return args


def create_template(file_path: Path):
    with open(file_path, "w") as f:
        f.write("""import sys

sys.path.append("/home/dongdong/cmd_runner")

from pathlib import Path

from run import Tasks
from config import GLOBAL_CONFIG as cfg

# modify your config
cfg.dry_run = False
cfg.log_path = "./zzz_log"
cfg.max_worker = 22
# create your command template""")
    print(f"create template CmdRunner in {file_path}")


def main():
    args = mk_argparser()
    create_template(args.input_file)


if __name__ == "__main__":
    main()
