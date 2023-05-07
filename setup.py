from pathlib import Path
from setuptools import setup, find_namespace_packages  # type: ignore[import]

reqs = Path("requirements.txt").read_text().strip().splitlines()


pkg = "my_feed"


def main() -> None:
    setup(
        name=pkg,
        packages=find_namespace_packages("src"),
        url=f"https://github.com/seanbreckenridge/{pkg}",
        author="Sean Breckenridge",
        author_email="seanbrecke@gmail.com",
        python_requires=">=3.8",
        package_dir={"": "src"},
        zip_safe=False,
        description="A personal feed/website",
        package_data={pkg: ["py.typed"]},
        install_requires=reqs,
        license="MIT",
        entry_points={"console_scripts": ["my_feed = my_feed.__main__:main"]},
        version="0.1.0",
    )


if __name__ == "__main__":
    main()
