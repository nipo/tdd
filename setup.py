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
    version = "0.1",
    description = "2D-Doc toolsuite",
    author = "Nicolas Pouillon",
    author_email = "nipo@ssji.net",
    license = "BSD",
    classifiers = [
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
    ],
    package_data = {
        'tdd': ['chains/*.der', 'chains/tsl_signed.xml'],
    },
    include_package_data = True,
    use_2to3 = False,
    packages = find_packages(),
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
