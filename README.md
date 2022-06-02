# anachat

[![Github Actions Status](https://github.com/EPICLab/DSChatbot/workflows/Build/badge.svg)](https://github.com/EPICLab/DSChatbot/actions/workflows/build.yml)[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/EPICLab/DSChatbot/main?urlpath=lab)

Chatbot for supporting data science analyses in Jupyter Lab

This extension is composed of a Python package named `anachat`
for the server extension and a NPM package named `anachat`
for the frontend extension.

## Requirements

- JupyterLab >= 3.0

## Install

To install the extension, execute:

```bash
pip install anachat
```

## Uninstall

To remove the extension, execute:

```bash
pip uninstall anachat
```

## Troubleshoot

If you are seeing the frontend extension, but it is not working, check
that the server extension is enabled:

```bash
jupyter server extension list
```

If the server extension is installed and enabled, but you are not seeing
the frontend extension, check the frontend extension is installed:

```bash
jupyter labextension list
```
