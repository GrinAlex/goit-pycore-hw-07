from colorama import Fore
from collections import UserDict
from datetime import datetime, timedelta


class InputPhoneError(Exception):
    """Exception for input phone error"""
    pass


class InputBirthdayError(Exception):
    """Exception for input birthday error"""
    pass


def input_error(func):
    """Decorator to handle input errors for contact functions."""
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return f"{Fore.RED}Give correct command please{Fore.RESET}"
        except IndexError:
            return f"{Fore.RED}Enter the argument for the command{Fore.RESET}"
        except KeyError:
            return f"{Fore.RED}This contact does not exist{Fore.RESET}"
        except InputPhoneError:
            return f"{Fore.RED}Phone number must be 10 digits.{Fore.RESET}"
        except InputBirthdayError:
            return f"{Fore.RED}Invalid date format. Use DD.MM.YYYY{Fore.RESET}"
    return inner


def parse_input(user_input):
    """Function for parsing input parameters"""
    if len(user_input) != 0:
        cmd, *args = user_input.split()
        cmd = cmd.strip().lower()
    else:
        return False, ''
    return cmd, *args


class Field:
    """Class for field"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    """Class for name"""
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty.")
        super().__init__(value)


class Phone(Field):
    """Class for phone number"""
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise InputPhoneError
        super().__init__(value)


class Birthday(Field):
    """Class for birthday"""
    def __init__(self, value):
        try:
            parse_date = datetime.strptime(value, "%d.%m.%Y")
            super().__init__(parse_date.date())
        except:
            raise InputBirthdayError
    
    def __str__(self):
        date = self.value.strftime("%d.%m.%Y")
        return date      

class Record:
    """Class for record"""
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    
    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        self.phones.append(phone)
    
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

    def add_birthday(self, value: str):
        self.birthday = Birthday(value)

    def __str__(self):
        return f"Contact name: {self.name.value:<20} phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    """Class for address book"""
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name):
        if name in self.data:
            return self.data[name]
        else:
            return None
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]
    
    def get_upcoming_birthdays(self):
        """Get a list of users with birthdays in the next 7 days."""
        today = datetime.today().date()

        upcoming_birthdays = []

        for key, user in self.data.items():
            selected_user = {} # Dictionary to hold user info for congratulations
            if user.birthday is not None:
                user_birthday = user.birthday.value
                birthday_this_year = user_birthday.replace(year=today.year) # Birthday date for the current year
                days_until_birthday = (birthday_this_year - today).days

                if 0 <= days_until_birthday <= 7: # Check if birthday is within the next 7 days
                    selected_user["name"] = key
                    if birthday_this_year.weekday() < 5:  # Check if birthday is on a weekday
                        selected_user["congratulation_date"] = birthday_this_year.strftime("%d.%m.%Y")
                    else:  # If birthday is on weekend, set congratulation date to next Monday
                        days_to_monday = 7 - birthday_this_year.weekday() # Days to next Monday
                        congratulation_date = birthday_this_year + timedelta(days=days_to_monday) # Calculate next Monday
                        selected_user["congratulation_date"] = congratulation_date.strftime("%d.%m.%Y")
                    upcoming_birthdays.append(selected_user)
        return upcoming_birthdays
    

@input_error
def add_contact(args, book: AddressBook):
    """Add a new contact to the contacts dictionary."""
    name, phone, *_ = args
    record = book.find(name)
    message = f"{Fore.GREEN}Contact updated.{Fore.RESET}"
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = f"{Fore.GREEN}Contact added.{Fore.RESET}"
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    """Change the phone number of an existing contact."""
    name, phone_old, phone_new = args[0], args[1], args[2]
    record = book.find(name)
    if record is None:
        raise KeyError
    else:
        record_phone = record.find_phone(phone_old)
        if record_phone is None:
            return f"{Fore.RED}Phone {phone_old} for contact {name} not found.{Fore.RESET}"
        else:
            record.remove_phone(phone_old)
            record.add_phone(phone_new)
            return f"{Fore.GREEN}Phone {phone_old} for contact {name} was updated to {phone_new}.{Fore.RESET}"


@input_error
def get_phone(args, book: AddressBook):
    """Get phone numbers of a contact."""
    name, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError
    else:
        return f"{Fore.GREEN}{record}{Fore.RESET}"


@input_error    
def get_all_contacts(book: AddressBook):
    """ Return all contacts"""
    for record in book.data.values():
        print(f"{Fore.GREEN}{record}{Fore.RESET}")


@input_error
def add_birthday(args, book):
    """Add a birthday to contact."""
    name, birth, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError  
    else:
        record.add_birthday(birth)
    return f"{Fore.GREEN}Birthday was added to contact {name}.{Fore.RESET}"


@input_error
def show_birthday(args, book: AddressBook):
    """Show contact birthday"""
    name, *_ = args
    record = book.find(name)
    if record is None:
        return f"{Fore.RED}Contact {name} not found.{Fore.RESET}"
    else:
        birth = record.birthday
        if birth is None:
            return f"{Fore.RED}No information on birthday of contact {name}.{Fore.RESET}"
        else:
            return f"{Fore.GREEN}Contact {name} have birthday {birth}{Fore.RESET}"


@input_error
def birthdays(book: AddressBook):
    """Show upcoming birthdays"""
    upcoming_birthdays = book.get_upcoming_birthdays()
    if len(upcoming_birthdays) < 1:
        print(f"{Fore.RED}No contacts with birthday in future 7 days.{Fore.RESET}")
    else:
        for contact in upcoming_birthdays:
            print(f"{Fore.GREEN}{contact['name']}. Congratulation date: {contact['congratulation_date']}{Fore.RESET}")  


def main():
    book = AddressBook()
    print(f"{Fore.BLUE}Welcome to the assistant bot!{Fore.RESET}")
    while True:
        user_input = input(f"{Fore.BLUE}Enter a command: {Fore.RESET}")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print(f"{Fore.BLUE}Good bye!{Fore.RESET}")
            break
        elif command == "hello":
            print(f"{Fore.BLUE}How can I help you?{Fore.RESET}")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(get_phone(args, book))
        elif command == "all":
            get_all_contacts(book)
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
             print(show_birthday(args, book))
        elif command == "birthdays":
           birthdays(book)
        else:
            print(f"{Fore.RED}Invalid command.{Fore.RESET}")


if __name__ == '__main__':
    main()

