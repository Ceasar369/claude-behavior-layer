"""hear.py — waiting for a change, heard, never polled.

macOS tells a process when a file is written or another process exits,
through kqueue, in the standard library. until() sleeps until one of those
happens, then asks again. Its deadline is its only clock.

Imported, never run.
"""

import os
import select
import time

# A watched file is opened for its events only, so it never counts as open.
EVENTS = getattr(os, "O_EVTONLY", 0x8000)
WRITTEN = (select.KQ_NOTE_WRITE | select.KQ_NOTE_EXTEND
           | select.KQ_NOTE_DELETE | select.KQ_NOTE_RENAME)
# The watched file itself went: removed, or swapped for a new one.
GONE = select.KQ_NOTE_DELETE | select.KQ_NOTE_RENAME


def until(check, files=(), pids=(), seconds: float = 0) -> bool:
    """Whether check() held before `seconds` ran out.

    It is asked at once, again once the watch is set, then each time a file
    is written or a pid exits. A file missing or a pid already gone is not
    watched: check() already sees it. A file swapped whole for a new one,
    as registry.write_whole swaps it, is followed to the new one.
    """
    if check():
        return True
    kq = select.kqueue()
    fds = {}

    def watch(path) -> None:
        try:
            fd = os.open(path, EVENTS)
        except OSError:
            return
        fds[fd] = path
        kq.control([select.kevent(fd, select.KQ_FILTER_VNODE,
                                  select.KQ_EV_ADD | select.KQ_EV_CLEAR, WRITTEN)], 0)

    try:
        for path in files:
            watch(path)
        for pid in pids:
            try:
                kq.control([select.kevent(int(pid), select.KQ_FILTER_PROC,
                                          select.KQ_EV_ADD | select.KQ_EV_ONESHOT,
                                          select.KQ_NOTE_EXIT)], 0)
            except (OSError, ValueError):
                pass
        if check():
            return True
        deadline = time.time() + seconds
        while (left := deadline - time.time()) > 0:
            heard = kq.control(None, 8, left)
            # A file swapped whole is a new file under its old name. The
            # watch moves to it, or every later swap would go unheard.
            for e in heard:
                if e.filter == select.KQ_FILTER_VNODE and e.fflags & GONE and e.ident in fds:
                    os.close(e.ident)
                    watch(fds.pop(e.ident))
            if heard and check():
                return True
        return check()
    finally:
        for fd in fds:
            os.close(fd)
        kq.close()
