# Client for Bitmarket24.pl API


## Features

### Public
* list of all active offers
* market status

### Orders
* cancel selected order
* cancel all orders
* order details
* list of client orders
* list of order transactions
* making orders

### Trades
* client trade list

### Client
* balance
* turnover
* fee


## Installation
Install _bitmarket24_ library from PYPI using your favourite package manager. It has dependency to _requests_ and _PyJWT_ (temporary) packages.

```
pip install bitmarket24
```



## Usage

```python

from bitmarket24 import BM24PLClient, MarketID, OrderStatus

# create global client
api = BM24PLClient(client_id='your client id', client_key='your secret key')

# ex. get your completed and active orders form LTC_PLN market
api.get_client_orders(market=MarketID.LTC_PLN, status=[OrderStatus.ACTIVE, OrderStatus.COMPLETED])

# make BID order - 10 LTC for 200 PLN
api.make_bid(amount=10, rate=200, market_id)

# get LTC_PLN market orders
api.get_order_book(MarketID.LTC_PLN)


# create BTC_PLN client
class BtcPlnBM24PLClient(BM24PLClient):
    SELECTED_MARKET = MarketID.BTC_PLN

btc_pln_api = BtcPlnBM24PLClient(client_id='your client id', client_key='your secret key')

# ex. get your completed and active orders form BTC_PLN market
btc_pln_api.get_client_orders(status=[OrderStatus.ACTIVE, OrderStatus.COMPLETED])
```