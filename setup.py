"""Package setuptools config."""

import importlib

import setuptools

pkg_meta_spec = importlib.util.spec_from_file_location(
    "pkg_meta",
    "singleton_type/pkg_meta.py",
)
pkg_meta = importlib.util.module_from_spec(pkg_meta_spec)
pkg_meta_spec.loader.exec_module(pkg_meta)


with open("README.md", "r", encoding="utf-8") as fh:
    long_description_content_type = "text/markdown"
    long_description = fh.read()


setuptools.setup(
    name=getattr(pkg_meta, "name"),
    version=getattr(pkg_meta, "version"),
    description=getattr(pkg_meta, "description"),
    long_description_content_type=long_description_content_type,
    long_description=long_description,
    author=getattr(pkg_meta, "author"),
    author_email=getattr(pkg_meta, "author_email"),
    url=getattr(pkg_meta, "url"),
    classifiers=getattr(pkg_meta, "classifiers"),
    entry_points=getattr(pkg_meta, "entry_points"),
    python_requires=getattr(pkg_meta, "python_requires"),
    install_requires=getattr(pkg_meta, "install_requires"),
    extras_require=getattr(pkg_meta, "extras_require"),
    packages=setuptools.find_packages(exclude=["test*"]),
)
