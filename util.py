import os
import os.path


def last_line(filename):
    """
    Find and return the last line in the file.
    Very efficient implementation - should be blazing fast even for
    large files.
    """
    if not os.path.exists(filename):
        return None

    try:
        with open(filename, 'rb') as f:
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b"\n":
                f.seek(-2, os.SEEK_CUR)

            last = f.readline()
            return last
    except OSError:
        return None
