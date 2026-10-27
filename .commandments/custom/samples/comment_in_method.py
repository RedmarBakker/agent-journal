class Shelf:
    """Books on a shelf, counted."""

    # @sin CommentInMethodDetector
    def count(self, books: list[str]) -> int:
        # every book counts once
        return len(set(books))

    # @righteous CommentInMethodDetector
    def distinct_count(self, books: list[str]) -> int:
        return len(set(books))

    # @sin CommentInMethodDetector
    @staticmethod
    def width(books: list[str]) -> int:
        # three centimetres a book
        return 3 * len(books)


# @righteous CommentInMethodDetector
def total_width(books: list[str]) -> int:
    return 3 * len(books)


# @sin CommentAboveMethodDetector
# @righteous CommentInMethodDetector
# a comment above a function is the other rule's, never this one's
def spine_width() -> int:
    return 2
