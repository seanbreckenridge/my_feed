"""
Installed into my global environment incase I ever want to use media_feed as a sort of 'normalized' version of media history
"""

from setuptools import setup, find_namespace_packages  # type: ignore[import]

def main():
    setup(
        name=f"my_media_feed",  # use a different name from karlicoss/HPI, for confusion regarding egg-link reasons
        zip_safe=False,
        packages=["my_media_feed.media_feed"],
        url=f"https://github.com/seanbreckenridge/my_media_feed",
        author="Sean Breckenridge",
        author_email="seanbrecke@gmail.com",
        python_requires=">=3.8",
    )


if __name__ == "__main__":
    main()
