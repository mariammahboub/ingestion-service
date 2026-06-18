class DuplicateReadingError(Exception):
    pass

class ReadingPersistenceError(Exception):

    def __init__(self, cause: Exception):
        self.cause = cause
        super().__init__(f"Failed to persist reading: {cause}")
class SensorNotFoundError(Exception):
    pass