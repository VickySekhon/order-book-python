import math
from typing import Literal, Sequence
from collections import defaultdict
from datetime import datetime
from dataclasses import dataclass, field

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

            match = self._find_match(order)

            if not match:
                # TODO: do we need the index anywhere?
                insertion_indx = self.add_order(order)
                spread = self._update_spread(order)
                if spread:
                    print(f"Updated spread on {order.asset} -> {spread}")
                return

            self.execute_trade(order, match)

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

    # returns the index of resting order that fulfills this trade
    def _find_match(self, order: Order) -> int | None:
        _, price, _, order_type, _, _ = order

        if order_type == "Ask":
            match_pool = self.book.get("Bid")
        else:
            match_pool = self.book.get("Ask")

        for resting_indx, resting_order in enumerate(match_pool):
            if resting_order.price <= price:
                return resting_indx

        return None

    # Performs the trade and handles quantity adjustment/removal of old /appending 
    def execute_trade(self, buyer: Order, seller: Order):
        asset = buyer.asset

        if buyer.order_id <= seller.order_id:
            price = buyer.price
        else:
            price = seller.price

        # executes the trade at "price"
        # new_buyer = buyer after trade (quantity mutated)
        # new_seller = seller after trade (quantity mutated)
        self._update_book([new_buyer, new_seller])
        self._update_last_traded_price(asset, price)
        pass

    def _update_book(self, orders: list[Order]) -> None:
        pass

    def _update_spread(self, order: Order) -> float:
        _, price, asset, order_type, _, _ = order
        best_order = self.book.get(order_type)[0]
        
        # This is the only condition where spread needs recomputation
        if best_order is order:
            # find the best order on the other side
            if order_type == "Ask":
                sorted_by_asset = sorted(self.book.get("Bid"), key=lambda pending_order : pending_order.asset == asset)
                best_order_on_other_side = sorted_by_asset[0]
            else:
                sorted_by_asset = sorted(self.book.get("Ask"), key=lambda pending_order : pending_order.asset == asset)
                best_order_on_other_side = sorted_by_asset[0]
            
            spread = self._calculate_spread(best_order.price, best_order_on_other_side.price)
            self.set_spread(asset, spread)
            self.set_last_traded_price(asset, price)

    def _calculate_spread(self, price1, price2):
        return math.abs(price1 - price2)

    def set_spread(self, asset: Universe, spread: float) -> None:
        assets[asset]["spread"] = spread
        
    def set_last_traded_price(self, asset: Universe, price: float) -> None:
        assets[asset]["price"] = price

    def __str__(self):
        return ""
