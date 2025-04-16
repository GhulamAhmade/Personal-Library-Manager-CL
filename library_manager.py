import json
import os
import time
import sys
from typing import List, Dict, Optional
from colorama import init, Fore, Back, Style
from datetime import datetime

# Initialize colorama for Windows support
init(autoreset=True)

class Book:
    def __init__(self, title: str, author: str, year: int, genre: str, read: bool):
        self.title = title
        self.author = author
        self.year = year
        self.genre = genre
        self.read = read

    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'author': self.author,
            'year': self.year,
            'genre': self.genre,
            'read': self.read
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Book':
        return cls(
            title=data['title'],
            author=data['author'],
            year=data['year'],
            genre=data['genre'],
            read=data['read']
        )

    def __str__(self) -> str:
        read_status = f"{Fore.GREEN}Read" if self.read else f"{Fore.RED}Unread"
        return f"{Fore.CYAN}{self.title}{Style.RESET_ALL} by {Fore.YELLOW}{self.author}{Style.RESET_ALL} ({Fore.MAGENTA}{self.year}{Style.RESET_ALL}) - {Fore.BLUE}{self.genre}{Style.RESET_ALL} - {read_status}{Style.RESET_ALL}"

class LibraryManager:
    def __init__(self, filename: str = "library.json"):
        self.filename = filename
        self.books: List[Book] = []
        self.load_library()

    def print_header(self, text: str) -> None:
        """Print a formatted header."""
        print(f"\n{Fore.CYAN}{'=' * 50}")
        print(f"{text.center(50)}")
        print(f"{'=' * 50}{Style.RESET_ALL}\n")

    def loading_animation(self, text: str, duration: float = 1.0) -> None:
        """Display a loading animation."""
        print(f"\n{Fore.YELLOW}{text}", end="", flush=True)
        for _ in range(3):
            time.sleep(duration/3)
            print(".", end="", flush=True)
        print(f"{Style.RESET_ALL}\n")

    def load_library(self) -> None:
        """Load the library from a JSON file if it exists."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as file:
                    data = json.load(file)
                    self.books = [Book.from_dict(book_data) for book_data in data]
                self.loading_animation("Loading your library")
            except (json.JSONDecodeError, KeyError):
                print(f"{Fore.RED}Error loading library file. Starting with empty library.{Style.RESET_ALL}")
                self.books = []
        else:
            self.books = []

    def save_library(self) -> None:
        """Save the library to a JSON file."""
        try:
            with open(self.filename, 'w') as file:
                json.dump([book.to_dict() for book in self.books], file, indent=4)
            self.loading_animation("Saving your library")
        except IOError:
            print(f"{Fore.RED}Error saving library to file.{Style.RESET_ALL}")

    def add_book(self) -> None:
        """Add a new book to the library."""
        self.print_header("Add a Book")
        title = input(f"{Fore.CYAN}Enter the book title: {Style.RESET_ALL}").strip()
        author = input(f"{Fore.CYAN}Enter the author: {Style.RESET_ALL}").strip()
        
        while True:
            try:
                year = int(input(f"{Fore.CYAN}Enter the publication year: {Style.RESET_ALL}"))
                if year < 0:
                    raise ValueError
                break
            except ValueError:
                print(f"{Fore.RED}Please enter a valid year (positive integer).{Style.RESET_ALL}")
        
        genre = input(f"{Fore.CYAN}Enter the genre: {Style.RESET_ALL}").strip()
        
        while True:
            read_input = input(f"{Fore.CYAN}Have you read this book? (yes/no): {Style.RESET_ALL}").lower().strip()
            if read_input in ['yes', 'no']:
                read = read_input == 'yes'
                break
            print(f"{Fore.RED}Please enter 'yes' or 'no'.{Style.RESET_ALL}")
        
        new_book = Book(title, author, year, genre, read)
        self.books.append(new_book)
        self.save_library()
        print(f"\n{Fore.GREEN}Book added successfully!{Style.RESET_ALL}")

    def remove_book(self) -> None:
        """Remove a book from the library by title."""
        self.print_header("Remove a Book")
        title = input(f"{Fore.CYAN}Enter the title of the book to remove: {Style.RESET_ALL}").strip()
        
        found_books = [book for book in self.books if book.title.lower() == title.lower()]
        
        if not found_books:
            print(f"{Fore.RED}No book found with that title.{Style.RESET_ALL}")
            return
        
        if len(found_books) > 1:
            print(f"\n{Fore.YELLOW}Multiple books found with that title:{Style.RESET_ALL}")
            for i, book in enumerate(found_books, 1):
                print(f"{Fore.CYAN}{i}.{Style.RESET_ALL} {book}")
            
            while True:
                try:
                    choice = int(input(f"\n{Fore.CYAN}Enter the number of the book to remove: {Style.RESET_ALL}"))
                    if 1 <= choice <= len(found_books):
                        book_to_remove = found_books[choice - 1]
                        self.books.remove(book_to_remove)
                        self.save_library()
                        print(f"\n{Fore.GREEN}Book removed successfully!{Style.RESET_ALL}")
                        return
                    print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}Please enter a valid number.{Style.RESET_ALL}")
        else:
            self.books.remove(found_books[0])
            self.save_library()
            print(f"\n{Fore.GREEN}Book removed successfully!{Style.RESET_ALL}")

    def search_books(self) -> None:
        """Search for books by title or author."""
        self.print_header("Search for a Book")
        print(f"{Fore.CYAN}Search by:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}1.{Style.RESET_ALL} Title")
        print(f"{Fore.YELLOW}2.{Style.RESET_ALL} Author")
        
        while True:
            try:
                choice = int(input(f"\n{Fore.CYAN}Enter your choice: {Style.RESET_ALL}"))
                if choice in [1, 2]:
                    break
                print(f"{Fore.RED}Please enter 1 or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Please enter a valid number.{Style.RESET_ALL}")
        
        search_term = input(f"{Fore.CYAN}Enter the {'title' if choice == 1 else 'author'}: {Style.RESET_ALL}").strip().lower()
        
        if choice == 1:
            results = [book for book in self.books if search_term in book.title.lower()]
        else:
            results = [book for book in self.books if search_term in book.author.lower()]
        
        if not results:
            print(f"\n{Fore.RED}No matching books found.{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.GREEN}Matching Books:{Style.RESET_ALL}")
            for i, book in enumerate(results, 1):
                print(f"{Fore.CYAN}{i}.{Style.RESET_ALL} {book}")

    def display_all_books(self) -> None:
        """Display all books in the library."""
        self.print_header("Your Library")
        if not self.books:
            print(f"{Fore.YELLOW}Your library is empty.{Style.RESET_ALL}")
            return
        
        for i, book in enumerate(self.books, 1):
            print(f"{Fore.CYAN}{i}.{Style.RESET_ALL} {book}")

    def display_statistics(self) -> None:
        """Display library statistics."""
        self.print_header("Library Statistics")
        total_books = len(self.books)
        if total_books == 0:
            print(f"{Fore.YELLOW}No books in the library.{Style.RESET_ALL}")
            return
        
        read_books = sum(1 for book in self.books if book.read)
        percentage_read = (read_books / total_books) * 100
        
        print(f"{Fore.CYAN}Total books:{Style.RESET_ALL} {Fore.YELLOW}{total_books}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Percentage read:{Style.RESET_ALL} {Fore.YELLOW}{percentage_read:.1f}%{Style.RESET_ALL}")
        
        # Additional statistics
        genres = {}
        for book in self.books:
            genres[book.genre] = genres.get(book.genre, 0) + 1
        
        print(f"\n{Fore.CYAN}Books by genre:{Style.RESET_ALL}")
        for genre, count in sorted(genres.items(), key=lambda x: x[1], reverse=True):
            print(f"{Fore.YELLOW}{genre}:{Style.RESET_ALL} {count}")

    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def run(self) -> None:
        """Run the library manager program."""
        while True:
            self.clear_screen()
            print(f"\n{Fore.CYAN}{'=' * 50}")
            print(f"{'Personal Library Manager'.center(50)}")
            print(f"{'=' * 50}{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}Menu:{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}1.{Style.RESET_ALL} Add a book")
            print(f"{Fore.YELLOW}2.{Style.RESET_ALL} Remove a book")
            print(f"{Fore.YELLOW}3.{Style.RESET_ALL} Search for a book")
            print(f"{Fore.YELLOW}4.{Style.RESET_ALL} Display all books")
            print(f"{Fore.YELLOW}5.{Style.RESET_ALL} Display statistics")
            print(f"{Fore.YELLOW}6.{Style.RESET_ALL} Exit")
            
            try:
                choice = int(input(f"\n{Fore.CYAN}Enter your choice: {Style.RESET_ALL}"))
                
                if choice == 1:
                    self.add_book()
                elif choice == 2:
                    self.remove_book()
                elif choice == 3:
                    self.search_books()
                elif choice == 4:
                    self.display_all_books()
                elif choice == 5:
                    self.display_statistics()
                elif choice == 6:
                    self.loading_animation("Saving and exiting")
                    print(f"\n{Fore.GREEN}Library saved to file. Goodbye!{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED}Invalid choice. Please enter a number between 1 and 6.{Style.RESET_ALL}")
                
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            
            except ValueError:
                print(f"{Fore.RED}Please enter a valid number.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

if __name__ == "__main__":
    library = LibraryManager()
    library.run()
