# llm-video-frames

[![PyPI](https://img.shields.io/pypi/v/llm-video-frames.svg)](https://pypi.org/project/llm-video-frames/)
[![Changelog](https://img.shields.io/github/v/release/simonw/llm-video-frames?include_prereleases&label=changelog)](https://github.com/simonw/llm-video-frames/releases)
[![Tests](https://github.com/simonw/llm-video-frames/actions/workflows/test.yml/badge.svg)](https://github.com/simonw/llm-video-frames/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/llm-video-frames/blob/main/LICENSE)

LLM plugin to turn a video into individual frames

## Installation

Install this plugin in the same environment as [LLM](https://llm.datasette.io/).
```bash
llm install llm-video-frames
```
## Usage

Usage instructions go here.

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:
```bash
cd llm-video-frames
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
python -m pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
