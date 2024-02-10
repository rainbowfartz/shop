from flask_login import UserMixin

class User(UserMixin):
    id = 0

    def __init__(self, Username, Email, Password):
        User.id += 1
        self.id = User.id
        self.username = Username
        self.email = Email
        self.password = Password