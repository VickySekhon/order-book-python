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

order_id = 1


@dataclass
class Order:
    quantity: int
    price: float
    asset: Universe
    order_type: OrderType
    submission_time: datetime = field(default_factory=datetime.now)
    order_id: int = field(default=0, init=False)

    def __post_init__(self):
        """Validate order parameters and assign order_id"""
        if self.quantity <= 0:
            raise ValueError("Quantity cannot be negative.")

        if self.price <= 0:
            raise ValueError("Price cannot be negative.")

        if self.asset not in TRADABLE_ASSETS:
            raise ValueError(
                f"Cannot trade asset: {self.asset}. Tradable assets: {list(TRADABLE_ASSETS)}"
            )

        if self.order_type not in VALID_ORDERS:
            raise ValueError(
                f"Invalid order: {self.order_type}. Orders can only be: {list(VALID_ORDERS)}"
            )

        global order_id
        self.order_id = order_id
        order_id += 1

    def __iter__(self):
        """Allow unpacking of order: quantity, price, asset, order_type = order"""
        return iter([self.quantity, self.price, self.asset, self.order_type])

    def __str__(self):
        return f"""Quantity: {self.quantity}\nPrice: {self.price}\nAsset: {self.asset}\nOrder Type: {self.order_type}\nOrder ID: {self.order_id}\nTime Submitted: {self.submission_time}\n"""


class Book:
    def __init__(self):
        self._book: dict[OrderType, list[Order]] = {"Bid": [], "Ask": []}
        """ 
        self.book = {
            "Ask": [
                    Order(quantity, price, asset, order_type, submission_time, order_id),
                    ^
                    | ordered by price increasing
            ],
            "Bid": [
                    Order(quantity, price, asset, order_type, submission_time, order_id),
                    |
                    V ordered by price decreasing
            ]
        }
        """

        # # Tracks volume
        # self.volume
        
    @property
    def book(self):
        return self._book
    
    def get(self, key):
        return self._book.get(key)

    @property
    def length(self):
        return len(self.book.get("Bid")), len(self.book.get("Ask"))
    
    @book.setter
    def book(self, value):
        raise AttributeError("Book cannot be reassigned manually, instead mutate it by calling submit_order().")

    """ 
    A newly submitted order can clear multiple orders.
    
    Steps (repeats until order quantity):
    1. looks for a match 
    """

    def submit_order(self, order: Order):
        while order.quantity > 0:

            match_indx = self._find_match(order)

            if match_indx is None:
                if self._order_exists(order.order_type, order.order_id):
                    return
                
                self.add_order(order)
                spread = self._update_spread(order.asset)
                if spread:
                    print(f"Updated spread on {order.asset} -> {spread}")
                return

            self.execute_trade(order, match_indx)

    # performs insertion sort and returns index where inserted
    def add_order(self, order: Order) -> None | Exception:
        _, price, _, order_type = order

        for pos, resting_order in enumerate(self.book.get(order_type)):
            if (order_type == "Bid" and price >= resting_order.price) or (
                order_type == "Ask" and price <= resting_order.price
            ):
                self.book[order_type].insert(pos, order)
                return pos

        self.book[order_type].append(order)
        return -1

    # returns the index of resting order that fulfills this trade fully or partially
    def _find_match(self, order: Order) -> int | None:
        _, price, asset, order_type = order

        if order_type == "Ask":
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
        quantity, price, asset, order_type = order
        
        if order_type == "Ask":
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
            if not self._order_exists(order_type, order.order_id):
                self.add_order(order)
        self._update_spread(asset)
        self.set_last_traded_price(asset, matched_price)
        self.log_updates(order, matched_order)
    
    def log_updates(self, order, matched_order):
        print(f"---------------------------------------------\nMatched order_id {order.order_id} to order_id {matched_order.order_id} at ${matched_order.price}")
        asset_names = list(assets.keys())
        prices = [assets[asset]["price"] for asset in assets]
        spreads = [assets[asset]["spread"] for asset in assets]
        print(f"Updated Universe:")
        print(tabulate([["Asset", "Last Traded Price", "Spread (Highest Bid <-> Lowest Ask)"], [asset_names, prices, spreads]]))
        
    def _order_exists(self, order_type: OrderType, order_id: int) -> bool:
        for order in self.book.get(order_type):
            if order.order_id == order_id:
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
    print(book)
    # 2) quantity > resting order quantity
    book.submit_order(Order(4,200, "GOOGL", "Ask"))
    print(book)
    
    return

if __name__ == "__main__":
    main()