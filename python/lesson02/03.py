def main() -> None:
    libraries = ["requests", "bs4", "selenium", "pandas"]

    for lib in libraries:
        try:
            __import__(lib)
            print(f"✅ {lib}: OK")
        except ImportError:
            print(f"❌ {lib}: NG")


if __name__ == "__main__":
    main()
