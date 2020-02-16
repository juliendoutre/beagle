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

## Dataset

The collection can be downloaded here: http://web.stanford.edu/class/cs276/pa/pa1-data.zip.

This is a 170MBs corpus organized in 10 folders. Each file contains a web page tokenized contents.

## TODO

- get the stop words and remove them from the collection
- stem/lemmatize the tokens
- get the vocabulary
- create a reversed index
