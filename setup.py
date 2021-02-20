import setuptools
import toml

with open("pyproject.toml") as pyproject_toml:
    project = toml.load(pyproject_toml)["project"]

setuptools.setup(**project)
