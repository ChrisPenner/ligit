#!/usr/bin/python
""" ligit """
import sys
import os
from subprocess import call
from tempfile import mkdtemp
import shutil
from shutil import ignore_patterns
from argparse import ArgumentParser, FileType
from contextlib import contextmanager

VERSION = 'v0.0.1'

parser = ArgumentParser(description="Minimalist Git library management.")
parser.add_argument('manifest', help='Path to manifest file containing instructions.',
                    type=FileType('r'), default=None, nargs='?')

parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                    help='Print out all error messages and git logs')
parser.add_argument('--version', action='version', version=VERSION)
args =  parser.parse_args()
VERBOSE = args.verbose

try:
    manifest = args.manifest or open('manifest', 'r')
except IOError as e:
    print 'No manifest file found in current directory.'
    print 'Please specify a file or move to a directory containing one.'
    sys.exit(1)

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
OUT = sys.stdout if VERBOSE else open(os.devnull, 'w')
LIB_DIR = os.getcwd()
TEMP_DIR = mkdtemp(prefix='ligit')

ERROR = 1
OK = 0

@contextmanager
def cd(path):
    old_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_dir)

def _error(*args):
    """Prints errors in red."""
    print RED, ' '.join(args), RESET

def _ok(*args):
    """Prints messages in green."""
    print GREEN, ' '.join(args), RESET

def _clone(info):
    """Uses git to clone a repo into TEMP_DIR."""
    url = info['url']
    clone_dir = info['clone_dir']
    branch = info['branch']
    project = info['project']
    status = call(['git', 'clone', url, clone_dir], stdout=OUT, stderr=OUT)
    if status != 0:
        _error('Failed to clone %s, moving on.' % url)
        return ERROR
    if branch:
        with cd(clone_dir):
            status = call(['git', 'checkout', branch], stdout=OUT, stderr=OUT)
        if status != 0:
            _error("Error in project %s: No branch/tag %s found" % (project, branch))
            return ERROR
    return OK

def _move(src, dest):
    """Moves desired files from src to dest"""
    if os.path.isfile(src):
        file_name = os.path.basename(src)
        dest_dir = os.path.dirname(dest)
        dest_file_name = os.path.join(dest_dir, file_name)
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        if os.path.isfile(dest_file_name):
            os.remove(dest_file_name)
        success = shutil.move(src, dest)
    else:
        if os.path.isdir(dest):
            shutil.rmtree(dest)
        success = shutil.copytree(src, dest, ignore=ignore_patterns('.git'))
    return success

def _get_line_type(line):
    """Determine type of the current line"""
    if line.strip().startswith('#') or line.strip() == '':
        return COMMENT
    if line.startswith(' ') or line.startswith('\t'):
        return COMMAND
    else:
        return REPO

def _parse_repo(line):
    if '#' in line:
        repo, branch = line.split('#')
        repo, branch = repo.strip(), branch.strip()
    else:
        repo = line.strip()
        branch = None
    user, project = repo.split('/')
    user, project = user.strip(), project.strip()
    url = GIT_PREFIX + repo
    clone_dir = os.path.join(TEMP_DIR, project)
    return {'user': user, 'project': project, 'url': url, 'repo': repo, 'clone_dir': clone_dir, 'branch': branch}


def _split_file_into_chunks(f):
    """Produces a list where each element is a list of lines associated with a project,"""
    chunks = []
    current_chunk = []
    for line in f.xreadlines():
        line_type = _get_line_type(line)
        line = line.strip()
        if line_type == COMMENT:
            # Skip comments
            continue
        elif line_type == REPO:
            # If the current chunk is empty, add the repo
            if len(current_chunk) == 0:
                current_chunk.append(line)
                continue
            # Otherwise start a new chunk
            else:
                chunks.append(current_chunk)
                current_chunk = [line]
                continue
        else: # Line is command
            # If the current chunk is empty, something weird happened
            if len(current_chunk) == 0:
                _error('Command found outside of a project block')
                _error(line)
                raise Exception('Command found outside of a project block')
            # Otherwise add command to chunk
            else:
                current_chunk.append(line)
    # clean up un-added chunks
    if current_chunk:
        chunks.append(current_chunk)
    return chunks


def _process_chunk(chunk):
    project_info = _parse_repo(chunk[0])
    status = _clone(project_info)
    if status == ERROR:
        return
    if len(chunk) == 1:
        _copy_all(project_info)
        return
    # No longer need repo info
    chunk.pop(0)
    _run_commands(project_info, chunk)

def _run_commands(info, chunk):
    for line in chunk:
        if '>' in line:
            src, dest = line.split('>')
            src, dest = src.strip(), dest.strip()
        else:
            src, dest = line.strip(), ''
        clone_dir = info['clone_dir']
        project = info['project']
        src = os.path.join(clone_dir, src)
        dest = os.path.join(LIB_DIR, project, dest)
        try:
            _move(src, dest)
        except Exception as e:
            _error('copy failed in project %s' % project, e)
    _ok('Finished %s' % project)

def _copy_all(info):
    src = info['clone_dir']
    project = info['project']
    dest = os.path.join(LIB_DIR, project)
    status = _move(src, dest)
    if status == ERROR:
        _error('Failed to copy %s to %s' % (project, dest))
    else:
        _ok('Finished %s' % project)

def main():
    chunks = _split_file_into_chunks(manifest)
    for chunk in chunks:
        _process_chunk(chunk)

try:
    main()
finally:
    print TEMP_DIR
    call(['rm', '-rf', TEMP_DIR])
