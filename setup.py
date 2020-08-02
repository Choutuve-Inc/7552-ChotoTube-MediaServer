import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="7552-ChotoTube-MediaServer", # Replace with your own username
    version="1.0.0",
    author="Santiago Mariaro",
    author_email="santiagomarinaro1@gmail.com",
    description="Trabajo practico de taller 2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Choutuve-Inc/7552-ChotoTube-MediaServer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)