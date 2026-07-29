import pytest
from src.book import Book, Order


def test_add_order():
     book = Book()
     my_order = Order(10, 255, "AAPL", "Bid")
     book.add_order(my_order)
     assert len(book["Bids"]) > 0