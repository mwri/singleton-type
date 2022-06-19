"""NOX config."""

import glob
import importlib

import nox

pkg_meta_spec = importlib.util.spec_from_file_location(
    "pkg_meta",
    "singleton_type/pkg_meta.py",
)
pkg_meta = importlib.util.module_from_spec(pkg_meta_spec)
pkg_meta_spec.loader.exec_module(pkg_meta)


default_pyvsn = "3"
test_pyvsns = ["3.6", "3.7", "3.8", "3.9", "3.10"]


@nox.session(python=[default_pyvsn])
def build(session):
    session.install("setuptools", "wheel")
    session.run("python3", "setup.py", "sdist", "bdist_wheel")


@nox.session(python=[default_pyvsn])
def lint(session):
    session.install("black")
    session.install("isort")
    session.run(
        "black",
        "--check",
        "--line-length",
        "120",
        "--skip-string-normalization",
        "singleton_type",
        "test",
        "setup.py",
        "noxfile.py",
    )
    session.run(
        "isort",
        "--check",
        "singleton_type",
        "test",
        "setup.py",
        "noxfile.py",
    )


@nox.session(python=[default_pyvsn])
def mypy(session):
    session.install("mypy")
    session.run(
        "mypy",
        "singleton_type",
    )


@nox.session(python=[default_pyvsn])
def coverage(session):
    session.install("coverage", "pytest")
    session.run(
        "coverage",
        "run",
        "--branch",
        "--source=singleton_type",
        "--omit=singleton_type/pkg_meta.py",
        "-m",
        "pytest",
        "test",
    )
    session.run("coverage", "report")
    session.run("coverage", "html")
    session.run("coverage", "xml")


@nox.session(python=test_pyvsns)
def test(session):
    session.install("pytest")
    session.run("pytest")
