# Packagr CLI

A CLI for https://www.packagr.app

## Introduction

> THIS REPOSITORY IS STILL JUST A PLACEHOLDER AND DOESN'T ACTUALLY DO ANYTHING YET!

This repository allows you to fully manage your Packagr account from an intuitive CLI. All Packagr functions are
available through the CLI, with the exception of user and billing management


## Installation

> PLACEHOLDER

```
pip install packagr
```

## Usage

> PLACEHOLDER

```
packagr configure <packagr-hash-id> <packagr-api-access-key>
```

The above verifies your credentials then creates a file at ~/packagr_conf.toml and stores those credentials there. Most
other commands will need to reference these credentials in order to work

## Project setup

```
[packagr.package]
name = 'mypackage'
version = '0.1.0'
readme = 'README.rst'
authors = ["Chris Davies <chris@packagr.app>"]
# more options to be added, e.g. everything that setup.py supports
```

## Commands

> PLACEHOLDER

### Admin commands
``packagr create <my-package>``: Creates a skeleton packgr.toml file at the current location

``packagr set foo bar``: Sets the value of `foo` to `bar` in the `packagr.conf` file

``packagr add authors "somebody else <me@example.com"``: Adds a new author to the authors array (works with any array setting)

``packagr install <some-package>``: Installs `some-package` with pip and adds it to the dependencies. Will add packagr repo as `--extra-index-url`

``packagr bump [0.2.0] [--minor|--major]``: Increases the package version

### Packaging commands

``packagr build``: Creates a Python package. Defaults to `sdist` and `wheel` packages

``packagr upload [--ignore-409]``: Uploads any built packages to Packagr. `--ignore-409` means that 409 errors are ignored

### Access tokens

``packagr token create <my-package> <email> [--read-only]``: Creates an access token for a package

``packagr token delete <my-package> <email> [--no-warnings]``: Deletes an access token

## Public access

``packagr set-public <my-package>``: Sets a package as `public`

``packagr set-private <my-package>``: Sets a package as `private`




