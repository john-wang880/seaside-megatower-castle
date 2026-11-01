"""Small native local-file leases and optional metrics; no Blender import."""
import contextlib
import os
from pathlib import Path
import sys

class LeaseError(RuntimeError):
    pass

def require_normal_python():
    if sys.flags.optimize:
        raise RuntimeError('Optimized Python (-O/-OO) is unsupported: frozen checks require assertions')

def execution_lock_path():
    # Stable across output directories and copies of this tool for the same user.
    if sys.platform == 'win32':
        base = os.environ.get('LOCALAPPDATA')
        if not base:
            raise LeaseError('LOCALAPPDATA unavailable; cannot establish stable execution lease')
        root = Path(base)
    elif os.name == 'posix':
        root = Path(os.environ.get('XDG_CACHE_HOME', str(Path.home() / '.cache')))
        if not root.is_absolute():
            raise LeaseError('XDG_CACHE_HOME must be absolute')
    else:
        raise LeaseError('Unsupported native locking platform')
    return root / 'castle-portable-render' / 'execution.lock'

@contextlib.contextmanager
def exclusive_lock(path):
    path = Path(path)
    if path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction()):
        raise LeaseError('Refusing redirected lockfile')
    path.parent.mkdir(parents=True, exist_ok=True)
    # Never truncate, unlink or replace the stable lease file.
    handle = path.open('a+b')
    acquired = False
    try:
        if os.fstat(handle.fileno()).st_size == 0:
            handle.write(b'\0'); handle.flush(); os.fsync(handle.fileno())
        handle.seek(0)
        if sys.platform == 'win32':
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        elif os.name == 'posix':
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        else:
            raise LeaseError('Unsupported native locking platform')
        acquired = True
        yield handle
    except OSError as exc:
        raise LeaseError('Lease unavailable or operation failed; no lock bypass: ' + str(path)) from exc
    finally:
        try:
            if acquired:
                handle.seek(0)
                if sys.platform == 'win32':
                    import msvcrt
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally:
            handle.close()

def optional_metrics():
    affinity = rss = None
    try:
        affinity = sorted(os.sched_getaffinity(0))
    except (AttributeError, OSError):
        pass
    if sys.platform == 'linux':
        try:
            import resource
            rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        except Exception:
            pass
    return {'affinity_logical_cpus': affinity, 'peak_rss_linux_kib': rss}
