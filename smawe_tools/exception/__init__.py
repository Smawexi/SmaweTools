class MaxRetryError(Exception):
    def __init__(self, *args, last_exception=None):
        self.last_exception = last_exception
        super().__init__(*args)

    def __str__(self):
        return str(self.last_exception)
