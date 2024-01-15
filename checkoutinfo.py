class CheckoutInfo:
    count_id = 0
    def __init__(self, name, address, card_number, exp_month, exp_year, cvv, date):
        CheckoutInfo.count_id += 1
        self.__info_id = CheckoutInfo.count_id
        self.__name = name 
        self.__address= address
        self.__card_number = card_number
        self.__exp_month = exp_month
        self.__exp_year = exp_year
        self.__cvv = cvv
        self.__date = date

    def get_info_id(self):
        return self.__info_id
    def get_name(self):
        return self.__name 
    def get_address(self):
        return self.__address
    def get_card_number(self):
        return self.__card_number 
    def get_exp_month(self):
        return self.__exp_month
    def get_exp_year(self):
        return self.__exp_year
    def get_cvv(self):
        return self.__cvv
    def get_date(self):
        return self.__date

    
    def set_info_id(self, info_id):
        self.__info_id = info_id
    def set_name(self, name):
        self.__name = name
    def set_address(self, address):
        self.__address = address
    def set_card_number(self, card_number):
        self.__card_number = card_number
    def set_month(self, exp_month):
        self.__exp_month = exp_month
    def set_year(self, exp_year):
        self.__exp_year = exp_year
    def set_cvv(self, cvv):
        self.__cvv = cvv
    def set_date(self, date):
        self.__date = date