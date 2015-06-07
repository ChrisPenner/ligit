#!/usr/bin/python
""" ligit """
import sys
import os
from subprocess import call
from tempfile import mkdtemp

GIT_PREFIX = 'https://www.github.com/'
BLACK   = '\033[30m'
RED     = '\033[31m'
GREEN   = '\033[32m'
YELLOW  = '\033[33m'
BLUE    = '\033[34m'
MAGENTA = '\033[35m'
CYAN    = '\033[36m'
WHITE   = '\033[37m'
DEFAULT = '\033[39m'

RESET         = '\033[0m'
BOLD          = '\033[1m'
ITALICS       = '\033[2m'
UNDERLINE     = '\033[4m'
INVERSE       = '\033[7m'
STRIKETHROUGH = '\033[9m'

COMMENT = 'comment'
REPO = 'repo'
COMMAND = 'command'


def print_error(message):
    print RED + message + RESET

def green(message):
    print GREEN + message + RESET

def clone(user, project, tempdir, branch=None):
    print 'user:', user, 'project:', project
    url = GIT_PREFIX + user + '/' + project
    print 'url:', url
    project_dir = os.path.join(tempdir, project)
    green('cloning %s into %s' % (url, project_dir))
    status = call(['git', 'clone', url, project_dir])
    if status != 0:
        print_error('Failed to clone %s, moving on.' % url)
        return False, None;
    if branch:
        prev_dir = os.getcwd()
        os.chdir(project_dir)
        green('checking out branch: %s' % branch)
        checkout_succeeded = call(['git', 'checkout', branch]) == 0
        os.chdir(prev_dir)
        if not checkout_succeeded:
            print_error("No branch/tag %s in project %s" % (branch, project))
            return False, None
    return True, project_dir

def move(src, dest):
    green('moving %s to %s' % (src, dest))
    return

def get_line_type(line):
    if line.strip().startswith('#') or line.strip() == '':
        return COMMENT
    if line.startswith(' ') or line.startswith('\t'):
        return COMMAND
    else:
        return REPO

file_path = 'manifest'
if len(sys.argv) > 1:
    file_path = sys.argv[1]

if not os.path.isfile(file_path):
    print "Can't find file %s" % file_path
    sys.exit(1)

manifest_dir = os.path.dirname(file_path) or os.getcwd()
manifest_file = os.path.join(manifest_dir, file_path)

os.chdir(manifest_dir)
print "Using %s from %s" % (file_path, manifest_dir)


tempdir = mkdtemp(prefix='ligit')
with open(manifest_file) as f:
    failed = False
    project_dir = None
    clone_succeeded = False
    for line in f.xreadlines():
        line_type = get_line_type(line)
        if line_type == COMMENT:
            continue
        if line_type == REPO:
            if '#' in line:
                repo, branch = line.split('#')
                repo, branch = repo.strip(), branch.strip()
            else:
                repo = line.strip()
                branch = None
            user, project = repo.split('/')
            user, project = user.strip(), project.strip()
            clone_succeeded, project_dir = clone(user=user, project=project,
                                              tempdir=tempdir, branch=branch)

        if line_type == COMMAND:
            if not clone_succeeded:
                continue
            if '>' in line:
                src, dest = line.split('>')
                src, dest = src.strip(), dest.strip()
            else:
                src, dest = line, ''
            src = os.path.join(tempdir, src)
            dest = os.path.join(project_dir, dest)
            move(src, dest)

print tempdir
call(['rm', '-rf', tempdir])

# move(){
#     src=`cut -f1 -d\> <<< "$1" | tr -d ' '`
#     dest=`cut -f2 -d\> <<< "$1" | tr -d ' '`
#     if [ -d $dest ]; then
#         echo "Folder at $dest already exists"
#         # if [ $response = 'y' -o $response = 'Y' ]; then
#         # echo rm -rf $dest
#         # else
#             # echo "Skipping over $dest"
#         # fi
#     fi
#     mkdir -p "$dest"
#     echo "Moving `basename $src` > $dest"
#     if mv "$tempdir/$src" $dest; then
#         return 0
#     else
#         echo "Failed moving '$src' to '$dest'"
#         return 1
#     fi
# }


# while IFS='' read -r line; do
#     if [ "`tr -d ' ' <<< \"$line\" | cut -c1 `" = '#' ]; then
#         continue
#     fi
#     if [ "`cut -c1 <<< \"$line\"`" = ' ' ]; then
#         iscommand=0
#     else
#         iscommand=1
#         if [ $tempdir ]; then
#             rm -rf $tempdir
#         fi
#     fi

#     if [ $iscommand = 0 -a "$error" = 1 ]; then
#         continue
#     fi

#     if [ $iscommand = 1 ]; then
#         if clone $line; then
#             error=0
#             echo "Successfully cloned $line"
#         else
#             error=1
#             rm -rf $tempdir
#         fi
#     else
#         move "$line"
#     fi
# done < $file
# rm -rf $tempdir
