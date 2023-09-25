from setuptools import setup, find_namespace_packages


def main() -> None:
    setup(
        packages=find_namespace_packages("src"),
        package_dir={"": "src"},
        zip_safe=False,
        package_data={"my_feed": ["py.typed"]},
    )


if __name__ == "__main__":
    main()
