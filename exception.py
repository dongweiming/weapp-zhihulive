class LoginException(Exception):
    def __init__(self, error):
        self.error = error

    def __repr__(self):
        return 'Login Fail: {}'.format(self.error)

    __str__ = __repr__
