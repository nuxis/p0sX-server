import os
import subprocess

def get_release(path=None):
    """
    Get release info from a git repo in the current dir.

    Attempts to derive version from git tag, fallbacks to git commit

    Returns:
        str
    """
    def format_release(string):
        # Sentry does not support / in release names...
        return string.replace('version/', '').replace('/', '_') if isinstance(string, str) else ''

    def _git_command(cmd):
        with open(os.path.devnull, "w+") as null:
            try:
                return (
                    subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=null,
                        stdin=null,
                        cwd=path,
                    ).communicate()[0]
                    .strip()
                    .decode("utf-8")
                )
            except (OSError, IOError):
                return ''
    cmd1 = ["git", "describe", "--tags"]
    cmd2 = ["git", "rev-parse", "--short", "HEAD"]
    ret = _git_command(cmd1) or _git_command(cmd2)
    return format_release(ret)
