# Ligit (Lah-Jit)
A quick, easy, and very portable manager for libraries hosted on git, works for any language and any project structure.

## Why?
There are tons of different package managers out there, but let's be honest; a lot of them suck, sometimes they're
not kept up to date with the latest versions/formulas, and if you want to manage your own libraries you need
to package them up nicely and it's a lot of work. Not to mention you need a different package manager for each
platform or language (pip, npm, gem etc.).

Ligit solves these problems by making the package the source code itself, this means it's:

* **Always up to date**
* **Always accessible** (git is the only dependency for ligit)
* **Always configurable** (you can specify to keep only the folders/files you actually need)
* **Easy to update** (with a single command you can update ALL your libs, regardless of what they are)

The basic idea is to clone the repo, then pull only the folders/files you need into your project.
You can specify exactly which files you need and how you'd like them organized by using a dead-simple **manifest file**.

## Manifest files
Define a manifest like this:
```bash
# Sample manifest file

# Specify github username and repo for each project 'username/project'
# Using only the username/repo will simply include the entire project in a folder named after the repo
ChrisPenner/vimprove#v0.3

# An indented block contains instructions for that project. Here we're copying only a few files from that repo
# and we're rearranging the structure of it a bit.
# If a file/folder is listed without a destination it's copied to the project folder.
ChrisPenner/dotfiles
    zshrc
    vimrc
    profile
    functions > extras/

# You can also specify a specific tag, version, branch, or commit to checkout using the '#' symbol
# File globbing works too!
ChrisPenner/BoxKite#nightly-build
    *.py
    content
    css > static/
    js > static/
    templates/* > static/html/
```

This manifest file results in a structure something like this (simplified):
```
lib
├── vimprove
│   ├── vimtips.sh
│   ├── tips
│   └── data
├── dotfiles
│   ├── extras
│   │   └── functions
│   ├── zshrc
│   ├── vimrc
│   └── profile
└── BoxKite
    ├── static
    │   ├── js
    │   ├── html
    │   │   ├── template2.html
    │   │   └── template1.html
    │   └── css
    ├── content
    │   ├── posts
    │   │   ├── post3.txt
    │   │   ├── post2.txt
    │   │   └── post1.txt
    │   └── images
    │       ├── image2.png
    │       └── image1.png
    ├── routes.py
    ├── main.py
    └── config.py
```

Any files or directories that are not specified are not be added, so make sure you grab everything you need.

## Usage
Run with: `ligit [manifest-file]`

ligit will install the libs in the same folder as the given manifest file.
