import math
from typing import Literal, Sequence
from collections import defaultdict
from datetime import datetime
from dataclasses import dataclass, field
from tabulate import tabulate

# Global price tracker
assets = {
    "AAPL": {"price": 291, "spread": float('inf')},
    "AMZN": {"price": 238, "spread": float('inf')},
    "GOOGL":{"price": 359, "spread": float('inf')},
    "MSFT": {"price": 390, "spread": float('inf')},
    "NVDA": {"price": 205, "spread": float('inf')},
    "TSLA": {"price": 406, "spread": float('inf')},
}

TRADABLE_ASSETS = assets.keys()
VALID_ORDERS = ("Bid", "Ask")

Universe = Literal["AAPL", "AMZN", "GOOGL", "MSFT", "NVDA", "TSLA"]
OrderType = Literal["Bid", "Ask"]

id = 1


@dataclass
class Order:
    quantity: int
    price: float
    asset: Universe
    type: OrderType
    submission_time: datetime = field(default_factory=datetime.now)
    id: int = field(default=0, init=False)

    def __post_init__(self):
        """Validate order parameters and assign id"""
        if self.quantity <= 0:
            raise ValueError("Quantity cannot be negative or zero.")

        if self.price <= 0:
            raise ValueError("Price cannot be negative.")

        if self.asset not in TRADABLE_ASSETS:
            raise ValueError(
                f"Cannot trade asset: {self.asset}. Tradable assets: {list(TRADABLE_ASSETS)}"
            )

        if self.type not in VALID_ORDERS:
            raise ValueError(
                f"Invalid order: {self.type}. Orders can only be: {list(VALID_ORDERS)}"
            )

        global id
        self.id = id
        id += 1

    def __iter__(self):
        """Allow unpacking of order: quantity, price, asset, type = order"""
        return iter([self.quantity, self.price, self.asset, self.type])

    def __str__(self):
        return f"""Quantity: {self.quantity}\nPrice: {self.price}\nAsset: {self.asset}\nOrder Type: {self.type}\nOrder ID: {self.id}\nTime Submitted: {self.submission_time}\n\n"""


class Book:
    def __init__(self):
        self._book: dict[OrderType, list[Order]] = {"Bid": [], "Ask": []}
        """ 
        self.book = {
            "Ask": [
                    Order(quantity, price, asset, type, submission_time, id),
                    ^
                    | ordered by price increasing
            ],
            "Bid": [
                    Order(quantity, price, asset, type, submission_time, id),
                    |
                    V ordered by price decreasing
            ]
        }
        """
        
    @property
    def book(self):
        return self._book

    @property
    def length(self):
        return len(self.book.get("Bid")), len(self.book.get("Ask"))
    
    @book.setter
    def book(self, value):
        raise AttributeError("Book cannot be reassigned manually, instead mutate it by calling submit_order().")
    
    def get(self, key):
        return self._book.get(key)

    """ 
    A newly submitted order can clear multiple orders.
    
    Steps (repeats until order quantity):
    1. looks for a match 
    """

    def submit_order(self, order: Order):
        while order.quantity > 0:

            match_indx = self._find_match(order)

            if match_indx is None:
                if self._order_exists(order.type, order.id):
                    return
                
                self.add_order(order)
                spread = self._update_spread(order.asset)
                if spread:
                    print(f"Updated spread on {order.asset} -> {spread}")
                return

            self.execute_trade(order, match_indx)

    # performs insertion sort and returns index where inserted
    def add_order(self, order: Order) -> None | Exception:
        _, price, _, type = order

        for pos, resting_order in enumerate(self.book.get(type)):
            if (type == "Bid" and price >= resting_order.price) or (
                type == "Ask" and price <= resting_order.price
            ):
                self.book[type].insert(pos, order)
                return pos

        self.book[type].append(order)
        return -1

    # returns the index of resting order that fulfills this trade fully or partially
    def _find_match(self, order: Order) -> int | None:
        _, price, asset, type = order

        if type == "Ask":
            for indx, resting_bid in enumerate(self.book.get("Bid")):
                if resting_bid.asset == asset and price <= resting_bid.price:
                    return indx
        else:
            for indx, resting_ask in enumerate(self.book.get("Ask")):
                if resting_ask.asset == asset and resting_ask.price <= price:
                    return indx
        """
        Bid: (executes at price <= bid)
        resting_order.price <= order.price -> executes at resting_order.price
        
        Ask: (executes at price >= ask)
        order.price <= resting_order.price -> executes at resting_order.price
        """
        return None

    # Performs the trade and handles quantity adjustment/removal of old /appending 
    def execute_trade(self, order: Order, match_indx: int):
        quantity, price, asset, type = order
        
        if type == "Ask":
            match_pool = self.book.get("Bid")
        else:
            match_pool = self.book.get("Ask")
        
        matched_order = match_pool[match_indx]
        matched_quantity, matched_price, _, _ = matched_order
        if matched_quantity == quantity:
            match_pool.pop(match_indx)
            order.quantity = 0
        elif matched_quantity > quantity:
            updated_quantity = matched_quantity - quantity
            matched_order.quantity = updated_quantity
            order.quantity = 0
        else:
            match_pool.pop(match_indx)
            updated_quantity = quantity - matched_quantity
            order.quantity = updated_quantity
            if not self._order_exists(type, order.id):
                self.add_order(order)
        self._update_spread(asset)
        self.set_last_traded_price(asset, matched_price)
        self.log_updates(order, matched_order)
    
    def log_updates(self, order, matched_order):
        print(f"---------------------------------------------\nMatched id {order.id} to id {matched_order.id} at ${matched_order.price}")
        asset_names = list(assets.keys())
        prices = [assets[asset]["price"] for asset in assets]
        spreads = [assets[asset]["spread"] for asset in assets]
        print(f"Updated Universe:")
        print(tabulate([["Asset", "Last Traded Price", "Spread (Highest Bid <-> Lowest Ask)"], [asset_names, prices, spreads]]))
        
    def _order_exists(self, type: OrderType, id: int) -> bool:
        for order in self.book.get(type):
            if order.id == id:
                return True
        return False

    def _update_spread(self, asset) -> float:
        if not self.book.get("Bid") or not self.book.get("Ask"):
            return
        
        highest_bid = sorted(self.book.get("Bid"), key=lambda x : x.asset == asset, reverse=True)[0]
        lowest_ask = sorted(self.book.get("Ask"), key=lambda x : x.asset == asset)[0]
        spread = self._calculate_spread(lowest_ask.price, highest_bid.price)
        self.set_spread(asset, spread)

    def _calculate_spread(self, price1, price2):
        return abs(price1 - price2)

    def set_spread(self, asset: Universe, spread: float) -> None:
        assets[asset]["spread"] = spread
        
    def set_last_traded_price(self, asset: Universe, price: float) -> None:
        assets[asset]["price"] = price

    def __str__(self):
        string = f"\n"
        asks = ""
        for ask in self.book.get("Ask"):
            asks += str(ask)
        bids = ""
        for bid in self.book.get("Bid"):
             bids += str(bid)
        string += tabulate([["Bids", "Asks"], [bids, asks]],headers="firstrow")
        string += "\n"
        return string

def main():
    
    book = Book()
    book.submit_order(Order(1,300, "AAPL", "Ask"))
    print(book)
    book.submit_order(Order(3,200, "GOOGL", "Bid"))
    print(book)
    
    # fulfilled orders
    # 1) quantity is the same
    book.submit_order(Order(1,310, "AAPL", "Bid"))
    #print(book)
    # 2) quantity > resting order quantity
    book.submit_order(Order(4,200, "GOOGL", "Ask"))
    print(book)
    # 3) quantity < resting_order quantity
    book.submit_order(Order(4,300, "AMZN", "Ask"))
    print(book)
    book.submit_order(Order(3,310, "AMZN", "Bid"))
    print(book)
    
    
    return

if __name__ == "__main__":
    main()