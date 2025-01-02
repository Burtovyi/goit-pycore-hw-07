from datetime import datetime, timedelta

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, KeyError, IndexError) as e:
            return str(e)
    return wrapper

class Field:
    def __init__(self, value):
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class Name(Field):
    def __init__(self, value):
        if not value.isalpha():
            raise ValueError("Name must contain only alphabetic characters.")
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be 10 digits long.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            self._date = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)

    @property
    def date(self):
        return self._date


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        if not isinstance(phone, Phone):
            raise ValueError("Phone must be an instance of Phone class.")
        self.phones.append(phone)

    def remove_phone(self, phone):
        self.phones.remove(phone)

    def add_birthday(self, birthday):
        if not isinstance(birthday, Birthday):
            raise ValueError("Birthday must be an instance of Birthday class.")
        self.birthday = birthday

    def days_to_birthday(self):
        if not self.birthday:
            return None

        today = datetime.today().date()
        next_birthday = self.birthday.date.replace(year=today.year)

        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)

        return (next_birthday - today).days


class AddressBook:
    def __init__(self):
        self.records = {}

    def add_record(self, record):
        if not isinstance(record, Record):
            raise ValueError("Record must be an instance of Record class.")
        self.records[record.name.value] = record

    def find(self, name):
        return self.records.get(name)

    def get_upcoming_birthdays(self, days=7):
        today = datetime.today().date()
        upcoming = []

        for record in self.records.values():
            if record.birthday:
                next_birthday = record.birthday.date.replace(year=today.year)

                if next_birthday < today:
                    next_birthday = next_birthday.replace(year=today.year + 1)

                if 0 <= (next_birthday - today).days < days:
                    upcoming.append(record.name.value)

        return upcoming


@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        raise ValueError("Command 'add' requires both name and phone number.")
    name, phone = args[:2]
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(Phone(phone))
    return message

@input_error
def add_birthday(args, book):
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        raise ValueError("Contact not found.")
    record.add_birthday(Birthday(birthday))
    return f"Birthday added for {name}."

@input_error
def show_birthday(args, book):
    name, *_ = args
    record = book.find(name)
    if record is None or not record.birthday:
        raise ValueError("No birthday found for this contact.")
    return f"{name}'s birthday is {record.birthday.date.strftime('%d.%m.%Y')}"

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays."
    return "\n".join(upcoming)


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = user_input.split()

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            name, old_phone, new_phone, *_ = args
            record = book.find(name)
            if record is None:
                print("Contact not found.")
            else:
                try:
                    record.remove_phone(Phone(old_phone))
                    record.add_phone(Phone(new_phone))
                    print("Phone updated.")
                except ValueError:
                    print("Phone not found.")

        elif command == "phone":
            name, *_ = args
            record = book.find(name)
            if record is None:
                print("Contact not found.")
            else:
                phones = ", ".join(phone.value for phone in record.phones)
                print(f"{name}'s phones: {phones}")

        elif command == "all":
            for record in book.records.values():
                phones = ", ".join(phone.value for phone in record.phones)
                print(f"{record.name.value}: {phones}")

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
