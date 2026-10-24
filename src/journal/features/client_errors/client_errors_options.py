from journal.support.option import Option


class ClientErrorsOptions:
    REPORT = Option("client_errors.report", "Tell the agent about the viewer's errors", "Each console error the viewer logs is told to the agent at once and again every fifty tool uses while it stays unhandled; for working on the journal itself, so off by default, and the Developer tab lists them either way", False, kind="switch")
