# Beagle

A text search-engine over the Stanford CS276 document collection.

## Install

Run
```shell
pip3 install -e .
```
to install the package.

## Usage

```shell
python3 -m beagle
```

## Tests

```shell
pytest
```

## Dataset

The collection can be downloaded here: http://web.stanford.edu/class/cs276/pa/pa1-data.zip.

This is a 170MBs corpus organized in 10 folders. Each file contains a web page tokenized contents.

## Stop words

The english stop words list we use (saved in `stop_words.json`) comes from this post : https://gist.github.com/sebleier/554280.

## Report

More details can be found in the project [report](./doc/report.md).
