from importlib import util
from pathlib import Path


def load_scraper():
    path = Path(__file__).with_name("02_scraper.py")
    spec = util.spec_from_file_location("lesson_24_scraper", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("module load failed: 02_scraper.py")

    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


scraper_module = load_scraper()
JobScraper = scraper_module.JobScraper


if __name__ == "__main__":
    scraper = JobScraper("https://realpython.github.io/fake-jobs/")
    scraper.run()
