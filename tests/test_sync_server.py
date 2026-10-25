import pytest

from sync_server.account import ADMIN, MEMBER
from sync_server.accounts import Accounts
from sync_server.change_log import ChangeLog
from sync_server.devices import FAILURES_ALLOWED, LOCKOUT_SECONDS, Devices
from sync_server.hub_doc_rules import HubDocRules
from sync_server.id_ranges import IdRanges
from sync_server.logged_change import LoggedChange
from sync_server.protocol import MIGRATION_HEADER, PROTOCOL, PROTOCOL_HEADER, VERSION_HEADER
from sync_server.refusal import Refusal
from sync_server.stored_row import StoredRow
from sync_server.db.account_rows import AccountRows
from sync_server.db.change_rows import ChangeRows
from sync_server.db.device_rows import DeviceRows
from sync_server.db.failed_login_rows import FailedLoginRows
from sync_server.db.id_block_rows import IdBlockRows
from sync_server.db.row_values import RowValues
from sync_server.db.server_schema import MIGRATIONS, ServerSchema
from sync_server.db.store import Store
from sync_server.db.pool_capacity_rows import PoolCapacityRows
from sync_server.pool_slots import PoolSlots
from sync_server.pull_query import PullQuery

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


def test_the_server_migrates_its_own_schema_once_and_keeps_its_version(tmp_path):
    store = Store(tmp_path / "team.db")
    assert ServerSchema(store).migrated() == len(MIGRATIONS)
    assert ServerSchema(store).migrated() == len(MIGRATIONS), "a second start migrates nothing"
    store.close()


def test_a_new_team_server_draws_its_key_and_a_number_t_below_2_21_once_and_one_claimed_before_keeps_t_0(tmp_path):
    from sync_server.db.team_detail_rows import TeamDetailRows
    from sync_server.team_server import TeamServer
    for name in ("first", "second", "old"):
        (tmp_path / name).mkdir()
    first, second = TeamServer(tmp_path / "first"), TeamServer(tmp_path / "second")
    drawn = [team.details.answer() for team in (first, second)]
    assert all(len(answer.key) == 32 and 0 < answer.number < 2 ** 21 and answer.on_hub for answer in drawn), "a new server draws a key and a number T above 0 and below 2^21, and is on the hub"
    assert drawn[0].key != drawn[1].key, "each server draws its own key"
    ServerSchema(first.store).migrated()
    assert first.details.answer() == drawn[0], "a second start draws nothing anew"
    old = Store(tmp_path / "old" / "team.db")
    old.script("CREATE TABLE schema_version (number INTEGER NOT NULL)")
    before_keys = next(number for number, script in enumerate(MIGRATIONS) if "'key'" in script)
    for script in MIGRATIONS[:before_keys]:
        old.script(script)
    old.execute("INSERT INTO schema_version (number) VALUES (?)", (before_keys,))
    Accounts(AccountRows(old)).create("ada@example.com", "Ada", PASSWORD, ADMIN, 1.0)
    ServerSchema(old).migrated()
    assert TeamDetailRows(old).value("number") == "" and len(TeamDetailRows(old).value("key")) == 32, "a server claimed before stores no number and is given a key"
    old.close()
    reopened = TeamServer(tmp_path / "old")
    assert (reopened.details.answer().number, reopened.details.answer().on_hub) == (0, False), "and reads T = 0, not on the hub until it is moved there"
    for store in (first.store, second.store, reopened.store):
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


def test_the_log_keeps_changes_in_order_with_each_rows_current_value_and_a_device_never_pulls_its_own(store):
    log = ChangeLog(store, ChangeRows(store), RowValues(store))
    first = log.appended(LoggedChange("tasks", 7, "created", "user:1", 1, 1, {"title": "a", "brief": "b"}, {"title": 1.0, "brief": 1.0}))
    second = log.appended(LoggedChange("tasks", 7, "updated", "agent:s", 2, 2, {"title": "c"}, {"title": 2.0}))
    assert (first.sequence, second.sequence, log.head()) == (1, 2, 2)
    assert log.row("tasks", 7) == StoredRow({"title": "c", "brief": "b"}, {"title": 2.0, "brief": 1.0}, {"title": 2, "brief": 1})
    assert [change.sequence for change in log.pull_page(0, 1)] == [2] and [change.sequence for change in log.pull_page(1, 3)] == [2]
    log.appended(LoggedChange("tasks", 7, "deleted", "user:1", 1, 1))
    assert log.row("tasks", 7) is None


def test_number_blocks_never_overlap_start_above_a_shared_journals_numbers_and_of_a_team_of_number_t_from_t_times_2_32(store):
    from sync_server.db.team_detail_rows import TeamDetailRows
    from sync_server.team_details import TeamDetails
    details = TeamDetails(TeamDetailRows(store), ChangeLog(store, ChangeRows(store), RowValues(store)), Accounts(AccountRows(store)))
    ranges, base = IdRanges(store, IdBlockRows(store), details), details.number() << 32
    assert details.number() > 0, "a new server draws its T"
    ranges.raise_floor("tasks", 1450)
    assert ranges.block(1, "tasks", 100) == (base + 1, base + 100), "a team's numbers start at T * 2^32, above the journal's own small ones"
    assert ranges.block(2, "tasks", 100) == (base + 101, base + 200)
    store.execute("DELETE FROM team_details WHERE name = 'number'")
    ranges.raise_floor("messages", 1450)
    ranges.raise_floor("messages", 1200)
    assert ranges.block(1, "messages", 100) == (1451, 1550), "a team from before T, T = 0, numbers as it always has, above a shared journal's numbers"
    assert ranges.block(2, "messages", 100) == (1551, 1650)
    assert ranges.block(1, "links", 1000) == (1, 1000)


def test_a_push_keeps_the_later_edit_of_a_field_puts_times_on_the_servers_clock_and_rejects_the_older(store, tmp_path):
    from sync_server.file_store import FileStore
    from sync_server.push_handler import PushHandler
    from sync_server.host_requests import HostRequests
    from sync_server.db.host_request_rows import HostRequestRows
    from sync_server.push_results import PushResults
    from sync_server.db.push_result_rows import PushResultRows
    from sync_server.push_request import PushRequest
    from sync_server.rejected_field import RejectedField

    accounts, devices = people(store)
    accounts.create("ada@example.com", "Ada", PASSWORD, ADMIN, 1.0)
    accounts.create("bob@example.com", "Bob", PASSWORD, MEMBER, 1.0)
    _, ada = devices.login("ada@example.com", PASSWORD, "ada's laptop", "10.0.0.1", 2.0)
    _, bob = devices.login("bob@example.com", PASSWORD, "bob's laptop", "10.0.0.2", 2.0)
    log = ChangeLog(store, ChangeRows(store), RowValues(store))
    push = PushHandler(store, log, devices, PushResults(PushResultRows(store)), HostRequests(HostRequestRows(store), PoolCapacityRows(store), devices, log), FileStore(tmp_path / "files"), HubDocRules(log, accounts))

    def request(action, actor, fields, seconds, clock_offset=0.0):
        return PushRequest.parsed([{"row_table": "tasks", "row": 7, "action": action, "actor": actor, "fields": fields, "changed_at": {name: seconds for name in fields}}], clock_offset)

    assert push.answer(ada, request("created", "user:1", {"title": "first", "brief": "b"}, 10.0), 11.0).sequences == (1,)
    answer = push.answer(bob, request("updated", "agent:s", {"title": "bob's"}, 120.0, -100.0), 21.0)
    assert (answer.sequences, answer.rejected, answer.server_time) == ((2,), (), 21.0), "bob's clock runs 100 seconds ahead; his edit was made at 20 by the server's"
    older = push.answer(ada, request("updated", "user:1", {"title": "ada's", "brief": "c"}, 15.0), 22.0)
    assert older.rejected == (RejectedField("tasks", 7, "title", "bob's", 20.0, "Bob"),), "the older edit of the title is rejected and sent back with the value that stands and who wrote it"
    assert log.row("tasks", 7) == StoredRow({"title": "bob's", "brief": "c"}, {"title": 20.0, "brief": 15.0}, {"title": 2, "brief": 1}), "the brief, which nobody edited later, is kept"
    push.answer(bob, request("deleted", "user:2", {}, 30.0), 31.0)
    stale = push.answer(ada, request("updated", "user:1", {"title": "too late"}, 40.0), 41.0)
    assert stale.sequences == (0,) and stale.rejected == (RejectedField.deleted_row("tasks", 7),), "an update to a deleted row is dropped and named"
    with pytest.raises(Refusal, match="a person sends only their own writes"):
        push.answer(ada, request("updated", "user:2", {"title": "as bob"}, 50.0), 51.0)
    assert log.head() == 4, "a refused push keeps nothing"


def test_over_http_a_pull_waits_and_wakes_on_a_push_while_other_requests_go_on_and_a_joiner_downloads_a_full_copy(tmp_path):
    import json
    import threading
    import time
    import urllib.error
    import urllib.request

    from sync_server.team_server import TeamServer

    team = TeamServer(tmp_path)
    team.accounts.create("ada@example.com", "Ada", PASSWORD, ADMIN, 1.0)
    team.accounts.create("bob@example.com", "Bob", PASSWORD, MEMBER, 1.0)
    server = team.started("127.0.0.1", 0)
    address = f"http://127.0.0.1:{server.server_address[1]}"

    def call(path, body=None, token=""):
        request = urllib.request.Request(address + path, data=None if body is None else json.dumps(body).encode(), headers={PROTOCOL_HEADER: str(PROTOCOL), **({"Authorization": f"Bearer {token}"} if token else {})})
        try:
            with urllib.request.urlopen(request, timeout=10) as answer:
                return answer.status, json.loads(answer.read())
        except urllib.error.HTTPError as refused:
            return refused.code, json.loads(refused.read())

    try:
        assert call("/login", {"email": "ada@example.com", "password": "wrong", "device_name": "laptop"}) == (403, {"error": "the email or the password is wrong"})
        ada = call("/login", {"email": "ada@example.com", "password": PASSWORD, "device_name": "laptop"})[1]["token"]
        bob = call("/login", {"email": "bob@example.com", "password": PASSWORD, "device_name": "desktop"})[1]["token"]
        assert call("/pull?after=0", token="made up")[0] == 403 and call("/nothing")[0] == 404
        task = {"row_table": "tasks", "row": 7, "action": "created", "actor": "user:1", "fields": {"title": "first"}, "changed_at": {"title": 1.0}}
        assert call("/push", {"changes": [task]}, ada)[1]["settlement"]["sequences"] == [1]
        first = call("/pull?after=0", token=bob)[1]
        assert [change["row"] for change in first["changes"]] == [7] and first["head"] == 1 and first["server_time"] > 0
        assert call("/pull?after=0", token=ada)[1]["changes"] == [], "a device never pulls its own changes"
        waited = {}

        def held_pull():
            began = time.monotonic()
            waited["answer"] = call("/pull?after=1&wait=8", token=bob)[1]
            waited["seconds"] = time.monotonic() - began

        puller = threading.Thread(target=held_pull)
        puller.start()
        time.sleep(0.3)
        began = time.monotonic()
        copy = call("/copy", token=ada)[1]
        assert time.monotonic() - began < 2, "another request is answered while a pull is held"
        assert copy["rows"] == [{"row_table": "tasks", "row": 7, "fields": {"title": "first"}, "changed_at": {"title": 1.0}}] and copy["head"] == 1
        call("/push", {"changes": [{**task, "action": "updated", "fields": {"title": "second"}, "changed_at": {"title": 2.0}}]}, ada)
        puller.join(10)
        assert [change["fields"] for change in waited["answer"]["changes"]] == [{"title": "second"}] and waited["seconds"] < 4, "the held pull answers the moment a change arrives"
        assert team.devices.pulled_sequence(team.devices.device(bob)) == 1, "the sequence a device holds is recorded"
    finally:
        server.shutdown()
        server.server_close()
        team.store.close()


def test_a_stale_offline_edit_to_a_hub_document_that_became_read_only_is_refused_and_sent_back_with_what_stands(store, tmp_path):
    from sync_server.file_store import FileStore
    from sync_server.db.push_result_rows import PushResultRows
    from sync_server.push_handler import PushHandler
    from sync_server.host_requests import HostRequests
    from sync_server.db.host_request_rows import HostRequestRows
    from sync_server.push_request import PushRequest
    from sync_server.push_results import PushResults
    from sync_server.rejected_field import RejectedField

    accounts, devices = people(store)
    accounts.create("ada@example.com", "Ada", PASSWORD, ADMIN, 1.0)
    accounts.create("bob@example.com", "Bob", PASSWORD, MEMBER, 1.0)
    accounts.create("carol@example.com", "Carol", PASSWORD, MEMBER, 1.0)
    _, ada = devices.login("ada@example.com", PASSWORD, "ada's laptop", "10.0.0.1", 2.0)
    _, bob = devices.login("bob@example.com", PASSWORD, "bob's laptop", "10.0.0.2", 2.0)
    _, carol = devices.login("carol@example.com", PASSWORD, "carol's laptop", "10.0.0.3", 2.0)
    log = ChangeLog(store, ChangeRows(store), RowValues(store))
    push = PushHandler(store, log, devices, PushResults(PushResultRows(store)), HostRequests(HostRequestRows(store), PoolCapacityRows(store), devices, log), FileStore(tmp_path / "files"), HubDocRules(log, accounts))

    def send(device, table, row, action, actor, fields, seconds):
        return push.answer(device, PushRequest.parsed([{"row_table": table, "row": row, "action": action, "actor": actor, "fields": fields, "changed_at": {name: seconds for name in fields}}], 0.0), seconds + 1)

    send(ada, "environments", 3, "created", "user:1", {"kind": "hub", "team_name": "acme"}, 1.0)
    send(ada, "environments", 4, "created", "user:1", {"kind": "local", "team_name": "ada-main"}, 1.0)
    send(ada, "docs", 9, "created", "user:1", {"environment_id": 3, "title": "Handbook", "body": "first words", "edit_mode": "free", "owner": 1}, 2.0)
    send(ada, "docs", 8, "created", "user:1", {"environment_id": 4, "title": "Mine", "body": "a personal document", "edit_mode": "local", "owner": 0}, 2.0)
    assert send(bob, "docs", 9, "updated", "user:2", {"body": "Bob's edit made while it was free"}, 3.0).rejected == (), "anyone edits a document free to edit"
    send(ada, "docs", 9, "updated", "user:1", {"edit_mode": "read_only"}, 4.0)
    stale = send(bob, "docs", 9, "updated", "user:2", {"body": "Bob's stale offline edit", "title": "Bob's title"}, 3.5)
    assert {field.field for field in stale.rejected} == {"body", "title"} and stale.sequences == (0,), "a stale edit to a document that became read-only is refused whole and the sender told"
    assert {field.field: field.value for field in stale.rejected} == {"body": "Bob's edit made while it was free", "title": "Handbook"}, "with the values that stand, which the sender puts back in its copy"
    assert log.row("docs", 9).fields["body"] == "Bob's edit made while it was free" and log.row("docs", 9).fields["edit_mode"] == "read_only", "and the server keeps what it held"
    assert [field.field for field in send(bob, "docs", 9, "updated", "user:2", {"edit_mode": "free"}, 5.0).rejected] == ["edit_mode"], "another member does not change who may edit it"
    assert send(carol, "docs", 9, "updated", "user:3", {"body": "Carol, a late joiner"}, 6.0).rejected[0].field == "body", "nor does a member who joined later"
    assert send(ada, "docs", 9, "updated", "user:1", {"body": "the owner edits"}, 7.0).rejected == (), "its owner edits it"
    accounts.create("dan@example.com", "Dan", PASSWORD, ADMIN, 1.0)
    _, dan = devices.login("dan@example.com", PASSWORD, "dan's laptop", "10.0.0.4", 2.0)
    assert send(dan, "docs", 9, "updated", "user:4", {"body": "an admin edits it"}, 8.0).rejected == (), "and so does an admin who is not its owner"
    assert send(bob, "docs", 8, "updated", "user:2", {"body": "outside the hub"}, 9.0).rejected == (), "a document outside the hub is no business of the rules"


def test_a_push_sent_again_after_a_lost_answer_is_kept_once_and_answered_as_the_first_time(store, tmp_path):
    from sync_server.file_store import FileStore
    from sync_server.db.push_result_rows import PushResultRows
    from sync_server.push_handler import PushHandler
    from sync_server.host_requests import HostRequests
    from sync_server.db.host_request_rows import HostRequestRows
    from sync_server.push_request import PushRequest
    from sync_server.push_results import PushResults

    accounts, devices = people(store)
    accounts.create("ada@example.com", "Ada", PASSWORD, ADMIN, 1.0)
    accounts.create("bob@example.com", "Bob", PASSWORD, MEMBER, 1.0)
    _, ada = devices.login("ada@example.com", PASSWORD, "laptop", "10.0.0.1", 2.0)
    _, bob = devices.login("bob@example.com", PASSWORD, "desktop", "10.0.0.2", 2.0)
    log = ChangeLog(store, ChangeRows(store), RowValues(store))
    push = PushHandler(store, log, devices, PushResults(PushResultRows(store)), HostRequests(HostRequestRows(store), PoolCapacityRows(store), devices, log), FileStore(tmp_path / "files"), HubDocRules(log, accounts))

    def request(local_number, actor, title, seconds):
        return PushRequest.parsed([{"row_table": "tasks", "row": 7, "action": "updated", "actor": actor, "fields": {"title": title}, "changed_at": {"title": seconds}, "local_number": local_number}])

    push.answer(bob, request(1, "user:2", "bob's", 20.0), 21.0)
    first = push.answer(ada, request(5, "user:1", "ada's", 10.0), 22.0)
    again = push.answer(ada, request(5, "user:1", "ada's", 10.0), 23.0)
    assert (again.sequences, again.rejected) == (first.sequences, first.rejected) and first.rejected[0].writer == "Bob", "the second answer is the first, rejection and all"
    bob_again = push.answer(bob, request(1, "user:2", "bob's", 20.0), 24.0)
    assert bob_again.sequences == (1,) and bob_again.rejected == () and log.head() == 1, "a change sent twice is kept once and never rejected by itself"
    assert push.answer(ada, request(6, "user:1", "ada's newest", 30.0), 31.0).sequences == (2,), "a new local number is a new change"
    kept = lambda device: [row["local_number"] for row in store.all("SELECT local_number FROM push_results WHERE device_id = ? ORDER BY local_number", (device,))]
    assert kept(devices.device(ada).id) == [6], "a push whose lowest local number is 6 settles every answer below it, which the device can never send again"
    newest_again = push.answer(ada, request(6, "user:1", "ada's newest", 30.0), 32.0)
    assert newest_again.sequences == (2,) and log.head() == 2, "and the answer it may still retry is kept: sent again, it is answered as the first time and stored once"


def test_an_admin_invites_a_person_hands_out_blocks_lists_revokes_and_removes_and_takes_the_first_full_copy(tmp_path):
    import json
    import urllib.error
    import urllib.request

    from sync_server.team_server import TeamServer

    team = TeamServer(tmp_path)
    team.accounts.create("ada@example.com", "Ada", PASSWORD, ADMIN, 1.0)
    server = team.started("127.0.0.1", 0)
    address = f"http://127.0.0.1:{server.server_address[1]}"

    def call(path, body=None, token="", migration=3, version="4.21.0"):
        request = urllib.request.Request(address + path, data=None if body is None else json.dumps(body).encode(), headers={PROTOCOL_HEADER: str(PROTOCOL), MIGRATION_HEADER: str(migration), VERSION_HEADER: version, **({"Authorization": f"Bearer {token}"} if token else {})})
        try:
            with urllib.request.urlopen(request, timeout=10) as answer:
                return answer.status, json.loads(answer.read())
        except urllib.error.HTTPError as refused:
            return refused.code, json.loads(refused.read())

    try:
        for path in ("/invite", "/blocks", "/devices/revoke", "/people/remove", "/upload"):
            assert call(path, {})[0] == 403, f"{path} refuses a request with no token"
        ada = call("/login", {"email": "ada@example.com", "password": PASSWORD, "device_name": "laptop"})[1]["token"]
        upload = {"rows": [{"row_table": "tasks", "row": 1450, "fields": {"title": "from before"}, "changed_at": {"title": 1.0}}], "highest": {"tasks": 1450}, "repository": "", "version": "4.20.0", "migration": 3}
        drawn = {"key": team.details.answer().key, "number": team.details.number(), "on_hub": True, "tied_to_repository": True}
        assert call("/team") == (200, {"repository": "", "has_rows": False, "version": "", "migration": 0, "versions": "exact", "has_admin": True, **drawn, "name": ""}), "anyone may ask what the team holds before joining, whether it has its admin, and its key and T"
        assert call("/upload", {**upload, "repository": "abc123", "team_name": "acme"}, ada) == (200, {"rows": 1, "head": 1})
        assert call("/team") == (200, {"repository": "abc123", "has_rows": True, "version": "4.20.0", "migration": 3, "versions": "exact", "has_admin": True, **drawn, "name": "acme"}), "the first copy pins the team to its journal's version and names the team"
        assert call("/upload", upload, ada)[1]["error"].startswith("the team's journal already holds rows"), "a full copy is taken once"
        base = team.details.number() << 32
        assert call("/blocks", {"tables": ["tasks", "messages"]}, ada)[1]["blocks"] == [{"row_table": "tasks", "first": base + 1, "last": base + 500}, {"row_table": "messages", "first": base + 1, "last": base + 5000}], "blocks start in the team's own number space, above the copy's numbers, and messages get a bigger one"
        invitation = call("/invite", {"email": "Bob@Example.com"}, ada)[1]
        assert invitation["email"] == "bob@example.com" and invitation["code"]
        assert call("/accept", {"code": invitation["code"], "email": "bob@example.com", "name": "Bob", "password": PASSWORD, "password_repeat": "another password", "device_name": "desktop"})[1]["error"].startswith("the two passwords differ")
        assert call("/accept", {"code": invitation["code"], "email": "eve@example.com", "name": "Bob", "password": PASSWORD, "password_repeat": PASSWORD, "device_name": "desktop"})[1]["error"] == "this invitation is for bob@example.com: join with that email", "an invitation is taken up only with the email it was made for"
        bob = call("/accept", {"code": invitation["code"], "email": "Bob@Example.com", "name": "Bob", "password": PASSWORD, "password_repeat": PASSWORD, "device_name": "desktop"})[1]
        assert bob["name"] == "Bob" and bob["account_id"] == 2
        assert call("/team/version", {"version": "4.21.0"}, bob["token"])[0] == 403, "only an admin moves the team's version"
        assert call("/team/version", {"version": "latest"}, ada)[1]["error"].startswith("latest is not a journal version"), "a version is three numbers"
        assert call("/team/version", {"version": "4.21.0"}, ada)[1]["version"] == "4.21.0"
        assert call("/pull?after=0&wait=0", None, bob["token"])[1]["team_version"] == "4.21.0", "every pull names the version the team is pinned to"
        behind = call("/pull?after=0&wait=0", None, bob["token"], migration=2)
        assert behind == (403, {"error": "this journal is on migration 2 and the team on 3: upgrade it to version 4.21.0 with journal update apply; its changes wait here until then"}), "a journal one migration behind the team's rows may not pull"
        assert call("/push", {"changes": []}, bob["token"], migration=2)[0] == 403, "nor push"
        for other in ("4.20.9", "4.21.1"):
            assert call("/pull?after=0&wait=0", None, bob["token"], version=other) == (403, {"error": f"this journal runs {other} and the team 4.21.0: install 4.21.0 with journal update apply; its changes wait here until then"}), "a journal on another version than the team's, older or newer, may not sync"
        assert call("/team/versions", {"versions": "any"}, bob["token"])[0] == 403, "only an admin allows other versions"
        assert call("/team/versions", {"versions": "any"}, ada)[1]["versions"] == "any"
        assert call("/pull?after=0&wait=0", None, bob["token"], version="4.20.9")[0] == 200, "once the admin allows any version, another version syncs"
        assert call("/team/versions", {"versions": "exact"}, ada)[1]["versions"] == "exact"
        assert call("/pull?after=0&wait=0", None, bob["token"], version="4.20.9")[0] == 403 and call("/pull?after=0&wait=0", None, bob["token"])[0] == 200, "exact again refuses it, and the matching journal syncs either way"
        assert call("/accept", {"code": invitation["code"], "email": "bob@example.com", "name": "Eve", "password": PASSWORD, "password_repeat": PASSWORD, "device_name": "x"})[1]["error"].startswith("this invitation code is not known or was used"), "a code is used once"
        assert call("/invite", {"email": "eve@example.com"}, bob["token"])[1]["error"].startswith("Bob is no admin"), "only an admin invites"
        assert [device["name"] for device in call("/devices", token=ada)[1]["devices"]] == ["laptop", "desktop"]
        _, laptop = call("/login", {"email": "bob@example.com", "password": PASSWORD, "device_name": "bob's laptop"})
        assert call("/devices/revoke", {"device_id": laptop["device_id"]}, ada)[0] == 200 and call("/copy", token=laptop["token"])[0] == 403, "a revoked device is refused"
        assert call("/people/remove", {"account_id": 2}, ada)[0] == 200
        assert call("/copy", token=bob["token"])[0] == 403 and call("/login", {"email": "bob@example.com", "password": PASSWORD, "device_name": "again"})[0] == 403, "a removed person's devices are refused and they cannot log in"
    finally:
        team.close(server)


def test_two_devices_racing_for_a_lease_leave_exactly_one_holder_and_an_unrenewed_lease_lapses(store):
    import threading
    from sync_server.db.lease_rows import LeaseRows
    from sync_server.leases import LAPSE_SECONDS, Leases

    accounts, devices = people(store)
    ada_account = accounts.create("ada@example.com", "Ada", PASSWORD, ADMIN, 1.0)
    bob_account = accounts.create("bob@example.com", "Bob", PASSWORD, MEMBER, 1.0)
    ada, _ = devices.login("ada@example.com", PASSWORD, "laptop", "10.0.0.1", 2.0)
    bob, _ = devices.login("bob@example.com", PASSWORD, "desktop", "10.0.0.2", 2.0)
    leases = Leases(store, LeaseRows(store), accounts)
    winners, losers = [], []

    def race(device, person):
        try:
            winners.append(leases.acquire("team-chat", device, person, 100.0).holder)
        except Refusal as refused:
            losers.append(str(refused))

    racers = [threading.Thread(target=race, args=pair) for pair in ((ada, ada_account), (bob, bob_account)) * 5]
    for racer in racers:
        racer.start()
    for racer in racers:
        racer.join(5)
    assert len(set(winners)) == 1 and losers and "is held by" in losers[0], "two devices racing for one lease leave exactly one holder"
    holder = ada if winners[0] == "Ada" else bob
    other, other_account = (bob, bob_account) if holder is ada else (ada, ada_account)
    assert leases.acquire("team-chat", holder, ada_account if holder is ada else bob_account, 130.0).renewed_at == 130.0, "the holder renews it by taking it again"
    with pytest.raises(Refusal, match="is held by"):
        leases.acquire("team-chat", other, other_account, 131.0)
    assert leases.state("team-chat", 130.0 + LAPSE_SECONDS + 1).is_lapsed, "a lease nobody renews lapses"
    assert leases.acquire("team-chat", other, other_account, 130.0 + LAPSE_SECONDS + 1).holder == other_account.name, "and another device may take it"
    assert leases.release("team-chat", other, 300.0).holder == "", "its holder lets it go"


def test_a_lease_taken_free_with_its_own_lapse_names_its_holder_and_device_and_passes_to_another_device_only_by_a_takeover_once_lapsed(store):
    from sync_server.db.lease_rows import LeaseRows
    from sync_server.leases import Leases

    accounts, devices = people(store)
    ada_account = accounts.create("ada@example.com", "Ada", PASSWORD, ADMIN, 1.0)
    bob_account = accounts.create("bob@example.com", "Bob", PASSWORD, MEMBER, 1.0)
    ada, _ = devices.login("ada@example.com", PASSWORD, "laptop", "10.0.0.1", 2.0)
    bob, _ = devices.login("bob@example.com", PASSWORD, "desktop", "10.0.0.2", 2.0)
    leases = Leases(store, LeaseRows(store), accounts)
    taken = leases.acquire_free("drive:tasks:7", ada, ada_account, 100.0, 900.0)
    assert (taken.holder, taken.device_name) == ("Ada", "laptop"), "the answer names the person and the device holding it"
    assert leases.acquire_free("drive:tasks:7", ada, ada_account, 700.0, 900.0).renewed_at == 700.0, "its holder renews it"
    with pytest.raises(Refusal, match="held by Ada on laptop"):
        leases.acquire_free("drive:tasks:7", bob, bob_account, 800.0, 900.0)
    with pytest.raises(Refusal, match="held by Ada on laptop"):
        leases.acquire("drive:tasks:7", bob, bob_account, 1500.0, 900.0)
    assert not leases.state("drive:tasks:7", 1500.0).is_lapsed and leases.state("drive:tasks:7", 1601.0).is_lapsed, "it lapses after its own 900 seconds, not the default 90"
    with pytest.raises(Refusal, match="only a takeover has it"):
        leases.acquire_free("drive:tasks:7", bob, bob_account, 1601.0, 900.0)
    assert leases.acquire("drive:tasks:7", bob, bob_account, 1601.0, 900.0).holder == "Bob", "lapsed, a takeover has it"


def test_a_journal_and_a_team_server_on_different_protocols_are_refused_with_the_side_to_upgrade(tmp_path, monkeypatch, connection):
    import json

    from journal.config import Config
    from journal.db.schema import Schema
    from journal.models.all_models import AllModels
    from journal.sync.team_account import TEAM_FILE, TeamAccount
    from journal.sync.team_refusal import TeamRefusal
    from journal.sync.team_server_link import TeamServerLink
    from sync_server.team_server import TeamServer

    server = TeamServer(tmp_path).started("127.0.0.1", 0)
    address = f"http://127.0.0.1:{server.server_address[1]}"
    config = Config(tmp_path / "journal")
    config.home.mkdir(parents=True)
    (config.home / TEAM_FILE).write_text(json.dumps({"address": address, "token": "t"}))
    link = TeamServerLink(TeamAccount(config), Schema(connection, AllModels.MODELS))
    try:
        assert link.summary(address) is not None, "a journal on the server's protocol is answered"
        monkeypatch.setattr("journal.sync.team_server_link.PROTOCOL", PROTOCOL - 1)
        with pytest.raises(TeamRefusal, match="upgrade the journal with journal update apply"):
            link.summary(address)
        monkeypatch.setattr("journal.sync.team_server_link.PROTOCOL", PROTOCOL + 1)
        with pytest.raises(TeamRefusal, match="upgrade the team server's image"):
            link.summary(address)
    finally:
        server.shutdown()
        server.server_close()


def test_a_withdrawn_change_reaches_a_journal_on_the_current_protocol_with_its_keeper_and_a_journal_on_the_old_one_is_refused_before_it_reads_it(tmp_path):
    import json
    import urllib.error
    import urllib.request

    from sync_server.team_server import TeamServer

    team = TeamServer(tmp_path)
    team.accounts.create("ada@example.com", "Ada", PASSWORD, ADMIN, 1.0)
    team.accounts.create("bob@example.com", "Bob", PASSWORD, MEMBER, 1.0)
    server = team.started("127.0.0.1", 0)
    address = f"http://127.0.0.1:{server.server_address[1]}"

    def call(path, body=None, token="", protocol=PROTOCOL):
        request = urllib.request.Request(address + path, data=None if body is None else json.dumps(body).encode(), headers={PROTOCOL_HEADER: str(protocol), **({"Authorization": f"Bearer {token}"} if token else {})})
        try:
            with urllib.request.urlopen(request, timeout=10) as answer:
                return answer.status, json.loads(answer.read())
        except urllib.error.HTTPError as refused:
            return refused.code, json.loads(refused.read())

    try:
        ada = call("/login", {"email": "ada@example.com", "password": PASSWORD, "device_name": "laptop"})[1]["token"]
        bob = call("/login", {"email": "bob@example.com", "password": PASSWORD, "device_name": "desktop"})[1]["token"]
        task = {"row_table": "tasks", "row": 7, "action": "created", "actor": "user:1", "fields": {"title": "mine"}, "changed_at": {"title": 1.0}}
        call("/push", {"changes": [task, {**task, "action": "withdrawn", "fields": {}, "changed_at": {}, "kept_by": "owner"}]}, ada)
        status, refusal = call("/pull?after=0", token=bob, protocol=PROTOCOL - 1)
        assert status == 426 and refusal == {"error": f"this journal speaks protocol {PROTOCOL - 1} and the team server {PROTOCOL}: upgrade the journal with journal update apply"}, "a journal on the protocol before the withdrawn action is refused, so it never reads a withdrawal as an update or a deletion"
        assert call("/push", {"changes": [{**task, "row": 8}]}, bob, PROTOCOL - 1)[0] == 426 and team.log.row("tasks", 8) is None, "nor does it push"
        pulled = call("/pull?after=0", token=bob)[1]["changes"]
        assert [(change["action"], change["kept_by"]) for change in pulled] == [("withdrawn", "owner")], "a journal on the current protocol pulls the withdrawal with who keeps the row, and nothing of the row from before it"
        assert call("/copy", token=bob)[1]["rows"] == [], "a full copy never holds a withdrawn row"
        call("/push", {"changes": [{**task, "action": "updated", "fields": {"title": "late"}, "changed_at": {"title": 9.0}}]}, ada)
        assert team.log.row("tasks", 7) is None, "an update to a withdrawn row is dropped"
    finally:
        server.shutdown()
        server.server_close()
        team.store.close()


def test_an_upgrade_holds_every_other_push_replaces_the_teams_rows_once_and_keeps_the_old_copy(tmp_path):
    import json
    import sqlite3
    import urllib.error
    import urllib.request

    from sync_server.team_server import TeamServer

    team = TeamServer(tmp_path)
    team.accounts.create("ada@example.com", "Ada", PASSWORD, ADMIN, 1.0)
    team.accounts.create("bob@example.com", "Bob", PASSWORD, MEMBER, 1.0)
    server = team.started("127.0.0.1", 0)
    address = f"http://127.0.0.1:{server.server_address[1]}"

    def call(path, body=None, token="", migration=3):
        request = urllib.request.Request(address + path, data=None if body is None else json.dumps(body).encode(), headers={PROTOCOL_HEADER: str(PROTOCOL), MIGRATION_HEADER: str(migration), VERSION_HEADER: "4.20.0", "Authorization": f"Bearer {token}"})
        try:
            with urllib.request.urlopen(request, timeout=10) as answer:
                return answer.status, json.loads(answer.read())
        except urllib.error.HTTPError as refused:
            return refused.code, json.loads(refused.read())

    def row(title):
        return {"row_table": "tasks", "row": 7, "fields": {"title": title}, "changed_at": {"title": 1.0}}

    try:
        ada = call("/login", {"email": "ada@example.com", "password": PASSWORD, "device_name": "laptop"})[1]["token"]
        bob = call("/login", {"email": "bob@example.com", "password": PASSWORD, "device_name": "desktop"})[1]["token"]
        head = call("/upload", {"rows": [row("before")], "highest": {"tasks": 7}, "repository": "", "version": "4.20.0", "migration": 3}, ada)[1]["head"]
        assert call("/leases/take", {"name": "upgrade"}, ada)[0] == 200
        assert call("/leases/take", {"name": "upgrade"}, bob)[0] == 403, "a second device cannot take the upgrade lease while it is held"
        refused = call("/push", {"changes": []}, bob)
        assert refused == (403, {"error": "the team is upgrading on Ada's machine: this journal's changes wait until it is done"}), "every other device's push waits while the upgrade lease is held"
        assert call("/upgrade", {"rows": [row("migrated")], "highest": {"tasks": 7}, "migration": 4, "base_sequence": head - 1}, ada)[1]["error"].startswith("the team's journal moved on"), "a copy migrated from a stale pull is refused"
        upgraded = call("/upgrade", {"rows": [row("migrated")], "highest": {"tasks": 7}, "migration": 4, "base_sequence": head}, ada, migration=4)
        assert upgraded[0] == 200
        assert call("/team")[1]["migration"] == 4
        behind = call(f"/pull?after={head}&wait=0", None, bob, migration=4)[1]
        assert behind["copy_needed"] and not behind["changes"], "a device behind the upgrade takes the full copy"
        assert call("/copy", None, bob, migration=4)[1]["rows"][0]["fields"] == {"title": "migrated"}, "the migrated copy is the team's"
        assert call(f"/pull?after={head}&wait=0", None, bob, migration=4)[1]["copy_needed"] is False, "once it has taken the copy, a pull that still names its older sequence goes on from the copy, never asked to take it again"
        assert call(f"/pull?after={upgraded[1]['head']}&wait=0", None, ada, migration=4)[1]["copy_needed"] is False, "the upgrader goes on from its upload"
        [backup] = (tmp_path / "backups").glob("team-before-upgrade-*.db")
        with sqlite3.connect(backup) as old:
            assert json.loads(old.execute("SELECT fields FROM rows").fetchone()[0]) == {"title": "before"}, "the copy it replaced is kept as a backup"
    finally:
        team.close(server)


def test_the_log_is_trimmed_of_what_every_device_pulled_while_deletions_stay_and_an_older_device_takes_the_copy(tmp_path, monkeypatch, capsys):
    from sync_server.team_server import TeamServer

    monkeypatch.setattr("sync_server.pull_handler.TRIM_SECONDS", 0)
    team = TeamServer(tmp_path)
    for email, name, role in (("ada@example.com", "Ada", ADMIN), ("bob@example.com", "Bob", MEMBER), ("eve@example.com", "Eve", MEMBER)):
        team.accounts.create(email, name, PASSWORD, role, 1.0)
    (ada_device, ada), (_, bob), (eve_device, eve) = (team.devices.login(email, PASSWORD, "laptop", "127.0.0.1", 1.0) for email in ("ada@example.com", "bob@example.com", "eve@example.com"))
    for change in (LoggedChange("tasks", 7, "created", "user:1", 1, ada_device.id, {"title": "a"}, {"title": 1.0}), LoggedChange("tasks", 8, "created", "user:1", 1, ada_device.id, {"title": "b"}, {"title": 1.0}),
                   LoggedChange("tasks", 8, "deleted", "user:1", 1, ada_device.id), LoggedChange("tasks", 7, "updated", "user:1", 1, ada_device.id, {"title": "c"}, {"title": 2.0})):
        team.log.appended(change)
    team.pulls.answer(eve, PullQuery(1, 0, (), PoolSlots(0, 0), ""))
    team.devices.revoke(eve_device.id, 2.0)
    team.pulls.answer(ada, PullQuery(4, 0, (), PoolSlots(0, 0), ""))
    team.pulls.answer(bob, PullQuery(3, 0, (), PoolSlots(0, 0), ""))
    assert team.log.size() == 1 and team.log.head() == 4, "the changes every device pulled are trimmed, a revoked device not counted and the newest kept"
    assert team.log.is_deleted("tasks", 8), "a deleted row stays on the server as a marker, so a deletion still wins over a later edit"
    _, late = team.devices.login("bob@example.com", PASSWORD, "old laptop", "127.0.0.1", 3.0)
    team.devices.record_pull(team.devices.device(late), 1, 3.0)
    assert team.pulls.answer(late, PullQuery(1, 0, (), PoolSlots(0, 0), "")).copy_needed, "a device older than the trimmed tail takes the full copy again"
    assert f"device {team.devices.device(late).id} told to take the full copy: its furthest sequence 1, the lowest 4, the head 4" in capsys.readouterr().err, "each copy asked for is logged with the device, its furthest sequence, the lowest and the head"
    _, joiner = team.devices.login("bob@example.com", PASSWORD, "new laptop", "127.0.0.1", 4.0)
    assert [(row.row, row.fields) for row in team.copies.answer(joiner).rows] == [(7, {"title": "c"})], "a new device still joins from the full copy"
    _, ahead = team.devices.login("bob@example.com", PASSWORD, "laptop from before a reset", "127.0.0.1", 5.0)
    team.pulls.answer(ahead, PullQuery(900, 0, (), PoolSlots(0, 0), ""))
    team.pulls.answer(ada, PullQuery(4, 0, (), PoolSlots(0, 0), ""))
    assert team.devices.pulled_sequence(team.devices.device(ahead)) <= team.log.head() and team.details.lowest_sequence() <= team.log.head(), "a device naming a sequence past the head records no pull past it, so the lowest never passes the head"
    assert not team.pulls.answer(ada, PullQuery(team.log.head(), 0, (), PoolSlots(0, 0), "")).copy_needed, "a pull at the head is never told to take the copy"
    team.store.close()


def test_only_the_hosted_journals_relay_account_sends_writes_in_another_persons_name(tmp_path):
    from sync_server.account import RELAY
    from sync_server.push_request import PushRequest
    from sync_server.team_server import TeamServer

    team = TeamServer(tmp_path)
    team.accounts.create("ada@example.com", "Ada", PASSWORD, ADMIN, 1.0)
    team.accounts.create("bob@example.com", "Bob", PASSWORD, MEMBER, 1.0)
    team.accounts.create("hosted-journal@team.server", "Hosted journal", PASSWORD, RELAY, 1.0)
    _, bob = team.devices.login("bob@example.com", PASSWORD, "laptop", "127.0.0.1", 1.0)
    _, hosted = team.devices.login("hosted-journal@team.server", PASSWORD, "server", "127.0.0.1", 1.0)
    as_ada = PushRequest.parsed([{"row_table": "messages", "row": 1, "action": "created", "actor": "user:1", "fields": {"text": "from a browser"}, "changed_at": {"text": 1.0}, "local_number": 1}])
    with pytest.raises(Refusal, match="a person sends only their own writes"):
        team.pushes.answer(bob, as_ada, 2.0)
    assert team.pushes.answer(hosted, as_ada, 2.0).sequences == (1,), "the hosted journal sends the write of whoever signed in to it"
    with pytest.raises(Refusal, match="Bob is no admin"):
        team.admins.pin(bob, "4.99.0")
    assert team.admins.pin(hosted, "4.99.0").version == "4.99.0", "the hosted journal pins the team to the release it installed"
    team.store.close()


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


def test_a_one_time_signin_link_is_issued_to_a_member_and_taken_up_once_by_the_hosted_journal_alone(tmp_path):
    from pathlib import Path
    from sync_server.account import RELAY
    from sync_server.team_server import TeamServer
    team = TeamServer(tmp_path)
    team.accounts.create("ada@example.com", "Ada", PASSWORD, MEMBER, 1.0)
    team.accounts.create("hosted-journal@team.server", "Hosted journal", PASSWORD, RELAY, 1.0)
    _, ada = team.devices.login("ada@example.com", PASSWORD, "laptop", "127.0.0.1", 1.0)
    _, hosted = team.devices.login("hosted-journal@team.server", PASSWORD, "server", "127.0.0.1", 1.0)
    code = team.signins.issue(ada, 10.0)
    with pytest.raises(Refusal, match="only the team's hosted journal"):
        team.signins.redeemed(ada, code, 11.0)
    assert team.signins.redeemed(hosted, code, 11.0).email == "ada@example.com", "the hosted journal signs in the member who asked"
    with pytest.raises(Refusal, match="used already or has expired"):
        team.signins.redeemed(hosted, code, 12.0)
    late = team.signins.issue(ada, 10.0)
    with pytest.raises(Refusal, match="used already or has expired"):
        team.signins.redeemed(hosted, late, 10.0 + 121)
    routes = (Path(__file__).resolve().parents[1] / "docker/team-server/routes.caddy").read_text()
    assert "not header Cookie *journal_session=*" in routes and "rewrite * /setup" in routes, "a browser without a session is sent to the setup page, which forbids it once the server has its admin"
    team.store.close()


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


def test_a_pool_request_goes_to_one_machine_with_a_free_slot_on_its_version_and_one_nobody_claims_is_answered_back(tmp_path):
    from sync_server.device_ask_request import DeviceAskRequest
    from sync_server.pool_ask_request import PoolAskRequest
    from sync_server.team_server import TeamServer

    team = TeamServer(tmp_path)
    team.accounts.create("ada@example.com", "Ada", PASSWORD, ADMIN, 1.0)
    team.accounts.create("bob@example.com", "Bob", PASSWORD, MEMBER, 1.0)
    _, ada = team.devices.login("ada@example.com", PASSWORD, "laptop", "127.0.0.1", 1.0)
    machines = {name: team.devices.login("bob@example.com", PASSWORD, name, "127.0.0.1", 1.0)[1] for name in ("first", "second", "older", "full")}
    offers = {"first": (PoolSlots(2, 1), "4.40.0"), "second": (PoolSlots(1, 1), "4.40.0"), "older": (PoolSlots(1, 1), "4.39.0"), "full": (PoolSlots(1, 0), "4.40.0")}
    pulled = lambda name, keys=(): {request.id: request for request in team.pulls.answer(machines[name], PullQuery(0, 0, keys, *offers[name])).requests}
    asked = lambda: team.host_requests.pooled(ada, PoolAskRequest("env-1", "pool_worker", {"task": 7}, 0, "4.40.0"), team.clock.time()).requests[0]
    try:
        first = asked()
        seen = {name: first.id in pulled(name) for name in machines}
        assert seen == {"first": True, "second": True, "older": False, "full": False}, "a pool request is offered to every machine with a free slot on the version it names, never to one that is full or on another version"
        assert {(capacity.slots, capacity.free, capacity.version) for capacity in PoolCapacityRows(team.store).capacities()} == {(2, 1, "4.40.0"), (1, 1, "4.40.0"), (1, 1, "4.39.0"), (1, 0, "4.40.0")}, "each machine's slots and free count are kept from its pull"
        assert pulled("first")[first.id].audience == "pool" and pulled("first")[first.id].account_id == 1, "it reaches the machine as a pool request in the name of the person who asked"
        team.host_requests.claimed(machines["first"], first.id)
        with pytest.raises(Refusal, match="taken by another machine"):
            team.host_requests.claimed(machines["second"], first.id)
        assert first.id not in pulled("second"), "once claimed it is no longer offered"
        second = asked()
        team.host_requests.declined(machines["first"], second.id)
        assert second.id not in pulled("first") and second.id in pulled("second"), "a machine that declines one is not offered it again, and the others still are"
        word = team.host_requests.addressed(ada, DeviceAskRequest(team.devices.device(machines["second"]).id, "env-1", "pool_word", {"text": "go on"}, 0), team.clock.time()).requests[0]
        assert word.id in pulled("second") and word.id not in pulled("first"), "a request addressed to one machine reaches that machine alone"
        team.host_requests.lapse(team.clock.time() + 601)
        answered_back = [request for request in pulled("first", ("env-1",)).values() if request.kind == "pool_unclaimed"]
        assert [request.body["request"] for request in answered_back] == [second.id] and second.id not in pulled("second"), "one nobody claimed in ten minutes is answered back to its environment's host and offered no more; a claimed one is left alone"
    finally:
        team.store.close()


def test_a_new_team_server_is_claimed_by_the_first_journal_with_no_code_and_a_second_claim_is_refused(tmp_path):
    from sync_server.install_request import InstallRequest
    from sync_server.team_server import TeamServer
    team = TeamServer(tmp_path)
    claim = lambda email: team.logins.installed(InstallRequest(email, "Ada", "correct horse battery staple", "laptop"), "1.2.3.4")
    assert claim("ada@example.com").role == "admin", "the first journal to reach a server with no admin claims it by its address alone"
    with pytest.raises(Refusal):
        claim("eve@example.com")
    assert InstallRequest("bob@example.com", "Bob", "x", "laptop", setup_code="ABCD-EFGH").email == "bob@example.com", "an older journal's setup code is still read, and ignored"


def test_a_new_team_servers_address_shows_the_setup_page_until_it_is_claimed_and_forbids_after(tmp_path):
    from urllib.parse import urlencode
    from sync_server.team_server import TeamServer
    team = TeamServer(tmp_path)
    status, page = team.setup_page.shown("https://team.example")
    assert status == 200 and "Setup code" not in page and "<form" in page
    form = lambda fields: urlencode(fields).encode()
    status, page = team.setup_page.posted(form({"name": "Ada", "email": "ada@example.com", "password": "correct horse battery staple"}), "https://team.example")
    assert status == 200 and "is yours, Ada" in page and "journal team join https://team.example --email ada@example.com" in page
    assert team.setup_page.shown("https://team.example")[0] == 403, "claimed, the address is forbidden to a stranger again"
