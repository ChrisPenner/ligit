# Ligit (le-jit)
A quick, easy, and very portable manager for libraries hosted on git, works for any language and any project structure.

## Why?
There are tons of different package managers out there, but let's be honest; a lot of them suck, sometimes they're
not kept up to date with the latest versions/formulas, and if you want to manage your own libraries you need
to package them up nicely and it's a lot of work. Not to mention you need a different package manager for each
platform or language (pip, npm, gem etc.).

Ligit solves these problems by making the package the source code itself, this means it's:
    - *Always up to date*
    - *Always accessible* (git is the only dependency for ligit)
    - *Always configurable* (you can specify to keep only the folders/files you actually need)
    - *Easy to update* (with a single command you can update ALL your libs, regardless of what they are)

The basic idea is to clone the repo, then pull only the folders/files you need into your project.
You can specify exactly which files you need and how you'd like them organized by using a dead-simple *manifest file*.

## Manifest files
Define a manifest like this:
```bash
# Inside 'manifest' file

# Specify github username and repo for each project 'username/project'
# The indented block contains instructions for that project. Here we're copying only a few files from that repo,
# and we're rearranging the structure of it a bit.
ChrisPenner/dotfiles
    vimrc > .
    functions > extras/

# You can also specify a specific tag, version, branch, or commit to checkout using the '#' symbol
ChrisPenner/vimprove#v0.3
    tips > .

# Using only the header will simply include the entire project in a folder named after the repo
ChrisPenner/BoxKite#nightly-builds
```

This manifest file results in a structure like this:
> lib
> ├── vimprove
> │   └── tips
> ├── dotfiles
> │   ├── extras
> │   │   └── functions
> │   └── vimrc
> └── BoxKite
>     └── boxkite-source-here

Any files or directories that are not specified are not be added, so make sure you grab everything you need.

## Usage
Run with: `ligit [manifest-file]`

ligit will install the libs in the same folder as the given manifest file.
