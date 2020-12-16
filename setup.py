from setuptools import setup, Extension
import sys

extensions = [
    Extension("wasmpy.compiled.values", ["wasmpy/compiled/values.pyx"])
]

if "--no-compile" in sys.argv:
    sys.argv.remove("--no-compile")
    extensions = []


with open("README.md", "r") as fp:
    description = fp.read()

setup(
    name="wasmpy",
    version="0.1.0a2",
    author="James Ryan",
    author_email="r.james.dev@gmail.com",
    description="Interactions between WebAssembly and Python",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/r-james-dev/wasmpy",
    packages=["wasmpy"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Assembly",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
    license="MIT",
    ext_modules=extensions
)
