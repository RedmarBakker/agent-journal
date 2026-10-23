from journal.http.support.file_response import FileResponse
from journal.http.support.request import Request
from journal.http.support.session_cookie import SessionCookie
from journal.http.support.login_page import LoginPage
from journal.repositories.browser_sessions import BrowserSessions
from journal.support.response import Response
from journal.sync.team_account import TeamAccount
from journal.sync.team_refusal import TeamRefusal
from journal.sync.team_server_link import TeamServerLink
from sync_server.login_request import LoginRequest

DEVICE_NAME = "a browser on the hosted journal"


class LoginController:
    """The sign-in of a hosted journal: the one-time link a member's own journal opens, which the team server trades for that person and which opens their browser session; the form with the team server's check of the email and password; and the sign-out, which ends it."""

    def __init__(self, sessions: BrowserSessions, link: TeamServerLink, account: TeamAccount) -> None:
        self.sessions, self.link, self.account = sessions, link, account

    def show(self, request: Request) -> FileResponse:
        return LoginPage.form(request.host)

    def submit(self, request: Request) -> FileResponse | Response:
        email = str(request.body.get("email", ""))
        try:
            login = self.link.login(self.account.address(), LoginRequest(email, str(request.body.get("password", "")), DEVICE_NAME))
        except TeamRefusal as refused:
            return LoginPage.wrong_login(request.host, email, str(refused))
        key = self.sessions.opened(login.account_id, login.name)
        return Response(303, None, {"Location": "/", "Set-Cookie": SessionCookie.value(key, request.protocol)})

    def opened(self, request: Request) -> FileResponse | Response:
        try:
            answer = self.link.signin_account(str(request.query.get("code", "")))
        except TeamRefusal as refused:
            return LoginPage.link_refused(request.host, str(refused))
        key = self.sessions.opened(answer.account_id, answer.name)
        return Response(303, None, {"Location": "/", "Set-Cookie": SessionCookie.value(key, request.protocol)})

    def logout(self, request: Request) -> Response:
        self.sessions.closed(SessionCookie.key(request.cookie))
        return Response(303, None, {"Location": "/sign-in", "Set-Cookie": SessionCookie.expired_value(request.protocol)})
