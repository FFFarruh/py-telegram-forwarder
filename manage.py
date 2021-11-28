import os
import subprocess
import sys
from argparse import ArgumentParser
from enum import Enum

# Path to manage.py file. List of commands (manage.py commands...).
_file, *command = sys.argv


class CommandEnum(Enum):
    run = "run"
    format_ = "format"
    lint = "lint"
    test = "test"


parser = ArgumentParser(description="Project's manage file.")
parser.add_argument("command", choices=[enum.value for enum in CommandEnum])
parsed_args = parser.parse_args(command)

command_enum = CommandEnum(parsed_args.command)

os.environ["PYTHONPATH"] = "app"

if command_enum == CommandEnum.run:
    subprocess.run("poetry run python -m app".split(" "))

elif command_enum == CommandEnum.format_:
    subprocess.run("poetry run isort .".split(" "))
    subprocess.run("poetry run black .".split(" "))

elif command_enum == CommandEnum.lint:
    subprocess.run("poetry run flake8 .".split(" "))

elif command_enum == CommandEnum.test:
    subprocess.run("poetry run pytest .".split(" "))
