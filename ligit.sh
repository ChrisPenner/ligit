#!/bin/sh

error=0
file='manifest'

if [ $1 ]; then
    if [ -d $1 ]; then
        dir="$1"
        cd $dir
        if [ ! -f "$file" ]; then
            echo "No $file file found in `pwd`"
            exit 1
        fi
    elif [ -f $1 ]; then
        cd `dirname $1`
        file="`basename $1`"
    else
        echo "ERROR: $1 doesn't exist!"
        exit 1
    fi
elif [ ! -f "./$file" ]; then
    echo "No $file file found in `pwd`."
    exit 1
fi

echo "Using $file in `pwd`"

clone(){
    curdir=`pwd`
    tempdir=`mktemp -d 2>/dev/null || mktemp -d -t 'ligit'`
    if git clone "https://github.com/$1" "$tempdir"; then
    # if true; then
        return 0
    else
        echo "git clone failed."
        return 1
    fi
}

move(){
    src=`cut -f1 -d\> <<< "$1" | tr -d ' '`
    dest=`cut -f2 -d\> <<< "$1" | tr -d ' '`
    if [ -d $dest ]; then
        echo "Folder at $dest already exists"
        # if [ $response = 'y' -o $response = 'Y' ]; then
        # echo rm -rf $dest
        # else
            # echo "Skipping over $dest"
        # fi
    fi
    mkdir -p "$dest"
    echo "Moving `basename $src` > $dest"
    if mv "$tempdir/$src" $dest; then
        return 0
    else
        echo "Failed moving '$src' to '$dest'"
        return 1
    fi
}


while IFS='' read -r line; do
    if [ "`tr -d ' ' <<< \"$line\" | cut -c1 `" = '#' ]; then
        continue
    fi
    if [ "`cut -c1 <<< \"$line\"`" = ' ' ]; then
        iscommand=0
    else
        iscommand=1
        if [ $tempdir ]; then
            rm -rf $tempdir
        fi
    fi

    if [ $iscommand = 0 -a "$error" = 1 ]; then
        continue
    fi

    if [ $iscommand = 1 ]; then
        if clone $line; then
            error=0
            echo "Successfully cloned $line"
        else
            error=1
            rm -rf $tempdir
        fi
    else
        move "$line"
    fi
done < $file
rm -rf $tempdir
