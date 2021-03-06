import setuptools
import toml

with open("pyproject.toml") as pyproject_toml:
    project = toml.load(pyproject_toml)["project"]
with open(project.pop("readme"), encoding="utf-8") as readme:
    project["long_description"] = readme.read()
    project["long_description_content_type"] = "text/x-rst"
license = project.pop("license")
project["license"] = license["text"]
setuptools.setup(**project)
