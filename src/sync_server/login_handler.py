from sync_server.accept_request import AcceptRequest
from sync_server.accounts import Accounts
from sync_server.devices import Devices
from sync_server.install_request import InstallRequest
from sync_server.invitations import Invitations
from sync_server.login_request import LoginRequest
from sync_server.login_answer import LoginAnswer
from sync_server.server_clock import ServerClock


class LoginHandler:
    """Trades a person's email and password for a device token, an invitation code for a new account and its first device token, or, on a server with no account yet, the first connection's email and password for its admin's account and first device token; the address is the one the proxy in front forwards."""

    def __init__(self, devices: Devices, invitations: Invitations, accounts: Accounts, clock: ServerClock) -> None:
        self.devices, self.invitations, self.accounts, self.clock = devices, invitations, accounts, clock

    def answer(self, request: LoginRequest, address: str) -> LoginAnswer:
        device, token = self.devices.login(request.email, request.password, request.device_name, address, self.clock.time())
        person = self.devices.person(token)
        return LoginAnswer(token, device.id, person.id, person.name, person.role)

    def accepted(self, request: AcceptRequest, address: str) -> LoginAnswer:
        account = self.invitations.accept(request.code, request.name, request.password, request.password_repeat, self.clock.time())
        return self.answer(LoginRequest(account.email, request.password, request.device_name), address)

    def installed(self, request: InstallRequest, address: str) -> LoginAnswer:
        account = self.accounts.first_admin(request.email, request.name, request.password, self.clock.time())
        return self.answer(LoginRequest(account.email, request.password, request.device_name), address)
