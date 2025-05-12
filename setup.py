from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="faketelemetry",
    version="0.1.2",
    description="Real-time Fake Telemetry Stream Generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Adam Billekvist",
    author_email="adam.billeqvist@gmail.com",
    url="https://github.com/adkvi/faketelemetry",
    project_urls={
        "Documentation": "https://github.com/adkvi/faketelemetry#readme",
        "Source": "https://github.com/adkvi/faketelemetry",
        "Tracker": "https://github.com/adkvi/faketelemetry/issues",
    },
    keywords=[
        "telemetry", "signal", "generator", "iot", "testing", "simulation", "waveform", "python"
    ],
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Testing",
    ],
)