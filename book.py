from typing import Literal, Sequence
from collections import defaultdict

assets = {
    "AAPL": {"price": 291, "spread": 0},
    "AMZN": {"price": 238, "spread": 0},
    "GOOGL": {"price": 359, "spread": 0},
    "MSFT": {"price": 390, "spread": 0},
    "NVDA": {"price": 205, "spread": 0},
    "TSLA": {"price": 406, "spread": 0},
}

TRADABLE_ASSETS = assets.keys()
VALID_ORDERS = ("Bid", "Ask")

Universe = Literal["AAPL", "AMZN", "GOOGL", "MSFT", "NVDA", "TSLA"]
OrderType = Literal["Bid", "Ask"]

order_id = 1


class Order:
    def __init__(self, quantity: int, price: float, asset: Universe, order_type: OrderType):
        if quantity <= 0:
            raise ValueError("Quantity cannot be negative.")
        else:
            self.quantity = quantity
            
        if price <= 0:
            raise ValueError("Price cannot be negative.")
        else:
            self.price = price

        if asset not in TRADABLE_ASSETS:
            raise ValueError(
                f"Cannot trade asset: {asset}. Tradable assets: {list(TRADABLE_ASSETS)}"
            )
        else:
            self.asset = asset

        if order_type not in VALID_ORDERS:
            raise ValueError(
                f"Invalid order: {order_type}. Orders can only be: {list(VALID_ORDERS)}"
            )
        else:
            self.order_type = order_type

        global order_id
        self.order_id = order_id
        order_id += 1

    # @property
    # def quantity(self):
    #     return self._quantity

    # @quantity.setter
    # def quantity(self, quantity):
    #     if quantity <= 0:
    #         raise ValueError("Quantity cannot be negative.")
    #     self.quantity = quantity

    def __str__(self):
        return f"""Quantity: {self.quantity}\nPrice: {self.price}\nAsset: {self.asset}\nOrder Type: {self.order_type}\nOrder ID: {self.order_id}"""


class Book:
    def __init__(self):
        self.book: list[Order] = []

        # Tracks prices
        global assets
        self.assets = assets

        # # Tracks volume
        # self.volume

    """ 
    A newly submitted order can clear multiple orders.
    
    Steps (repeats until order quantity):
    1. looks for a match 
    """

    def submit_order(self, order: Order):
        while order.quantity > 0:
            
            match = self._find_match(order)
            
            if not match:
                self.book.append(order)
                self._calculate_spread(order.asset)
                return

            buyer_indx, seller_indx = match
            buyer, seller = self.book[buyer_indx], self.book[seller_indx]
            self._execute_trade(buyer, seller)

    # returns the indexes of the buyer and seller, none if no match
    def _find_match(self, order: Order) -> tuple[int, int] | None:
        # matches order based on limit buy/sell
        # bid -> matches with earliest ask with ask <= bid
        # ask -> matches with earliest bid with bid >= ask
        pass

    def _execute_trade(self, buyer: Order, seller: Order):
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

    def _calculate_spread(self, asset: Universe) -> float:
        pass

    def _update_last_traded_price(self, asset: Universe, price: float) -> None:
        self.assets["asset"]["price"] = price
        
    def __str__(self):
        return ""
