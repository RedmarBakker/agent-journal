from journal.features.error_reports.error_reports_options import ErrorReportsOptions
from journal.features.error_reports.jobs.sentry_sender import SentrySender
from journal.features.feature import Feature


class ErrorReports(Feature):
    name = "error_reports"
    title = "Error reports"
    fixed = True
    help = "Each fault the journal meets is sent, with its version, where it happened and its frames, never the values it held, to the Sentry project you name; with none named, nothing is sent."
    jobs = (SentrySender,)
    options = (ErrorReportsOptions.SENTRY_DSN,)
