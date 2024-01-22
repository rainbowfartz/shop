# User class
class User:
    count_id = 0

    # initializer method
    def __init__(self, Fullname,Email,Password):
        User.count_id += 1
        self.__user_id = User.count_id
        self.__Fullname = Fullname
        self.__Email = Email
        self.__Password = Password
    # accessor methods
    def get_user_id(self):
        return self.__user_id

    def get_first_name(self):
        return self.__Fullname

    def get_Email(self):
        return self.__Email
    
    def get_Password(self):
        return self.__Password

    # mutator methods
    def set_user_id(self, user_id):
        self.__user_id = user_id

    def set_first_name(self, Fullname):
        self.__Fullname = Fullname
        
        
    def set_first_name(self, Email):
        self.__Email = Email
    
    def set_Password(self, Password):
        self.__Password = Password

