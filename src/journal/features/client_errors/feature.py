from journal.features.client_errors.client_errors_conduct import ClientErrorsConduct
from journal.features.client_errors.client_errors_nudges import ClientErrorsNudges
from journal.features.client_errors.client_errors_part import ClientErrorsPart
from journal.features.client_errors.support.client_errors_data import ClientErrorsData
from journal.features.client_errors.support.client_errors_data_reader import ClientErrorsDataReader
from journal.features.feature import Feature


class ClientErrors(Feature[ClientErrorsData]):
    name = ClientErrorsPart.name
    title = "Viewer errors"
    help = "The viewer posts each console error with its stack to the journal, which keeps them in memory, each distinct one counted once. The agent is told at once when a new one arrives and reminded every fifty tool uses while any stay unhandled; journal developer client-errors lists them and --clear empties the list."
    nudges = (ClientErrorsNudges.LOGGED, ClientErrorsNudges.UNHANDLED)
    data = (ClientErrorsDataReader,)
    conduct = (ClientErrorsConduct,)
