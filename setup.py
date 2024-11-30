import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="count_stuff",
    version="0.1.0",
    author="Wesley Monteith-Finas; Camille Challier; Emma Boehly; Leo Bruneau",
    # description="TODO",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
