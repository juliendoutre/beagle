# Project Report

Rémi Calixte & Julien Doutre

## Contents

- [Introduction](#introduction)
- [Beagle's usage](#beagle's-usage)
- [Repository organization](#repository-organization)
- [Dataset](#dataset)
- [Indexing engine](#indexing-engine)
- [Search engine](#search-engine)
- [Possible improvements](#possible-improvements)

## Introduction

Beagle is the name of the tool we developped for our **Information Research course**.
The goal was to create a text search engine from scratch based on a specific collection of documents.
It should index the collection in a efficient manner and have at least the capability to answer requests that take the following forms:
- boolean expression (ex: `(cancer OR oncology) AND NOT melanoma`)
- vectorial expression (ex: `cancer oncology`)

## Beagle's usage

### Requirements

Beagle was developped in Python 3.
We make an abusive use of Python type hints to help maintaining a clean and readable code.

It depends ont two Python packages listed in [requirements.txt](../requirements.txt):
- `nltk` is a natural language toolkit that we use for lemmatization
- `ttable` that we use to manipulate boolean expressions

By default, beagle expects to see the collection in a `./dataset` folder.
You can download it from this url: http://web.stanford.edu/class/cs276/pa/pa1-data.zip.
Since the collection is divided in 10 subdirectory, your project tree shoud look like this:
```shell
.
├── beagle/
├── dataset/
│   ├── 0/
│   ├── 1/
│   ├── 2/
│   ├── 3/
│   ├── 4/
│   ├── 5/
│   ├── 6/
│   ├── 7/
│   ├── 8/
│   └── 9/
├── doc/
├── LICENSE
├── README.md
├── report.md
├── requirements.txt
├── setup.py
├── stop_words.json
└── venv/
```

### Install

In order to avoid polluting your work environment, we recommand to install beagle in a dedicated virtualenv.

You can create a new one with:
```shell
python3 -m venv venv
```

Then enter it with:
```shell
. venv/bin/activate
```

You can install beagle by running the following commmand in the project directory:
```shell
pip3 install -e .
```

### Usage

Beagle takes the form of a cli tool offering two commands:
```shell
usage: beagle [-h] [-v] {index,search} ...

A text search-engine over the Stanford CS276 document collection.

positional arguments:
  {index,search}  available commands
    index         to index the collection
    search        to query the collection

optional arguments:
  -h, --help      show this help message and exit
  -v, --verbose   verbose mode
```

##### Indexing

```shell
usage: beagle index [-h] [-d DATASET] [-t {documents,frequencies,positions}]
                    [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -d DATASET, --dataset DATASET
                        path to the dataset
  -t {documents,frequencies,positions}, --type {documents,frequencies,positions}
                        type of index
  -o OUTPUT, --output OUTPUT
                        path to which save the index and stats
```

##### Researching

```shell
usage: beagle search [-h] [-i INPUT] [-e ENGINE]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        path to the saved index and stats
  -e ENGINE, --engine ENGINE
                        the engine to use to perform queries among (binary,
                        vectorial)
```

Unlike the `index` command, `search` will launch an interactive console that allows the user to enter several requests without the need to reload the index (which is a time-expensive operation). It can also understand some metacommands, prefixed with a `.` (like in the SQLite prompt):
```shell
(venv) 11:47 julien@julien-XPS-13 ~/dev/beagle% beagle search
2020-04-09 11:47:53,634 - root - INFO - Beginning to 'load_index'...
2020-04-09 11:48:12,006 - root - INFO - Finished to 'load_index' in 18.371545s.
welcome, to get instructions type .help
beagle> .help
available commands: exit, engine, help, set-engine
beagle> .engine
binary
beagle> .set-engine vectorial
beagle> .engine
vectorial
beagle> .exit
```

## Repository organization

The code of the package itself is contained in `./beagle`.

![packages dependencies](./img/packages_beagle.png)

### Setup

The `setup.py` file makes it installable with pip as a CLI tool, with the `main` function defined in `./beagle/__main__.py` as an entry point.

### CLI

This function contains the CLI logic. Its only purpose is to parse the user input and react by instanciating the appropriate classes and calling their methods.

### Logging

The `logging.py` file defines a specific format for out logging messages as well as the `timer` decorator that allows us to measure and print the execution time of a targeted function. Here is an example with the `InvertedIndex.load_index` method:
- The code:
```python
@timer # the function is decorated
def load_index(path: str) -> InvertedIndex:
    with open(path, "r") as f:
        raw = json.load(f)
        index = InvertedIndex(raw["type"])
        index.entries = raw["entries"]
    return index
```
- The output:
```shell
# Whenever the function is called, its execution time is logged
2020-04-09 11:47:53,634 - root - INFO - Beginning to 'load_index'...
2020-04-09 11:48:12,006 - root - INFO - Finished to 'load_index' in 18.371545s.
```

We use this decorator on critical functions whose we want to evaluate the efficiency and test optimizations on.

### Classes

We use object oriented programming to maintain consistency between the data structures we manipulate and their behaviors.

![classes diagram](./img/classes_beagle.png)

## Dataset

### Description

### Statistical analysis

## Indexing engine

### Files loading

### Stop words

### Lemmatization

### Vocabulary

## Search engine

### Boolean requests

### vectorial research

## Possible improvements
