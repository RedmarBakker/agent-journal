from test_features import *  # noqa
from replay import tick_after, drive_the_clock, catch_typed


def test_zz_debug(app: App, monkeypatch, tmp_path):
    from journal.repositories.command_outputs import CommandOutputs
    keystrokes = []
    catch_typed(app, monkeypatch, keystrokes)
    drive_the_clock(app, monkeypatch)
    hook(app, "SessionStart")
    app.console().run(["environment", "overview"], AGENT)
    folder = app.config.root / "c1"
    folder.mkdir()
    outputs = app.container.get(CommandOutputs)
    ShellVerbs(app).split("python3 -m pytest -q", str(folder))
    ShellVerbs(app).moved("c1", "python3 -m pytest -q", str(folder / "out"))
    active = outputs.chain_output("c1")
    a = tick_after(app, 360.0)
    b = tick_after(app, 370.0)
    from journal.features.shell.support.shell_data import ShellData
    assert False, f"answers {a!r} {b!r} typed {keystrokes!r} background {[o.id for o in outputs.background('s1')]!r} active {active!r}"
