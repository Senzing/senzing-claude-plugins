#!/usr/bin/env python3
# cspell:ignore clearenv execv mqueue pidns unsetenv  (bwrap option names)
"""bwrap wrapper: reconcile mount points that `claude plugin eval` asks for
both as a file and as a directory.

WHY
  `claude plugin eval` writes its own sandbox settings and puts SIX paths in
  denyWrite for the AWS SSO cache -- from Vo = [".aws/sso", ".aws/cli/cache",
  ".aws/boto/cache"] flat-mapped to [<home>/N, <home>/dirname(N)]:
      <home>/.aws/sso  <home>/.aws  <home>/.aws/cli/cache
      <home>/.aws/cli  <home>/.aws/boto/cache  <home>/.aws/boto
  None of them exist in its throwaway HOME, so @anthropic-ai/sandbox-runtime
  plans, for each, a mount at the FIRST MISSING COMPONENT of the path -- which
  is `<home>/.aws` for all six. For the three deeper paths it mounts an empty
  read-only DIRECTORY there; for `<home>/.aws` itself it mounts /dev/null, a
  FILE. bwrap creates the mount point for the first one (a directory) and then
  dies on the second:
      bwrap: Can't create file at <home>/.aws: Is a directory
  Stacking several directory mounts on one point is fine (bwrap 0.8.0); only the
  file/directory mix is fatal.

WHAT THIS DOES
  Where one mount point is the target of both directory-sourced and
  file-sourced bind mounts, the file-sourced ones are re-pointed at an empty
  read-only directory, and the bind is forced to its read-only variant
  (--bind -> --ro-bind) regardless of what the runtime emitted. Nothing is
  dropped and no deny is weakened: an empty directory bound read-only over
  <home>/.aws blocks reads, writes and the creation of anything beneath it,
  exactly as the /dev/null mask intended.
  If the argument vector contains anything this does not understand, it is
  passed through untouched.
"""
import os, sys, tempfile

ARITY = {
    "--bind": 2, "--bind-try": 2, "--dev-bind": 2, "--dev-bind-try": 2,
    "--ro-bind": 2, "--ro-bind-try": 2, "--symlink": 2, "--bind-data": 2,
    "--ro-bind-data": 2, "--file": 2, "--setenv": 2,
    "--perms": 1, "--size": 1, "--tmpfs": 1, "--dir": 1, "--dev": 1,
    "--proc": 1, "--mqueue": 1, "--overlay-src": 1, "--chdir": 1,
    "--hostname": 1, "--uid": 1, "--gid": 1, "--userns": 1, "--userns2": 1,
    "--pidns": 1, "--seccomp": 1, "--add-seccomp-fd": 1, "--sync-fd": 1,
    "--block-fd": 1, "--userns-block-fd": 1, "--info-fd": 1,
    "--json-status-fd": 1, "--args": 1, "--argv0": 1, "--exec-label": 1,
    "--file-label": 1, "--cap-add": 1, "--cap-drop": 1, "--unsetenv": 1,
    "--remount-ro": 1,
    "--unshare-all": 0, "--share-net": 0, "--unshare-user": 0,
    "--unshare-user-try": 0, "--unshare-ipc": 0, "--unshare-pid": 0,
    "--unshare-net": 0, "--unshare-uts": 0, "--unshare-cgroup": 0,
    "--unshare-cgroup-try": 0, "--disable-userns": 0,
    "--assert-userns-disabled": 0, "--clearenv": 0, "--new-session": 0,
    "--die-with-parent": 0, "--as-pid-1": 0, "--level-prefix": 0,
    "--version": 0, "--help": 0,
}
BIND = ("--bind", "--bind-try", "--dev-bind", "--dev-bind-try",
        "--ro-bind", "--ro-bind-try")
DIR_MOUNT = ("--tmpfs", "--dir", "--dev", "--proc", "--mqueue")

argv = sys.argv[1:]
real = os.environ.get("BWRAP_REAL", "/usr/bin/bwrap.real")


def scan(a):
    """[(index, opt, operands)] for options before `--`; None if unparsable."""
    ops, i = [], 0
    while i < len(a) and a[i].startswith("--") and a[i] != "--":
        opt = a[i]
        if opt not in ARITY:
            return None
        n = ARITY[opt]
        if i + n > len(a) - 1:
            return None
        ops.append((i, opt, a[i + 1:i + 1 + n]))
        i += 1 + n
    return ops


ops = scan(argv)
if ops is not None:
    kinds = {}          # dest -> set of "dir"/"file"
    for _, opt, operand in ops:
        if opt in BIND:
            src, dest = operand
            try:
                kinds.setdefault(dest, set()).add(
                    "dir" if os.path.isdir(src) else "file")
            except OSError:
                pass
        elif opt in DIR_MOUNT:
            kinds.setdefault(operand[0], set()).add("dir")
    mixed = {d for d, k in kinds.items() if len(k) > 1}
    if mixed:
        empty = tempfile.mkdtemp(prefix="bwrap-shim-empty-")
        os.chmod(empty, 0o555)
        fixed = []
        RO = {"--bind": "--ro-bind", "--bind-try": "--ro-bind-try",
              "--dev-bind": "--ro-bind", "--dev-bind-try": "--ro-bind-try"}
        for i, opt, operand in ops:
            if opt in BIND and operand[1] in mixed and not os.path.isdir(operand[0]):
                argv[i + 1] = empty
                # A file mask exists to deny; the replacement must be read-only on
                # the MOUNT, not just by the directory's mode bits — a root process
                # in the sandbox ignores mode bits. Force the ro variant whatever
                # the runtime emitted (today it emits --ro-bind; do not rely on it).
                argv[i] = RO.get(opt, opt)
                fixed.append(operand[1])
        sys.stderr.write(
            "[bwrap-shim] re-pointed %d file mask(s) at an empty read-only "
            "directory because the same mount point is also mounted as a "
            "directory: %s\n" % (len(fixed), ", ".join(sorted(set(fixed)))))

os.execv(real, [real] + argv)
