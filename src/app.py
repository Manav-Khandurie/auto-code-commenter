import json
import os

INVENTORY_FILE = "bookstore_inventory.json"

class Book:
    def __init__(self, title, author, price, stock):
        self.title = title
        self.author = author
        self.price = price
        self.stock = stock

    def to_dict(self):
        return {
            "title": self.title,
            "author": self.author,
            "price": self.price,
            "stock": self.stock
        }

    @staticmethod
    def from_dict(data):
        return Book(
            title=data["title"],
            author=data["author"],
            price=data["price"],
            stock=data["stock"]
        )

class Inventory:
    def __init__(self):
        self.books = []
        self.load_inventory()

    def load_inventory(self):
        if os.path.exists(INVENTORY_FILE):
            with open(INVENTORY_FILE, "r") as file:
                data = json.load(file)
                self.books = [Book.from_dict(b) for b in data]
        else:
            self.books = []

    def save_inventory(self):
        with open(INVENTORY_FILE, "w") as file:
            json.dump([b.to_dict() for b in self.books], file, indent=4)

    def add_book(self, book):
        for b in self.books:
            if b.title == book.title and b.author == book.author:
                b.stock += book.stock
                return
        self.books.append(book)

    def remove_book(self, title, author):
        self.books = [b for b in self.books if not (b.title == title and b.author == author)]

    def update_stock(self, title, author, change):
        for b in self.books:
            if b.title == title and b.author == author:
                b.stock += change
                if b.stock < 0:
                    b.stock = 0
                return

    def list_books(self):
        for book in self.books:
            print(f"{book.title} by {book.author} - ${book.price:.2f} - Stock: {book.stock}")

    def search_books(self, keyword):
        results = []
        for book in self.books:
            if keyword.lower() in book.title.lower() or keyword.lower() in book.author.lower():
                results.append(book)
        return results

def main():
    inventory = Inventory()

    while True:
        print("\n--- Bookstore Inventory ---")
        print("1. List books")
        print("2. Add book")
        print("3. Remove book")
        print("4. Update stock")
        print("5. Search books")
        print("6. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            inventory.list_books()

        elif choice == "2":
            title = input("Title: ")
            author = input("Author: ")
            price = float(input("Price: "))
            stock = int(input("Stock: "))
            new_book = Book(title, author, price, stock)
            inventory.add_book(new_book)
            inventory.save_inventory()

        elif choice == "3":
            title = input("Title to remove: ")
            author = input("Author: ")
            inventory.remove_book(title, author)
            inventory.save_inventory()

        elif choice == "4":
            title = input("Title: ")
            author = input("Author: ")
            change = int(input("Change in stock (use negative to decrease): "))
            inventory.update_stock(title, author, change)
            inventory.save_inventory()

        elif choice == "5":
            keyword = input("Enter keyword to search: ")
            results = inventory.search_books(keyword)
            if results:
                for book in results:
                    print(f"{book.title} by {book.author} - ${book.price:.2f} - Stock: {book.stock}")
            else:
                print("No matching books found.")

        elif choice == "6":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
