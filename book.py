from typing import Literal, Sequence
from collections import defaultdict
from datetime import datetime
from dataclasses import dataclass, field


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

@dataclass
class Order:
    quantity: int
    price: float
    asset: Universe
    order_type: OrderType
    submission_time: datetime = field(default_factory=datetime.now)
    order_id: int = field(default=0, init=False)
    fulfilled: bool = False

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
        return f"""Quantity: {self.quantity}\nPrice: {self.price}\nAsset: {self.asset}\nOrder Type: {self.order_type}\nOrder ID: {self.order_id}\nTime Submitted: {self.submission_time}\nFulfilled: {self.fulfilled}"""


class Book:
    def __init__(self):
        self.book: list[Order] = []

        # Tracks prices
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
        
        quantity, price, asset, order_type, submission_time = order
        asks = [posted_order for posted_order in self.book if posted_order.fulfilled == False and posted_order.order_type == "Ask"]
        bids = [posted_order for posted_order in self.book if posted_order.fulfilled == False and posted_order.order_type == "Bid"]
        if order_type == "Bid":
            for current_order in asks:
                pass
        else:
            for current_order in bids:
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
        current_spread = self.assets.get(asset).get("spread")
        orders_of_this_asset: list[Order] = [order for order in self.book if order.asset == asset]
        
        if not orders_of_this_asset or ...:
            return
        bids = sorted([order for order in orders_of_this_asset if order.order_type == "Bid"], key=lambda x : x.price, reverse=True)
        asks = sorted([order for order in orders_of_this_asset if order.order_type == "Ask"], key=lambda x : x.price)
        
        lowest_ask = asks[0]
        highest_bid = bids[0]
        
        if lowest_ask - highest_bid == current_spread:
            print(f"Spread is unchanged for asset: {asset}")
            return
        
        return lowest_ask - highest_bid

    def _update_last_traded_price(self, asset: Universe, price: float) -> None:
        self.assets["asset"]["price"] = price
        
    def __str__(self):
        return ""
