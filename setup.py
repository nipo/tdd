from pathlib import Path
from setuptools import setup, find_packages
from setuptools import Command

class FetchChains(Command):
    """Download certificate chains from ANTS TSL into tdd/chains/."""
    description = "download certificate chains from ANTS TSL"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from tdd.fetch_chains import main
        main(["-o", str(Path(__file__).parent / "tdd" / "chains")])

setup(
    name = "tdd",
    version = "0.2",
    description = "2D-Doc toolsuite",
    long_description = Path("readme.rst").read_text(encoding="utf-8"),
    long_description_content_type = "text/x-rst",
    author = "Nicolas Pouillon",
    author_email = "nipo@ssji.net",
    url = "https://github.com/nipo/tdd",
    license = "MIT",
    classifiers = [
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Security :: Cryptography",
        "Topic :: Text Processing :: General",
    ],
    python_requires = ">=3.9",
    package_data = {
        'tdd': ['chains/*.der', 'chains/tsl_signed.xml'],
    },
    include_package_data = True,
    packages = find_packages(exclude=["tests", "tests.*"]),
    install_requires = [
        "cryptography",
    ],
    cmdclass={
        'fetch_chains': FetchChains,
    },
    extras_require={
        'fetch': [
            'lxml',
            'requests',
        ],
        'dev': [
            'pytest',
            'pyyaml',
        ],
    },
)
