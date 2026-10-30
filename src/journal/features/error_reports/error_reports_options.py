from journal.support.option import USER, Option
from journal.support.option_scope import OptionScope


class ErrorReportsOptions:
    SENTRY_DSN = Option("faults.sentry_dsn", "Send faults to Sentry", "The DSN of a Sentry project the journal sends each fault it meets to, with its version, where it happened and its frames, never the values it held; empty sends nothing", "", option_type="text", scope=OptionScope.MACHINE, setter=USER)
