import contextlib
import importlib
import os
import signal
import sys
import tarfile
from concurrent import futures
from pathlib import Path
from typing import Any, Callable
from zipfile import ZipFile

import pytest
from jaraco import path
from packaging.requirements import Requirement

from .textwrap import DALS

TIMEOUT = int(os.getenv("TIMEOUT_BACKEND_TEST", "180"))  # in seconds
IS_PYPY = "__pypy__" in sys.builtin_module_names


pytestmark = pytest.mark.skipif(
    sys.platform == "win32" and IS_PYPY,
    reason="The combination of PyPy + Windows + pytest-xdist + ProcessPoolExecutor "
    "is flaky and problematic",
)


class BuildBackendBase:
    def __init__(
        self,
        cwd=".",
        env=None,
        backend_name="pyproject_toml.build_system.build_backend",
    ):
        self.cwd = cwd
        self.env = env or {}
        self.backend_name = backend_name


class BuildBackend(BuildBackendBase):
    """PEP 517 Build Backend"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pool = futures.ProcessPoolExecutor(max_workers=1)

    def __getattr__(self, name: str) -> Callable[..., Any]:
        """Handles arbitrary function invocations on the build backend."""

        def method(*args, **kw):
            root = os.path.abspath(self.cwd)
            caller = BuildBackendCaller(root, self.env, self.backend_name)
            pid = None
            try:
                pid = self.pool.submit(os.getpid).result(TIMEOUT)
                return self.pool.submit(caller, name, *args, **kw).result(TIMEOUT)
            except futures.TimeoutError:
                self.pool.shutdown(wait=False)  # doesn't stop already running processes
                self._kill(pid)
                pytest.xfail(f"Backend did not respond before timeout ({TIMEOUT} s)")
            except (futures.process.BrokenProcessPool, MemoryError, OSError):
                if IS_PYPY:
                    pytest.xfail("PyPy frequently fails tests with ProcessPoolExector")
                raise

        return method

    def _kill(self, pid):
        if pid is None:
            return
        with contextlib.suppress(ProcessLookupError, OSError):
            os.kill(pid, signal.SIGTERM if os.name == "nt" else signal.SIGKILL)


class BuildBackendCaller(BuildBackendBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        (self.backend_name, _, self.backend_obj) = self.backend_name.partition(":")

    def __call__(self, name, *args, **kw):
        """Handles arbitrary function invocations on the build backend."""
        os.chdir(self.cwd)
        os.environ.update(self.env)
        mod = importlib.import_module(self.backend_name)

        if self.backend_obj:
            backend = getattr(mod, self.backend_obj)
        else:
            backend = mod

        return getattr(backend, name)(*args, **kw)


class TestBuildMetaBackend:
    backend_name = "pyproject_toml.build_system.build_backend"

    def get_build_backend(self):
        return BuildBackend(backend_name=self.backend_name)

    def test_build_with_pyproject_config(self, tmpdir):
        files = {
            "pyproject.toml": DALS(
                """
                [build-system]
                requires = ["pyproject_toml"]
                build-backend = "pyproject_toml.build_system.build_backend"

                [project]
                name = "foo"
                license = {text = "MIT"}
                description = "This is a Python package"
                dynamic = ["version", "readme"]
                classifiers = [
                    "Development Status :: 5 - Production/Stable",
                    "Intended Audience :: Developers"
                ]
                urls = {Homepage = "http://github.com"}
                dependencies = [
                    "appdirs",
                ]

                [project.optional-dependencies]
                all = [
                    "tomli>=1",
                    "pyscaffold>=4,<5",
                    'importlib; python_version == "2.6"',
                ]

                [project.scripts]
                foo = "foo.cli:main"

                [tool.setuptools]
                zip-safe = false
                package-dir = {"" = "src"}
                packages = {find = {where = ["src"]}}
                license-files = ["LICENSE*"]

                [tool.setuptools.dynamic]
                version = {attr = "foo.__version__"}
                readme = {file = "README.rst"}

                [tool.distutils.sdist]
                formats = "gztar"
                """
            ),
            "MANIFEST.in": DALS(
                """
                global-include *.py *.txt
                global-exclude *.py[cod]
                """
            ),
            "README.rst": "This is a ``README``",
            "LICENSE.txt": "---- placeholder MIT license ----",
            "src": {
                "foo": {
                    "__init__.py": "__version__ = '0.1'",
                    "__init__.pyi": "__version__: str",
                    "cli.py": "def main(): print('hello world')",
                    "data.txt": "def main(): print('hello world')",
                    "py.typed": "",
                }
            },
        }

        build_backend = self.get_build_backend()
        with tmpdir.as_cwd():
            path.build(files)
            sdist_path = build_backend.build_sdist("temp")
            wheel_file = build_backend.build_wheel("temp")

        with tarfile.open(os.path.join(tmpdir, "temp", sdist_path)) as tar:
            sdist_contents = set(tar.getnames())

        with ZipFile(os.path.join(tmpdir, "temp", wheel_file)) as zipfile:
            wheel_contents = set(zipfile.namelist())
            metadata = str(zipfile.read("foo-0.1.dist-info/METADATA"), "utf-8")
            license = str(zipfile.read("foo-0.1.dist-info/LICENSE.txt"), "utf-8")
            epoints = str(zipfile.read("foo-0.1.dist-info/entry_points.txt"), "utf-8")

        assert sdist_contents == {
            "foo-0.1",
            "foo-0.1/LICENSE.txt",
            "foo-0.1/MANIFEST.in",
            "foo-0.1/PKG-INFO",
            "foo-0.1/README.rst",
            "foo-0.1/pyproject.toml",
            "foo-0.1/setup.cfg",
            "foo-0.1/src",
            "foo-0.1/src/foo",
            "foo-0.1/src/foo/__init__.py",
            "foo-0.1/src/foo/__init__.pyi",
            "foo-0.1/src/foo/cli.py",
            "foo-0.1/src/foo/data.txt",
            "foo-0.1/src/foo/py.typed",
            "foo-0.1/src/foo.egg-info",
            "foo-0.1/src/foo.egg-info/PKG-INFO",
            "foo-0.1/src/foo.egg-info/SOURCES.txt",
            "foo-0.1/src/foo.egg-info/dependency_links.txt",
            "foo-0.1/src/foo.egg-info/entry_points.txt",
            "foo-0.1/src/foo.egg-info/requires.txt",
            "foo-0.1/src/foo.egg-info/top_level.txt",
            "foo-0.1/src/foo.egg-info/not-zip-safe",
        }
        assert wheel_contents == {
            "foo/__init__.py",
            "foo/__init__.pyi",  # include type information by default
            "foo/cli.py",
            "foo/data.txt",  # include_package_data defaults to True
            "foo/py.typed",  # include type information by default
            "foo-0.1.dist-info/LICENSE.txt",
            "foo-0.1.dist-info/METADATA",
            "foo-0.1.dist-info/WHEEL",
            "foo-0.1.dist-info/entry_points.txt",
            "foo-0.1.dist-info/top_level.txt",
            "foo-0.1.dist-info/RECORD",
        }
        assert license == "---- placeholder MIT license ----"

        for line in (
            "Summary: This is a Python package",
            "License: MIT",
            "Classifier: Intended Audience :: Developers",
            "Requires-Dist: appdirs",
            "Requires-Dist: " + str(Requirement('tomli>=1 ; extra == "all"')),
            "Requires-Dist: "
            + str(Requirement('importlib; python_version=="2.6" and extra =="all"')),
        ):
            assert line in metadata, (line, metadata)

        assert metadata.strip().endswith("This is a ``README``")
        assert epoints.strip() == "[console_scripts]\nfoo = foo.cli:main"

    _simple_pyproject_example = {
        "pyproject.toml": DALS(
            """
            [project]
            name = "proj"
            version = "42"
            """
        ),
        "src": {"proj": {"__init__.py": ""}},
    }

    def _assert_link_tree(self, parent_dir):
        """All files in the directory should be either links or hard links"""
        files = list(Path(parent_dir).glob("**/*"))
        assert files  # Should not be empty
        for file in files:
            assert file.is_symlink() or os.stat(file).st_nlink > 0

    def test_editable_without_config_settings(self, tmpdir_cwd):
        """
        Sanity check to ensure tests with --mode=strict are different from the ones
        without --mode.

        --mode=strict should create a local directory with a package tree.
        The directory should not get created otherwise.
        """
        path.build(self._simple_pyproject_example)
        build_backend = self.get_build_backend()
        assert not Path("build").exists()
        build_backend.build_editable("temp")
        assert not Path("build").exists()

    def test_build_wheel_inplace(self, tmpdir_cwd):
        config_settings = {"--build-option": ["build_ext", "--inplace"]}
        path.build(self._simple_pyproject_example)
        build_backend = self.get_build_backend()
        assert not Path("build").exists()
        Path("build").mkdir()
        build_backend.prepare_metadata_for_build_wheel("build", config_settings)
        build_backend.build_wheel("build", config_settings)
        assert Path("build/proj-42-py3-none-any.whl").exists()

    @pytest.mark.parametrize("config_settings", [{"editable-mode": "strict"}])
    def test_editable_with_config_settings(self, tmpdir_cwd, config_settings):
        path.build({**self._simple_pyproject_example, "_meta": {}})
        assert not Path("build").exists()
        build_backend = self.get_build_backend()
        build_backend.prepare_metadata_for_build_editable("_meta", config_settings)
        build_backend.build_editable("temp", config_settings, "_meta")
        self._assert_link_tree(next(Path("build").glob("__editable__.*")))
