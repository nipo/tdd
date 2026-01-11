from setuptools import setup, find_packages

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
        'tdd': ['chains/*.der'],
    },
    include_package_data = True,
    use_2to3 = False,
    packages = find_packages(),
    install_requires = [
        "pycryptodome",
    ],
    dependency_links=[
    ],
    extras_require={
        'dev': [
            'pytest',
            'pyyaml',
        ]
    },
)
