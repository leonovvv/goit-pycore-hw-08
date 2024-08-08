from collections import UserDict
from datetime import datetime, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if str(value).strip() == '':
            raise Exception('No name')

        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        value = str(value)

        if not value.isdigit() or  len(value) != 10:
            raise Exception('Phone should be 10 digits long')

        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            super().__init__(datetime.strptime(value, "%d.%m.%Y").date())
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones.remove(Phone(phone))

    def edit_phone(self, old_phone, new_phone):
        i = 0
        while i < len(self.phones):
            if str(self.phones[i]) == old_phone:
                self.phones[i] = Phone(new_phone)
                break
            i += 1

    def find_phone(self, lookup_phone):
        for phone in self.phones:
            if str(phone) == lookup_phone:
                return phone

        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):
    def add_record(self, record):
        if record.name in self.data:
            raise Exception('Duplicate name')

        self.data[str(record.name)] = record

    def find(self, name):
        if name not in self.data:
            return None

        return self.data[name]

    def delete(self, name):
        if name not in self.data:
            raise Exception('Name not found')

        self.data.pop(name)

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []

        for name in self.data:
            birthday_date = self.data[name].birthday.value
        
            birthday_this_year = birthday_date.replace(year=today.year)
        
            if birthday_this_year < today:
                birthday_this_year = birthday_date.replace(year=today.year + 1)
        
            delta_days = (birthday_this_year - today).days
        
            if 0 <= delta_days <= 7:
                if birthday_this_year.weekday() >= 5:
                    birthday_this_year += timedelta(days=(7 - birthday_this_year.weekday()))
            
                upcoming_birthdays.append({
                    'name': name,
                    'congratulation_date': birthday_this_year.strftime('%Y.%m.%d')
                })

        return upcoming_birthdays

def input_command_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Input a valid command."

    return inner

@input_command_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as ex:
            return str(ex)#"Give me name and phone please."
        except KeyError:
            return "Contact was not found"
        except IndexError:
            return "Give me contact name to return phone for, please."

    return inner

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        try:
            if record.find_phone(phone) is not None:
                return "This phone already exists in this record"

            record.add_phone(phone)
        except Exception as ex:
            return ex
    return message

@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args

    if name not in book:
        return f"{name} contact is not found"

    if book[name].find_phone(old_phone) is None:
        return f"Phone: {old_phone} is not found"

    try:
        book[name].edit_phone(old_phone, new_phone)
    except Exception as ex:
        return ex

    return "Contact updated."

@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if record is None:
        return f"{name} contact is not found"


    return {'; '.join(p.value for p in record.phones)}

#Couldn't find any possible exceptions here, so no decorator
def show_all(book):
    result = ""
    for name in book:
        result += f"{str(book[name])}\r\n"
    return result.strip()

@input_error
def add_birthday(args, book):
    name, birthday = args
    book[name].add_birthday(birthday)
    return 'Birthday added.'

@input_error
def show_birthday(args, book):
    name = args[0]
    return book[name].birthday

def birthdays(book):
    return book.get_upcoming_birthdays()

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()




