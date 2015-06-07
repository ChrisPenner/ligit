#!/usr/bin/python
""" ligit """
import sys
import os
from subprocess import call
from tempfile import mkdtemp
import shutil
from shutil import ignore_patterns

GIT_PREFIX = 'https://www.github.com/'
BLACK = '\033[30m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'
DEFAULT = '\033[39m'

RESET = '\033[0m'
BOLD = '\033[1m'
ITALICS = '\033[2m'
UNDERLINE = '\033[4m'
INVERSE = '\033[7m'
STRIKETHROUGH = '\033[9m'

COMMENT = 'comment'
REPO = 'repo'
COMMAND = 'command'
DEVNULL = open(os.devnull, 'w')


def print_error(message):
    print RED + message + RESET

def green(message):
    print GREEN + message + RESET

def clone(user, project, tempdir, branch=None):
    print 'user:', user, 'project:', project
    url = GIT_PREFIX + user + '/' + project
    print 'url:', url
    project_dir = os.path.join(tempdir, project)
    green('cloning %s into %s' % (os.path.basename(url), project_dir))
    status = call(['git', 'clone', url, project_dir],
                  stdout=DEVNULL)
    if status != 0:
        print_error('Failed to clone %s, moving on.' % url)
        return False, None
    if branch:
        prev_dir = os.getcwd()
        os.chdir(project_dir)
        checkout_succeeded = call(['git', 'checkout', branch], stdout=DEVNULL) == 0
        os.chdir(prev_dir)
        if not checkout_succeeded:
            print_error("No branch/tag %s in project %s" % (branch, project))
            return False, None
    return True, project_dir

def move(src, dest):
    green('moving %s to %s' % (os.path.basename(src), dest))
    if os.path.isfile(src):
        dest_dir = os.path.dirname(dest)
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        success = shutil.move(src, dest) == 0
    else:
        success = shutil.copytree(src, dest,
                                  ignore=ignore_patterns('.git')) == 0
    return success

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
    commands_run = True
    for line in f.xreadlines():
        line_type = get_line_type(line)
        if line_type == COMMENT:
            continue
        if line_type == REPO:
            if not commands_run:
                src = project_dir
                dest = os.path.join(manifest_dir, project)
                move(src, dest)
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
            if clone_succeeded:
                commands_run = False
                project_dest = os.path.join(manifest_dir, project)
                if os.path.isdir(project_dest):
                    print_error('Removing existing dir: %s' % project_dest)
                    shutil.rmtree(project_dest)


        if line_type == COMMAND and clone_succeeded:
            commands_run = True
            if '>' in line:
                src, dest = line.split('>')
                src, dest = src.strip(), dest.strip()
            else:
                src, dest = line.strip(), ''
            src = os.path.join(project_dir, src)
            dest = os.path.join(manifest_dir, project, dest)
            move(src, dest)
    if not commands_run:
        src = project_dir
        dest = os.path.join(manifest_dir, project)
        move(src, dest)

print tempdir
call(['rm', '-rf', tempdir])
