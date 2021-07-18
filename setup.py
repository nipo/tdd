from setuptools import setup, find_packages

setup(
    name = "tdd -- TwoD Doc",
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
        '': ['*.der'],
    },
    entry_points={
        'console_scripts': [
#            'crobe = crobe.cli.console:cli',
        ],
        'setuptools.installation': [
#            'eggsecutable = crobe.cli.console:cli',
        ]
    },
    use_2to3 = False,
    packages = find_packages(),
    install_requires = [],
    dependency_links=[
    ],
    extras_require={
    },
)
