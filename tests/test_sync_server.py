import pytest

from sync_server.account import ADMIN, MEMBER
from sync_server.accounts import Accounts
from sync_server.devices import FAILURES_ALLOWED, LOCKOUT_SECONDS, Devices
from sync_server.protocol import MIGRATION_HEADER, PROTOCOL, PROTOCOL_HEADER, VERSION_HEADER
from sync_server.refusal import Refusal
from sync_server.db.account_rows import AccountRows
from sync_server.db.device_rows import DeviceRows
from sync_server.db.failed_login_rows import FailedLoginRows
from sync_server.db.server_schema import MIGRATIONS, ServerSchema
from sync_server.db.item_rows import ItemRows
from sync_server.db.item_version_rows import ItemVersionRows
from sync_server.db.store import Store
from sync_server.file_store import FileStore

PASSWORD = "correct horse battery"


def people(store: Store) -> tuple[Accounts, Devices]:
    accounts = Accounts(AccountRows(store))
    return accounts, Devices(DeviceRows(store), FailedLoginRows(store), accounts)


@pytest.fixture
def store(tmp_path) -> Store:
    store = Store(tmp_path / "team.db")
    ServerSchema(store).migrated()
    yield store
    store.close()


def test_the_library_tables_hold_an_item_and_its_versions_and_refuse_a_second_of_one_name_or_number(store):
    import sqlite3
    items, versions = ItemRows(store), ItemVersionRows(store)
    item = items.insert("sequence", "release", "How a release goes", 1, 10.0)
    assert items.item_row("sequence", "release")["description"] == "How a release goes" and [row["id"] for row in items.listed()] == [item]
    version = versions.insert(item, 1, '{"steps": []}', "abc", "4.67.0", "first", 1, 11.0)
    assert versions.complete(item) == [] and versions.highest_number(item) == 1, "a version is listed only once complete"
    versions.mark_complete(version, 12.0)
    assert [row["number"] for row in versions.complete(item)] == [1]
    with pytest.raises(sqlite3.IntegrityError):
        items.insert("sequence", "release", "again", 2, 13.0)
    with pytest.raises(sqlite3.IntegrityError):
        versions.insert(item, 1, "{}", "def", "4.67.0", "again", 2, 14.0)


def library_of(store, tmp_path):
    from sync_server.library import Library
    return Library(store, ItemRows(store), ItemVersionRows(store), FileStore(tmp_path / "files"))


def test_the_library_publishes_versions_of_a_name_only_its_publisher_or_an_admin_changes_and_withdraws(store, tmp_path):
    from sync_server.account import Account
    library = library_of(store, tmp_path)
    ada, bob, admin = Account(1, "ada@x", "Ada", MEMBER), Account(2, "bob@x", "Bob", MEMBER), Account(3, "eve@x", "Eve", ADMIN)
    library.publish(ada, "sequence", "release", "How a release goes", '{"steps": 1}', "4.67.0", "first", 10.0)
    library.publish(ada, "sequence", "release", "How a release goes", '{"steps": 2}', "4.67.0", "second", 12.0)
    [entry] = library.listed("sequence", "release")
    assert entry.version.number == 2 and library.numbered_version("sequence", "release", 1).body == '{"steps": 1}', "a publish adds a version and never changes one"
    with pytest.raises(Refusal):
        library.publish(bob, "sequence", "release", "mine now", "{}", "4.67.0", "taken", 14.0)
    with pytest.raises(Refusal):
        library.withdraw(bob, "sequence", "release", 14.0)
    library.withdraw(admin, "sequence", "release", 15.0)
    assert library.listed(None, None) == [] and library.latest_version("sequence", "release").number == 2, "a withdrawn item leaves the list and stays readable"
    library.publish(ada, "sequence", "release", "How a release goes", "{}", "4.67.0", "back", 16.0)
    assert [e.version.number for e in library.listed(None, "release")] == [3], "a new version of a withdrawn item lists it again"
    assert library.listed("template", None) == [] and library.listed(None, "nothing like it") == []


def test_a_version_naming_files_is_listed_once_its_publisher_sent_each_with_its_hash(store, tmp_path):
    import hashlib
    import json
    from sync_server.account import Account
    library = library_of(store, tmp_path)
    ada, bob = Account(1, "ada@x", "Ada", MEMBER), Account(2, "bob@x", "Bob", MEMBER)
    files = {"SKILL.md": b"# Release", "scripts/check.sh": b"exit 0"}
    body = json.dumps({"files": {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}})
    library.publish(ada, "skill", "release", "Releasing", body, "4.67.0", "first", 10.0)
    with pytest.raises(Refusal):
        library.file_received(bob, "skill", "release", 1, "SKILL.md", files["SKILL.md"], 11.0)
    with pytest.raises(Refusal):
        library.file_received(ada, "skill", "release", 1, "SKILL.md", b"something else", 11.0)
    with pytest.raises(Refusal):
        library.file_received(ada, "skill", "release", 1, "extra.txt", b"x", 11.0)
    assert not library.file_received(ada, "skill", "release", 1, "SKILL.md", files["SKILL.md"], 11.0).is_complete()
    assert library.listed(None, None) == [], "a version is listed only once every file it names is in"
    assert library.file_received(ada, "skill", "release", 1, "scripts/check.sh", files["scripts/check.sh"], 12.0).is_complete()
    assert library.item_file("skill", "release", 1, "scripts/check.sh") == b"exit 0" and [e.item.name for e in library.listed(None, None)] == ["release"]
    assert library.file_received(ada, "skill", "release", 1, "SKILL.md", files["SKILL.md"], 13.0).is_complete(), "the same file sent again is harmless"


def test_a_publish_sent_again_gets_its_waiting_version_back_and_one_left_waiting_a_day_is_cleared(store, tmp_path):
    import hashlib
    import json
    from sync_server.account import Account
    from sync_server.library import INCOMPLETE_SECONDS
    library = library_of(store, tmp_path)
    ada = Account(1, "ada@x", "Ada", MEMBER)
    body = json.dumps({"files": {"SKILL.md": hashlib.sha256(b"# Release").hexdigest()}})
    first = library.publish(ada, "skill", "release", "Releasing", body, "4.67.0", "first", 10.0)
    assert library.publish(ada, "skill", "release", "Releasing", body, "4.67.0", "first", 20.0) == first, "a dropped POST sent again gets the waiting version back"
    library.file_received(ada, "skill", "release", 1, "SKILL.md", b"# Release", 21.0)
    other = json.dumps({"files": {"SKILL.md": hashlib.sha256(b"# Two").hexdigest()}})
    waiting = library.publish(ada, "skill", "release", "Releasing", other, "4.67.0", "second", 30.0)
    assert waiting.number == 2 and not waiting.is_complete()
    again = library.publish(ada, "skill", "release", "Releasing", json.dumps({"steps": 3}), "4.67.0", "third", 30.0 + INCOMPLETE_SECONDS)
    assert again.number == 2 and again.is_complete(), "a version left waiting a day is cleared, and its number goes to the next"


def test_the_library_routes_publish_take_files_list_and_read_over_http_with_a_token_on_each(tmp_path):
    import hashlib
    import json
    import urllib.error
    import urllib.request
    from sync_server.team_server import TeamServer

    team = TeamServer(tmp_path)
    team.accounts.create("ada@example.com", "Ada", PASSWORD, ADMIN, 1.0)
    _, token = team.devices.login("ada@example.com", PASSWORD, "laptop", "127.0.0.1", 1.0)
    server = team.started("127.0.0.1", 0)
    address = f"http://127.0.0.1:{server.server_address[1]}"

    def call(method: str, path: str, body: bytes | None = None, signed: bool = True) -> tuple[int, bytes]:
        headers = {PROTOCOL_HEADER: str(PROTOCOL), VERSION_HEADER: "4.68.0", **({"Authorization": f"Bearer {token}"} if signed else {})}
        request = urllib.request.Request(f"{address}{path}", data=body, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=10) as answer:
                return answer.status, answer.read()
        except urllib.error.HTTPError as refused:
            return refused.code, refused.read()

    try:
        status, summary = call("GET", "/library", signed=False)
        assert status == 200 and json.loads(summary)["has_admin"] is True and json.loads(summary)["role"] == "", "the library answers who it is before login"
        assert json.loads(call("GET", "/library")[1])["role"] == ADMIN
        data = b"# Release"
        body = json.dumps({"files": {"SKILL.md": hashlib.sha256(data).hexdigest()}})
        status, published = call("POST", "/items/skill/release", json.dumps({"description": "Releasing", "body": body, "note": "first"}).encode())
        assert status == 200 and json.loads(published)["number"] == 1 and json.loads(published)["lowest_version"] == "4.68.0", "the lowest version is the publisher's own"
        assert json.loads(call("GET", "/items")[1])["items"] == [], "a version waiting for its file is not listed"
        assert call("PUT", "/items/skill/release/1/files/SKILL.md", data)[0] == 200
        [entry] = json.loads(call("GET", "/items?type=skill&search=releas")[1])["items"]
        assert entry["item"]["name"] == "release" and entry["version"]["number"] == 1
        assert call("GET", "/items/skill/release/1/files/SKILL.md") == (200, data)
        assert json.loads(call("GET", "/items/skill/release")[1])["versions"][0]["note"] == "first"
        assert call("GET", "/items/skill/missing")[0] == 404, "a missing item is not found"
        assert call("GET", "/items", signed=False)[0] == 403, "every other route needs the device token"
        assert call("POST", "/items/skill/release/withdraw", b"{}")[0] == 200 and json.loads(call("GET", "/items")[1])["items"] == []
        assert [call("POST", path, b"{}")[0] for path in ("/push", "/blocks", "/leases/take")] + [call("GET", path)[0] for path in ("/pull", "/copy", "/team")] == [404] * 6, "a route of the old row sync answers 404"
    finally:
        team.close(server)


def test_the_library_takes_only_known_kinds_and_names_and_file_paths_that_stay_in_their_folder(store, tmp_path):
    import hashlib
    import json
    from sync_server.account import Account
    from sync_server.item_file_place import ItemFilePlace
    library = library_of(store, tmp_path)
    ada = Account(1, "ada@x", "Ada", MEMBER)
    for item_type, name in (("virus", "x"), ("skill", "../up"), ("skill", "a/b"), ("skill", ""), ("skill", ".hidden")):
        with pytest.raises(Refusal):
            library.publish(ada, item_type, name, "d", "{}", "4.67.0", "n", 1.0)
    for file_name in ("../escape", "/etc/passwd", "a/../../b", "", "a//b"):
        with pytest.raises(Refusal):
            ItemFilePlace("skill", "release", 1, file_name).checked()
    nested = b"exit 0"
    library.publish(ada, "skill", "release", "d", json.dumps({"files": {"scripts/check.sh": hashlib.sha256(nested).hexdigest()}}), "4.67.0", "n", 1.0)
    assert library.file_received(ada, "skill", "release", 1, "scripts/check.sh", nested, 2.0).is_complete(), "a skill's nested file is kept in its folder"


def test_the_library_caps_a_versions_files_and_refuses_a_body_that_is_no_json_object(store, tmp_path, monkeypatch):
    import json
    import sync_server.library as library_module
    from sync_server.account import Account
    library = library_of(store, tmp_path)
    ada = Account(1, "ada@x", "Ada", MEMBER)
    with pytest.raises(Refusal, match="JSON object"):
        library.publish(ada, "skill", "release", "d", "not json", "4.67.0", "n", 1.0)
    many = json.dumps({"files": {f"f{n}.md": "x" for n in range(library_module.VERSION_FILE_COUNT_LIMIT + 1)}})
    with pytest.raises(Refusal, match="at most"):
        library.publish(ada, "skill", "release", "d", many, "4.67.0", "n", 1.0)
    import hashlib
    monkeypatch.setattr(library_module, "VERSION_BYTE_LIMIT", 10)
    big = b"x" * 11
    library.publish(ada, "skill", "release", "d", json.dumps({"files": {"big.md": hashlib.sha256(big).hexdigest()}}), "4.67.0", "n", 1.0)
    with pytest.raises(Refusal, match="more than"):
        library.file_received(ada, "skill", "release", 1, "big.md", big, 2.0)


def test_a_server_backup_keeps_the_librarys_item_files_and_a_restore_puts_them_back(tmp_path):
    from sync_server.item_file_place import ITEMS_FOLDER
    from sync_server.server_backups import ServerBackups
    store = Store(tmp_path / "team.db")
    ServerSchema(store).migrated()
    items = tmp_path / "files" / ITEMS_FOLDER
    (items / "skill" / "release" / "1").mkdir(parents=True)
    (items / "skill" / "release" / "1" / "SKILL.md").write_text("# Release")
    backups = ServerBackups(store, tmp_path / "backups", items)
    copy = backups.written("before-move")
    (items / "skill" / "release" / "1" / "SKILL.md").write_text("lost")
    backups.restored(copy)
    assert (items / "skill" / "release" / "1" / "SKILL.md").read_text() == "# Release", "the item files come back with the database"
    store.close()


def test_the_server_migrates_its_own_schema_once_and_keeps_its_version(tmp_path):
    store = Store(tmp_path / "team.db")
    assert ServerSchema(store).migrated() == len(MIGRATIONS)
    assert ServerSchema(store).migrated() == len(MIGRATIONS), "a second start migrates nothing"
    store.close()


def test_a_new_team_server_draws_its_key_once_and_one_from_before_keys_is_given_one(tmp_path):
    from sync_server.db.team_detail_rows import TeamDetailRows
    from sync_server.team_server import TeamServer
    for name in ("first", "second", "old"):
        (tmp_path / name).mkdir()
    first, second = TeamServer(tmp_path / "first"), TeamServer(tmp_path / "second")
    keys = [team.details.key() for team in (first, second)]
    assert all(len(key) == 32 for key in keys) and keys[0] != keys[1], "each new server draws a key of its own"
    ServerSchema(first.store).migrated()
    assert first.details.key() == keys[0], "a second start draws nothing anew"
    old = Store(tmp_path / "old" / "team.db")
    old.script("CREATE TABLE schema_version (number INTEGER NOT NULL)")
    before_keys = next(number for number, script in enumerate(MIGRATIONS) if "'key'" in script)
    for script in MIGRATIONS[:before_keys]:
        old.script(script)
    old.execute("INSERT INTO schema_version (number) VALUES (?)", (before_keys,))
    ServerSchema(old).migrated()
    assert len(TeamDetailRows(old).value("key")) == 32, "a server from before keys is given one"
    for store in (first.store, second.store, old):
        store.close()


def test_a_person_logs_in_a_device_which_can_be_revoked_and_a_wrong_password_is_refused(store):
    accounts, devices = people(store)
    admin = accounts.create("Ada@Example.com", "Ada", PASSWORD, ADMIN, 1.0)
    assert admin.is_admin() and admin.email == "ada@example.com" and not accounts.is_empty()
    with pytest.raises(Refusal, match="at least"):
        accounts.create("bob@example.com", "Bob", "short", MEMBER, 1.0)
    with pytest.raises(Refusal, match="has no upper case and no digits and no symbols"):
        accounts.create("bob@example.com", "Bob", "lowercaseonly", MEMBER, 1.0)
    with pytest.raises(Refusal, match="never holds the name of its email"):
        accounts.create("bob@example.com", "Bob", "Bob-Strong-2026", MEMBER, 1.0)
    assert accounts.create("carol@example.com", "Carol", "Tr1cky-pass!", MEMBER, 1.0).email == "carol@example.com", "twelve characters of three kinds is enough"
    with pytest.raises(Refusal, match="already has an account"):
        accounts.create("ada@example.com", "Ada again", PASSWORD, MEMBER, 1.0)
    device, token = devices.login("ada@example.com", PASSWORD, "laptop", "10.0.0.1", 2.0)
    assert devices.person(token) == admin and device.name == "laptop"
    assert DeviceRows(store).with_token_hash(token) is None and DeviceRows(store).with_token_hash(Devices.token_hash(token)) is not None, "the token is kept only as a hash"
    with pytest.raises(Refusal, match="email or the password is wrong"):
        devices.login("ada@example.com", "not the password", "phone", "10.0.0.2", 3.0)
    devices.revoke(device.id, 4.0)
    with pytest.raises(Refusal, match="revoked"):
        devices.person(token)
    with pytest.raises(Refusal, match="not known"):
        devices.person("made up")


def test_too_many_failed_logins_from_one_address_shut_it_out_for_a_while(store):
    accounts, devices = people(store)
    accounts.create("ada@example.com", "Ada", PASSWORD, ADMIN, 1.0)
    for attempt in range(FAILURES_ALLOWED):
        with pytest.raises(Refusal):
            devices.login("ada@example.com", "guess", "laptop", "10.0.0.9", 10.0 + attempt)
    with pytest.raises(Refusal, match="too many failed logins"):
        devices.login("ada@example.com", PASSWORD, "laptop", "10.0.0.9", 20.0)
    assert devices.login("ada@example.com", PASSWORD, "laptop", "10.0.0.8", 20.0)[1], "another address is not shut out"
    assert devices.login("ada@example.com", PASSWORD, "laptop", "10.0.0.9", 20.0 + LOCKOUT_SECONDS)[1], "the address may try again once the while is over"


def test_a_journal_and_a_team_server_on_different_protocols_are_refused_with_the_side_to_upgrade(tmp_path, monkeypatch, connection):
    from journal.config import Config
    from journal.db.schema import Schema
    from journal.models.all_models import AllModels
    from journal.sync.team_refusal import TeamRefusal
    from journal.features.library.support.library_account import LibraryAccount
    from journal.features.library.support.library_link import LibraryLink
    from sync_server.team_server import TeamServer

    server = TeamServer(tmp_path).started("127.0.0.1", 0)
    address = f"http://127.0.0.1:{server.server_address[1]}"
    config = Config(tmp_path / "journal")
    config.home.mkdir(parents=True)
    link = LibraryLink(LibraryAccount(config), Schema(connection, AllModels.MODELS))
    try:
        assert link.summary(address) is not None, "a journal on the server's protocol is answered"
        monkeypatch.setattr("journal.features.library.support.library_link.PROTOCOL", PROTOCOL - 1)
        with pytest.raises(TeamRefusal, match="upgrade the journal with journal update apply"):
            link.summary(address)
        monkeypatch.setattr("journal.features.library.support.library_link.PROTOCOL", PROTOCOL + 1)
        with pytest.raises(TeamRefusal, match="upgrade the team server's image"):
            link.summary(address)
    finally:
        server.shutdown()
        server.server_close()


def test_the_proxy_in_front_passes_every_path_the_team_server_answers():
    import re
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    answered = set(re.findall(r'"(/[a-z/]+)": lambda', (root / "src/sync_server/team_request_handler.py").read_text()))
    passed = re.search(r"@sync path (.+)", (root / "docker/team-server/routes.caddy").read_text()).group(1).split()
    missing = [path for path in answered if path not in passed and not any(rule.endswith("/*") and path.startswith(rule[:-1]) for rule in passed)]
    assert answered and missing == [], f"the proxy sends these to the hosted journal instead: {missing}"
    routes = (root / "docker/team-server/routes.caddy").read_text()
    assert "@unmarked not header X-Journal-Protocol *" in routes and "respond @unmarked 404" in routes, "a team server path without the journal's protocol header is turned away at the proxy"


def test_a_person_changes_their_own_password_and_an_admin_resets_a_members(tmp_path):
    from sync_server.team_server import TeamServer
    team = TeamServer(tmp_path)
    ada = team.accounts.create("ada@example.com", "Ada", PASSWORD, ADMIN, 1.0)
    bob = team.accounts.create("bob@example.com", "Bob", PASSWORD, MEMBER, 1.0)
    _, ada_token = team.devices.login("ada@example.com", PASSWORD, "laptop", "127.0.0.1", 1.0)
    _, bob_token = team.devices.login("bob@example.com", PASSWORD, "laptop", "127.0.0.2", 1.0)
    with pytest.raises(Refusal, match="email or the password is wrong"):
        team.accounts.password_changed(bob, "not mine", "Another-pass-2026")
    with pytest.raises(Refusal, match="at least"):
        team.accounts.password_changed(bob, PASSWORD, "weak")
    team.accounts.password_changed(bob, PASSWORD, "Another-pass-2026")
    assert team.devices.login("bob@example.com", "Another-pass-2026", "phone", "127.0.0.3", 2.0), "the new password signs in"
    with pytest.raises(Refusal, match="no admin"):
        team.admins.password_reset(bob_token, ada.id)
    fresh = team.admins.password_reset(ada_token, bob.id).password
    assert len(fresh) == 22 and team.devices.login("bob@example.com", fresh, "tablet", "127.0.0.4", 3.0), "an admin's reset gives a new password that signs in"
    team.store.close()


