import mimetypes
import os
import re
import sys
import tempfile

try:
    import readline
except ImportError:
    readline = None

BUGZ_COMMENT_TEMPLATE = """
BUGZ: ---------------------------------------------------
%s
BUGZ: Any line beginning with 'BUGZ:' will be ignored.
BUGZ: ---------------------------------------------------
"""

DEFAULT_NUM_COLS = 80

#
# Auxiliary functions
#


def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


def raw_input_block():
    """ Allows multiple line input until a Ctrl+D is detected.

    @rtype: string
    """
    target = ''
    while True:
        try:
            line = input()
            target += line + '\n'
        except EOFError:
            return target

#
# This function was lifted from Bazaar 1.9.
#


def terminal_width():
    """Return estimated terminal width."""
    if sys.platform == 'win32':
        return DEFAULT_NUM_COLS
        #return win32utils.get_console_size()[0]
    width = DEFAULT_NUM_COLS
    try:
        import struct
        import fcntl
        import termios
        s = struct.pack('HHHH', 0, 0, 0, 0)
        x = fcntl.ioctl(1, termios.TIOCGWINSZ, s)
        width = struct.unpack('HHHH', x)[1]
    except IOError:
        pass

    if width <= 0:
        try:
            width = int(os.environ['COLUMNS'])
        except:
            pass

    if width <= 0:
        width = DEFAULT_NUM_COLS

    return width


def launch_editor(initial_text, comment_from='', comment_prefix='BUGZ:'):
    """Launch an editor with some default text.

    Lifted from Mercurial 0.9.
    @rtype: string
    """
    (fd, name) = tempfile.mkstemp("bugz")
    f = os.fdopen(fd, "w")
    f.write(comment_from)
    f.write(initial_text)
    f.close()

    editor = (os.environ.get("BUGZ_EDITOR") or os.environ.get("EDITOR"))
    if editor:
        result = os.system("%s \"%s\"" % (editor, name))
        if result != 0:
            raise RuntimeError('Unable to launch editor: %s' % editor)

        new_text = open(name).read()
        new_text = re.sub('(?m)^%s.*\n' % comment_prefix, '', new_text)
        os.unlink(name)
        return new_text

    return ''


def block_edit(comment, comment_from=''):
    editor = (os.environ.get('BUGZ_EDITOR') or os.environ.get('EDITOR'))

    if not editor:
        print(comment + ': (Press Ctrl+D to end)')
        new_text = raw_input_block()
        return new_text

    initial_text = '\n'.join(['BUGZ: %s' % line
                              for line in comment.splitlines()])
    new_text = launch_editor(BUGZ_COMMENT_TEMPLATE % initial_text,
                             comment_from)

    if new_text.strip():
        return new_text
    else:
        return ''
