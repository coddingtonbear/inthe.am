class NestedCheckpointError(RuntimeError):
    pass


class CheckpointNeeded(RuntimeError):
    pass


class InvalidTaskwarriorConfiguration(RuntimeError):
    pass


class TrelloObjectRecentlyModified(RuntimeError):
    pass
