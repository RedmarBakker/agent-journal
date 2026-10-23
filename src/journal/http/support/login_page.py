import html

from journal.http.support.file_response import FileResponse

HELP = "Use the email and password your own journal joined the team with. An admin can reset a forgotten password from their journal's Team page."
PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sign in</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap">
<style>
:root {{
    color-scheme: dark;
    --bg: #131416;
    --border: #25272b;
    --border-2: #2f3136;
    --text: #e6e7ea;
    --text-2: #a9acb3;
    --text-3: #83868e;
    --accent: #5e64c9;
    --accent-text: #a3a8f0;
    --accent-dim: #2a2d5a;
    --danger: #df8b7e;
}}

* {{
    box-sizing: border-box;
}}

body {{
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    margin: 0;
    padding: 40px 16px;
    background: #0a0b0c;
    color: var(--text);
    font: 13px/1.45 "Geist", -apple-system, "Segoe UI", system-ui, sans-serif;
    -webkit-font-smoothing: antialiased;
}}

form {{
    display: flex;
    flex-direction: column;
    gap: 16px;
    width: 360px;
    max-width: 100%;
}}

h1 {{
    margin: 0;
    font-size: 18px;
    font-weight: 600;
}}

.address {{
    margin-top: 4px;
    color: var(--text-2);
    font: 12px "Geist Mono", ui-monospace, Menlo, monospace;
}}

.panel {{
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 14px 16px;
    border: 1px solid var(--border);
    border-radius: 10px;
    background: var(--bg);
}}

label {{
    display: flex;
    flex-direction: column;
    gap: 5px;
    color: var(--text-2);
    font-size: 12px;
    font-weight: 500;
}}

input {{
    height: 34px;
    padding: 0 9px;
    border: 1px solid var(--border-2);
    border-radius: 7px;
    background: var(--bg);
    color: var(--text);
    font: inherit;
    font-size: 13px;
    font-weight: 400;
}}

input:focus {{
    border-color: var(--accent);
    outline: none;
}}

input.wrong {{
    border-color: color-mix(in oklab, var(--danger) 70%, var(--border-2));
}}

button {{
    height: 32px;
    border: 1px solid var(--accent);
    border-radius: 7px;
    background: var(--accent-dim);
    color: var(--accent-text);
    font: inherit;
    font-size: 12.5px;
    cursor: pointer;
}}

.refusal {{
    display: flex;
    align-items: flex-start;
    gap: 8px;
    margin: 0;
    color: var(--danger);
}}

.refusal::before {{
    content: "";
    flex: none;
    width: 7px;
    height: 7px;
    margin-top: 6px;
    border-radius: 50%;
    background: var(--danger);
}}

.help {{
    margin: 0;
    color: var(--text-3);
    font-size: 12px;
}}

@media (max-width: 520px) {{
    body {{
        align-items: flex-start;
        padding-top: 72px;
    }}
}}
</style>
</head>
<body>
<form method="post" action="/sign-in" enctype="multipart/form-data">
<div>
<h1>Sign in to the team's journal</h1>
<div class="address">{address}</div>
</div>
<div class="panel">
{first}
<label>Email<input name="email" type="email" autocomplete="username" value="{email}" required {email_focus}></label>
<label>Password<input name="password" type="password" autocomplete="current-password" class="{password_class}" required {password_focus}></label>
{last}
<button type="submit">Sign in</button>
</div>
<p class="help">{help}</p>
</form>
</body>
</html>
"""


class LoginPage:
    """The hosted journal's sign-in form, in the viewer's colours: the team's address under the heading, the fields in a panel and the line on which email and password to use; refused, it says why where the person will read it next."""

    @staticmethod
    def form(address: str) -> FileResponse:
        return LoginPage.rendered(address, "", "", "", "", 200)

    @staticmethod
    def wrong_login(address: str, email: str, reason: str) -> FileResponse:
        return LoginPage.rendered(address, email, "", LoginPage.refusal(reason), "wrong", 401)

    @staticmethod
    def link_refused(address: str, reason: str) -> FileResponse:
        return LoginPage.rendered(address, "", LoginPage.refusal(reason), "", "", 403)

    @staticmethod
    def refusal(reason: str) -> str:
        return f'<p class="refusal">{html.escape(reason)}</p>'

    @staticmethod
    def rendered(address: str, email: str, first: str, last: str, password_class: str, status: int) -> FileResponse:
        page = PAGE.format(
            address=html.escape(address),
            email=html.escape(email),
            first=first,
            last=last,
            password_class=password_class,
            email_focus="" if email else "autofocus",
            password_focus="autofocus" if email else "",
            help=HELP,
        )
        return FileResponse("text/html; charset=utf-8", page.encode(), status)
