
from collections import UserDict
from datetime import datetime, timedelta


class NotFoundRecord(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"Record: {self.name} not foud"


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty.")
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            parse_date = datetime.strptime(value, "%d.%m.%Y")
            super().__init__(parse_date.date())
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
    
    def __str__(self):
        date = self.value.strftime("%d.%m.%Y")
        return date
      

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    
    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        self.phones.append(phone)

    def add_birthday(self, value: str):
        self.birthday = Birthday(value)
    
    def remove_phone(self, phone_number):
        phone_to_remove = None
        for phone in self.phones:
            if phone.value == phone_number:
                phone_to_remove = phone
                break
        if phone_to_remove:
            self.phones.remove(phone_to_remove)
    
    def edit_phone(self, old_number, new_number):
        for i, phone in enumerate(self.phones):
            if phone.value == old_number:
                self.phones[i] = Phone(new_number)
                return
    
    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name) -> Record:
        if name in self.data:
            return self.data[name]
        else:
            raise NotFoundRecord(name)
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]
    
    def get_upcoming_birthdays(self):
        """
        Get a list of users with birthdays in the next 7 days.
        """
        today = datetime.today().date() # Current date

        upcoming_birthdays = []

        for key, user in self.data.items():
            selected_user = {} # Dictionary to hold user info for congratulations
            user_birthday = user.birthday.value
            birthday_this_year = user_birthday.replace(year=today.year) # Birthday date for the current year
            days_until_birthday = (birthday_this_year - today).days # Amount days for biethday in current year

            if 0 <= days_until_birthday <= 7: # Check if birthday is within the next 7 days
                selected_user["name"] = key # Add user's name to the selected user dictionary
                if birthday_this_year.weekday() < 5:  # Check if birthday is on a weekday
                    selected_user["congratulation_date"] = birthday_this_year.strftime("%Y.%m.%d") # Add congratulation date in format YYYY.MM.DD
                else:  # If birthday is on weekend, set congratulation date to next Monday
                    days_to_monday = 7 - birthday_this_year.weekday() # Days to next Monday
                    congratulation_date = birthday_this_year + timedelta(days=days_to_monday) # Calculate next Monday
                    selected_user["congratulation_date"] = congratulation_date.strftime("%Y.%m.%d") # Add congratulation date in format YYYY.MM.DD
                upcoming_birthdays.append(selected_user) # Add selected user to the list
        return upcoming_birthdays
    
