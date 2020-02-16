from setuptools import setup

setup(
    name="beagle",
    description="A text search-engine over the Stanford CS276 document collection.",
    url="https://github.com/juliendoutre/beagle",
    author="Julien Doutre",
    author_email="jul.doutre@gmail.com",
    license="MIT",
    version="0.1.0",
    packages=["beagle"],
    zip_safe=True,
    entry_points={"console_scripts": ["beagle = beagle.__main__:main"]},
    install_requires=["nltk"],
)
