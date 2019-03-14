# Packagr CLI

A CLI for https://www.packagr.app

## Introduction

> THIS PROJECT IS NOT YET PRODUCTION-READY!

This repository allows you to fully manage your Packagr account from an intuitive CLI. All Packagr functions are
available through the CLI, with the exception of user and billing management


## Installation

```
pip install packagr
```

## Usage

```
packagr configure <packagr-hash-id> <email> <password>
```

The above verifies your credentials then creates a file at ~/packagr_conf.toml and stores those credentials there. Most
other commands will need to reference these credentials in order to work

## Project setup

Packagr relies on a file called `packagr.toml` to work - this file contains information about your specific package that
the CLI references in order to operate correctly. 

You can create a basic `packagr.toml` with the following command:

```bash
packagr init <my-package>
``` 

The file looks something like this: 
```
name = 'my-package'
version = '0.1.0'
```

This file supports the same options that `setup.py` does. You can set/add values in this file using the
`packagr set` and `packagr add` commands


## Commands

### Admin commands

``packagr init <my-package>``: Creates a skeleton packgr.toml file at the current location

``packagr set foo bar``: Sets the value of `foo` to `bar` in the `packagr.conf` file

``packagr add Authors "somebody else <me@example.com>"``: Adds a new author to the authors array (works with any array setting)

``packagr install <some-package>``: Installs `some-package` with pip and adds it to the dependencies. Will add packagr repo as `--extra-index-url`

!! ``packagr uninstall <some-package>``: Opposite of the above

``packagr bump [0.2.0] [--minor|--major]``: Increases the package version

!! ``packagr set-readme README.md``: Copies the content of `README.md` to the `long_description` value of the config

### Packaging commands

``packagr package``: Creates a Python package. Defaults to `sdist` and `wheel` packages

``packagr upload [--ignore-409]``: Uploads any built packages to Packagr. `--ignore-409` means that 409 errors are ignored

### Access tokens

``packagr token create <my-package> <email> [--read-only]``: Creates an access token for a package

``packagr token delete <my-package> <email> [--no-warnings]``: Deletes an access token

## Public access

``packagr set-public <my-package>``: Sets a package as `public`

``packagr set-private <my-package>``: Sets a package as `private`




