# Packagr CLI

## What is Packagr?

[Packagr](https://www.packagr.app) is a cloud hosted private repository for your private Python packages. The Packagr
CLI is a separate, open source project intended to support it by allowing you to perform most of Packagr's functionality
via the API 

## Installation

Packagr CLI can be installed via pip:

```bash
pip install packagr-cli
```

It can then be invoked via the `packagr` command in any terminal window:

```bash
packagr [command] [args]
```

## Commands

### Configure
`packagr configure <hash-id> <email> <password>`

You should call the `configure` command straight after you install Packagr CLI. This command will store your credentials
to a config file, `packagr_conf.toml`, that is referenced by many other of the Packagr CLI commands, and removes the
need for the Packagr CLI to contstantly prompt you for your password (as is the case with `pip`/`twine`)

#### Parameters

- `hash-id`: See below
- `email`: The email address you registered for Packagr with
- `password`: The password you registered for Packagr with

#### Where do I get my Packagr hash id?

When you first sign up for a [Packagr](https://www.packagr.app) account, you'll be assigned a unique repository url that
looks something like this:

```bash
https://api.packagr.app/u893rj/
```

The last part of this url is your `hash-id`

### Init 
`packagr init <name> [--overwrite]`

In order to create a Package, Packagr needs a file called `packagr.toml`, which contains information about your package.
The `package init` command creates this file for you

The `name` argument is optional - if not specified, the name will default to the name of the folder you invoke the call
from. 

Additionally, the `init` command will also create a subfolder called `name`, if one doesn't already exist. By default,
Packagr assumes that the code you want to package is stored in this folder. However, if you want to customize that, you
can easily do so by editing the `packages` parameter in `packagr.toml`. It's also possible to modify any of the valuues
in the config file manually.

#### Arguments

- `name` (Optional): The name of your package
- `--overwrite` (Optional): If you try to run `packagr init` in a folder where a `packagr.toml` file already exists, you
  will be prompted to confirm that you want to overwrite the existing file. Passing this argument overrides the prompt

### Set
`packagr set <key> <value>`

Once your `packagr.toml` file has been created, you can use the `set` command to set values within it. For example, if 
you wanted to add a description to the config, you could enter the following command:

```bash
packagr set description "some information"
```

You could equally just go into your `packagr.toml` file and add the line `description = "some information"` manually,
but the recommended way is to use the CLI - eventually, the CLI will validate the value of `key` to ensure that it is
valid.

If you enter a duplicate key, you will be prompted to confirm that you want to overwrite it

#### Arguments

- `key`: the setting key
- `value`: the setting value

### Add
`packagr add <key> <value>`

The `add` command works in a similar way to the `set` command, but it's purpose is to append data to arrays already 
defined in the config. For example, if your config already looks like this:

```toml
Authors = ['Chris <chris@packagr.app>'] 
```

Then you can update this value using `packagr add Authors "some guy <me@example.com>"` to change it to the following:

```toml
Authors = [ "Chris <chris@packagr.app>", "Some guy <me@example.com>",]
```

The `add` command will also add a value to a key that doesn't exist.

#### Arguments

- `key`: the setting key
- `value`: the setting value


### Install
`packagr install <some-package>`

The `install` command works in a similar way to `pip install` - it installs a package using your current environment's
`pip` installation. However, this command will also look for packages in your Packagr repository, as well as in the 
public PyPI repository. Once a package is installed correctly, it will also be added to your config's `install_requires`
section

#### Arguments

- `packages`: a list of packages to install
- `--ignore-errors`: In case of multiple packages, passing this argument means that Packagr will continue attempting to
  install the remaining packages on the list in the case that one fails

### Uninstall
`packagr uninstall <some-package>`


This command does the opposite of `install` - it uninstalls a given package and removes it from the dependencies list.

#### Arguments

- `packages`: a list of packages to uninstall
- `--ignore-errors`: In case of multiple packages, passing this argument means that Packagr will continue attempting to
  
  
### Bump
`packagr bump <version> [--minor] [--major]`

The `bump` command increases the version number of your package. Used without arguments, e.g. `packagr bump`, it 
increases the version number, e.g. `1.0.0` becomes `1.0.0`. Using the `--minor` argument increases the minor version
number, e.g. `1.0.0 > 1.1.0` and the `--major` argument converts `1.0.0` to `2.0.0`. The `--major` and `--minor` 
arguments can be used in conjuction with each other.

Alternatively, you can use `packagr bump 4.5.6` to set the version for a specific value. If you aren't using `semver`,
which means that the `bump` command may not be able to parse the existing version number, then you can use this option
instead

#### Arguments

- `version` (optional): the version number to set. Not compatible with any other argument
-  `--minor` (optional): Increase the minor version number
-  `--major` (optional): Increase the major version number


### Package
`packagr package`

Creates `sdist` and/or `wheel` packages based on your config file. Using the command without arguments will create a 
package in both formats. Using `--no-wheel` or `no-sdist` will prevent creation of specific formats

#### Arguments
- `--no-sdist`: Don't build a tarball
- `--no-wheel`: Don't build a wheel


### Upload
`packagr upload [--ignore-409]`

This command will push your package to Packagr. If you are uploading many packages at once, you may opt to use the 
`--ignore-409` argument, which will skip to the next package if encountering a 409 error (conflict for URL). In future,
Packagr CLI will have the ability to display detailed logs from Packagr, which offers a big advantage over `twine`'s
limited ability to handle error responses


### Coming soon

The following commands will be added to future versions of Packagr CLI:

- ``packagr set-readme <readme-file>``: passes the content of a readme file to `Description`
- ``packagr token create <my-package> <email> [--read-only]``: Creates an access token for a package
- ``packagr token delete <my-package> <email> [--no-warnings]``: Deletes an access token
- ``packagr set-public <my-package>``: Sets a package as `public`
- ``packagr set-private <my-package>``: Sets a package as `private`

