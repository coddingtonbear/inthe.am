

class NestedCheckpointError(RuntimeError):
    pass


class CheckpointNeeded(RuntimeError):
    pass


class InvalidBugwarriorConfiguration(RuntimeError):
    pass


class InvalidTaskwarriorConfiguration(RuntimeError):
    pass
