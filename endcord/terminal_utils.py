import fcntl
import os
import shutil
import sys
import termios
import time
import tty

KEY_CODES = {   # from curses for consistency
    b"\x1b[A": 259,  # UP
    b"\x1b[B": 258,  # DOWN
    b"\x1b[D": 260,  # LEFT
    b"\x1b[C": 261,  # RIGHT
    b"\x1b[H": 262,  # HOME
    b"\x1b[F": 360,  # END
    b"\x1b[5~": 339, # PG_UP
    b"\x1b[6~": 338, # PG_DOWN
    b"\x1b[3~": 330, # DELETE
    b"\x1b[2~": 331, # INSERT
}

STDIN_FD = sys.stdin.fileno()
OLD_TERM = termios.tcgetattr(STDIN_FD)

width = 0
height = 0


def enter_tui():
    """Enter tui terminal mode"""
    tty.setcbreak(STDIN_FD)
    sys.stdout.write(
        "\x1b[?1049h"   # alternate screen
        "\x1b[?7l"      # disable line wrap
        "\x1b[2J"       # clear screen
        "\x1b[?25l"     # hide curso
        "\x1b[H",       # cursor home
    )
    sys.stdout.flush()


def leave_tui():
    """Leave tui terminal mode"""
    sys.stdout.write(
        "\x1b[?1049l"   # leave alternate screen
        "\x1b[?7h"      # enable line wrap
        "\x1b[?25h"     # show cursor
        "\x1b[0m",      # reset attrs
    )
    sys.stdout.flush()
    termios.tcsetattr(STDIN_FD, termios.TCSADRAIN, OLD_TERM)


def get_size():
    """Get size of terminal in characters (h, w)"""
    size = shutil.get_terminal_size()
    return size.lines, size.columns


def draw(lines):
    """Draw lines on screen"""
    sys.stdout.write("\x1b[H")   # cursor home
    sys.stdout.write(lines)
    sys.stdout.flush()


def read_key():
    """Blocking read key, return key code like curses.getch(), alt sequences are not handled"""
    fd = sys.stdin.fileno()
    old_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    try:
        # wait for first byte
        first = os.read(fd, 1)

        # using O_NONBLOCK instead select() for windows compatibility
        fcntl.fcntl(fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)

        # backspace
        if first == b"\x7f":
            return 263

        # single code
        if first != b"\x1b":
            return KEY_CODES.get(first, ord(first))

        # escape sequences
        seq = first
        start = time.time()
        while time.time() - start < 0.01:   # 10ms timeout
            try:
                byte = os.read(fd, 1)
                if not byte:
                    time.sleep(0.001)
                    continue
                seq += byte
                if seq in KEY_CODES:
                    return KEY_CODES[seq]
                if len(seq) > 6:
                    break
            except BlockingIOError:
                time.sleep(0.001)

        return 27

    finally:
        fcntl.fcntl(fd, fcntl.F_SETFL, old_flags)


run_esc_detector = False

def esc_detector():
    """A function to be ran in a thread that waits for esc key then exits"""
    global run_esc_detector
    run_esc_detector = True
    fd = sys.stdin.fileno()
    old_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    try:
        fcntl.fcntl(fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)
        while run_esc_detector:
            try:
                byte = os.read(fd, 1)
                if not byte:
                    time.sleep(0.01)
                elif byte == b"\x1b":
                    run_esc_detector = False
                else:
                    time.sleep(0.01)
            except BlockingIOError:
                time.sleep(0.01)
    finally:
        fcntl.fcntl(fd, fcntl.F_SETFL, old_flags)


def stop_esc_detector():
    """Stop esc detector thread"""
    global run_esc_detector
    run_esc_detector = False
