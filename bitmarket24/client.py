from datetime import datetime
from urllib import parse

import jwt
import requests


class MarketID:
    BCC_PLN = 'bcc_pln'
    BTC_PLN = 'btc_pln'
    BTG_PLN = 'btg_pln'
    LTC_BTC = 'ltc_btc'
    LTC_PLN = 'ltc_pln'


class OfferType:
    ASK = 'ask'
    BID = 'bid'


class OrderStatus:
    NEW = 'new'
    ACTIVE = 'active'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'


class BM24PLClientException(Exception):
    pass


class BM24PLClient:
    SELECTED_MARKET = None

    _base_url = 'https://bitmarket24.pl/api/v1'
    _market_status_url = 'https://bitmarket24.pl/api/{}/status.json'

    # PUBLIC
    _endpoint_order_book = '/public/orderbook?market={}'

    # CLIENT
    _endpoint_client_balance = '/user/me/balance'
    _endpoint_client_orderbook = '/orderbook'
    _endpoint_client_orders = '/orders'
    _endpoint_client_trades = '/trades'
    _endpoint_client_turnover = '/user/me/turnover'
    _endpoint_client_fee = '/user/me/fee'
    _endpoint_order = '/order'
    _endpoint_order_trades = '/order/{}/trades'

    def __init__(self, client_id, client_key):
        self._client_id = client_id
        self._client_key = client_key

    def _prepare_jwt(self):
        now = int(datetime.now().timestamp())
        headers = {"alg": "HS256", "typ": "JWT"}
        payload = {
            'sub': self._client_id,
            'iat': now,
            'exp': now + 3
        }

        return jwt.encode(
            payload,
            self._client_key,
            headers=headers,
        ).decode()

    @property
    def auth_headers(self):
        return {'Authorization': 'Bearer {}'.format(self._prepare_jwt())}

    @classmethod
    def make_get_request(cls, endpoint, headers=None):
        return requests.get(
            '{}{}'.format(cls._base_url, endpoint), headers=headers)

    @classmethod
    def make_post_request(cls, endpoint, data, headers=None):
        return requests.post(
            '{}{}'.format(cls._base_url, endpoint), json=data, headers=headers)

    def make_delete_request(self, endpoint):
        return requests.delete(
            '{}{}'.format(self._base_url, endpoint), headers=self.auth_headers
        )

    @classmethod
    def get_market_id(cls, market_id):

        if market_id is None:
            market_id = cls.SELECTED_MARKET

        if market_id is None:
            raise BM24PLClientException('Provide `market_id` or override `SELECTED_MARKET` attribute')

        return market_id

    @classmethod
    def get_qs_params_from_dict(cls, qs_dict):
        for key in list(qs_dict.keys()):
            if qs_dict[key] is None:
                del qs_dict[key]

        return parse.urlencode(qs_dict)

    @classmethod
    def get_market_status(cls, market_id=None):
        market_id = cls.get_market_id(market_id)
        return requests.get(cls._market_status_url.format(market_id.upper())).json()

    def get_order_book(self, market_id=None):
        market_id = self.get_market_id(market_id)

        return self.make_get_request(
            self._endpoint_order_book.format(market_id)).json()

    def get_client_balance(self):
        return self.make_get_request(
            self._endpoint_client_balance,
            headers=self.auth_headers
        ).json()

    def get_client_orders(
        self, market_id=None, order_type=None, status=None, limit=None, offset=None, dir=None
    ):
        market_id = self.get_market_id(market_id)
        qs_dict = dict(
            market=market_id,
            type=order_type,
            limit=limit,
            offset=offset,
            dir=dir
        )
        qs_string = self.get_qs_params_from_dict(qs_dict)

        if status is not None:
            qs_string = "{}&{}".format(
                qs_string, "&".join(["status[]={}".format(item) for item in status]))

        return self.make_get_request(
            "{}?{}".format(self._endpoint_client_orders, qs_string),
            headers=self.auth_headers
        ).json()

    def get_client_trades(self, order_type, market_id=None, limit=None, offset=None):
        market_id = self.get_market_id(market_id)
        qs_dict = dict(
            market=market_id,
            type=order_type,
            limit=limit,
            offset=offset,
        )
        qs_params = self.get_qs_params_from_dict(qs_dict)
        return self.make_get_request(
            "{}?{}".format(self._endpoint_client_trades, qs_params),
            headers=self.auth_headers
        ).json()

    def get_client_turnover(self):
        return self.make_get_request(
            self._endpoint_client_turnover,
            headers=self.auth_headers
        ).json()

    def get_client_fee(self):
        return self.make_get_request(
            self._endpoint_client_fee,
            headers=self.auth_headers
        ).json()

    def get_order_info(self, order_id):
        endpoint = '{}/{}'.format(self._endpoint_order, order_id)
        return self.make_get_request(endpoint, headers=self.auth_headers).json()

    def get_order_trades(self, order_id):
        endpoint = self._endpoint_order_trades.format(order_id)
        return self.make_get_request(endpoint, headers=self.auth_headers).json()

    def cancel_client_order(self, order_id):
        return self.make_delete_request(
            "{}/{}".format(self._endpoint_client_orderbook, order_id)).status_code == 202

    def cancel_client_orders(self, market_id=None, order_type=None):
        qs_dict = dict(
            market=market_id,
            type=order_type
        )
        qs_params = self.get_qs_params_from_dict(qs_dict)
        return self.make_delete_request(
            "{}?{}".format(self._endpoint_client_orderbook, qs_params))

    def make_bid(self, amount, rate, market_id=None):
        market_id = self.get_market_id(market_id)

        data = {
            "type": OfferType.BID,
            "market": market_id,
            "amount": amount,
            "rate": rate
        }
        return requests.post(
            "{}{}".format(self._base_url, self._endpoint_order),
            json=data,
            headers=self.auth_headers
        )

    def make_ask(self, amount, rate, market_id=None):
        market_id = self.get_market_id(market_id)

        data = {
            "type": OfferType.ASK,
            "market": market_id,
            "amount": amount,
            "rate": rate
        }
        return requests.post(
            "{}{}".format(self._base_url, self._endpoint_order),
            json=data,
            headers=self.auth_headers
        )
