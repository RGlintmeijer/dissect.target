import pytest

from dissect.target.plugins.os.unix.linux.proc import ProcPlugin, ProcProcess


def test_process(target_unix_users, fs_unix_proc):
    target_unix_users.add_plugin(ProcPlugin)

    process = target_unix_users.proc.process(1)
    assert type(process) == ProcProcess
    assert process.pid == 1
    assert process.name == "systemd"
    assert process.parent.name == "swapper"
    assert process.ppid == 0
    assert process.state == "Sleeping"
    assert str(process.runtime) == "1 day, 13:19:27.970000"
    assert process.starttime.isoformat() == "2023-04-03T22:10:54.300000+00:00"

    environ = list(process.environ())
    assert environ[0].variable == b"VAR"
    assert environ[0].contents == b"1"


def test_process_not_found(target_unix_users, fs_unix_proc):
    target_unix_users.add_plugin(ProcPlugin)
    with pytest.raises(ProcessLookupError) as exc:
        target_unix_users.proc.process(404)
    assert str(exc.value) == f"Process with PID 404 could not be found on target: {target_unix_users}"


def test_processes(target_unix_users, fs_unix_proc):
    target_unix_users.add_plugin(ProcPlugin)

    for process in target_unix_users.proc.processes():
        assert process.pid in (1, 2, 3, 1337)
        assert process.state in ("Sleeping", "Paging", "Running", "Wakekill")
        assert process.name in ("systemd", "kthread", "acquire", "sshd")
        assert process.starttime.isoformat() == "2023-04-03T22:10:54.300000+00:00"
        assert str(process.runtime) == "1 day, 13:19:27.970000"

        for env in process.environ():
            assert env.variable == b"VAR"
            assert env.contents == b"1"
