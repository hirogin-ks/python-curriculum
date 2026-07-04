from importlib import util
from pathlib import Path


def load_config():
    path = Path(__file__).with_name("01_config.py")
    spec = util.spec_from_file_location("lesson_16_config", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("module load failed: 01_config.py")

    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    config = load_config()
    print(f"lesson_16 の作業用ファイルです: {config.BASE_URL}")
    print("必要な処理をここに実装してください。")


if __name__ == "__main__":
    main()
