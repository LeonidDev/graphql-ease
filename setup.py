from setuptools import setup, find_packages


setup(
    name="graphql-ease",
    version="0.0.1",
    packages=find_packages(),
    install_requires=["graphql-core-next"],
    python_requires=">=3.7",
    test_suite="tests",
    tests_require=["flake8", "pytest", "pytest-cov", "black"],
)
