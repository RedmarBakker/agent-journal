from journal.features.messages.support.unlinked_row_numbers import ROW_TABLES, TOKEN_PATTERN, UnlinkedRowNumbers


class RowReferences:
    """The rows a message refers to with their kind before the number, such as task 3687 or tasks 3345 and 3346, each as its kind and number, in the order they appear and once each."""

    @classmethod
    def rows(cls, text: str) -> list[tuple[str, int]]:
        tokens = [match.group() for match in TOKEN_PATTERN.finditer(text)]
        references = [(type_name, int(token)) for i, token in enumerate(tokens) if token.isdigit() and (type_name := cls.table_name(UnlinkedRowNumbers.preceding_word(tokens, i)))]
        return list(dict.fromkeys(references))

    @staticmethod
    def table_name(word: str) -> str:
        singular = word.removesuffix("s")
        return singular if singular in ROW_TABLES else ""
