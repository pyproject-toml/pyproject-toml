import setuptools
import toml

with open("pyproject.toml") as pyproject_toml:
    pyproject_toml = toml.load(pyproject_toml)
    project = pyproject_toml["project"]
    tool = pyproject_toml["tool"]["pyproject-toml"]
with open(project.pop("readme"), encoding="utf-8") as readme:
    project["long_description"] = readme.read()
    project["long_description_content_type"] = "text/x-rst"
license = project.pop("license")
project["license"] = license["text"]
project["install_requires"] = project.pop("dependencies", None)
setuptools.setup(**tool, **project)
