from importlib import util
from pathlib import Path


def load_module(filename: str, module_name: str):
    path = Path(__file__).with_name(filename)
    spec = util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"module load failed: {filename}")

    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


config = load_module("01_config.py", "lesson_12_config")
hands_on = load_module("02_hands_on.py", "lesson_12_hands_on")


if __name__ == "__main__":
    hands_on.main(config.BASE_URL)
