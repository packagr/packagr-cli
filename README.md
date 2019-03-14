# Packagr CLI

A CLI for https://www.packagr.app

## Introduction

> THIS PROJECT IS STILL IN BETA!

This repository allows you to fully manage your Packagr account from an intuitive CLI. All Packagr functions are
available through the CLI, with the exception of user and billing management


## Installation

```
pip install packagr-cli
```

## Quick start

### Step 1 - configure the client

> In order to use this tool, you first need to sign up for a [Packagr](https://www.packagr.app) account, and get your 
unique hash id. You'll need your hash id and the email address and password you used to sign up to Packagr in order to 
configure the client:

```
packagr configure <packagr-hash-id> <email> <password>
```

The above verifies your credentials then creates a file at ~/packagr_conf.toml and stores your credentials there. Many
other commands will need to reference these credentials in order to work.

You should **NOT** commit this file to version control

### Step 2 - create a project

Once you've installed Packagr, you can initiate a new project with the following command:

```bash
packagr init my_package
```

This will create a file called `packagr.toml`, which contains your project configuration, and also a folder called 
`my_package`, where you should put all your code

### Step 3 - add some code

Let's add a super simple file called `hello.py` to our `my_package` folder:

```python
def hello(*args, **kwargs):
    return 'Hello, world!'
```

### Step 4 - build and publish to Packagr

Use this command to build your package:

```bash
packagr package
```

And this one to publish it to Packagr:

```bash
packagr upload
```

Your package has now been pushed to Packagr! You'll be able to install it using the following command, as usual:
```
pip install --extra-index-url https://api.packagr.app/my_hash_id/
```

Or alternatively (and more simply), by using the Packagr CLI:

```bash
packagr add my_package
``` 

> Note that using `packagr add` will add your package as a dependency in your `packagr.toml` file

The Packager CLI also supports many other features, including creation/removal of access tokens and marking packages as
public/private. For the full set of available commands, please refer to the [docs](https://packagr.github.io/packagr-cli/)

