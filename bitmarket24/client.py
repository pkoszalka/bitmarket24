from datetime import datetime

import jwt
import requests


LTC_PLN_MARKET_ID = 'LTC_PLN'


class Bitmarket24ApiClient:
    _base_url = 'https://bitmarket24.pl/api/v1'
    _market_status_url = 'https://bitmarket24.pl/api/{}/status.json'

    # PUBLIC
    _endpoint_order_book = '/public/orderbook?market={}'

    # CLIENT
    _endpoint_client_balance = '/user/me/balance'

    # ORDERS
    _endpoint_order = '/order'
    _endpoint_delete_order = '/orderbook/{}'

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
    def get_market_status(cls, market_id):
        return requests.get(cls._market_status_url.format(market_id))

    def get_client_balance(self):
        return self.make_get_request(
            self._endpoint_client_balance,
            headers=self.auth_headers
        )

    def get_order_book(self, market_id):
        return self.make_get_request(
            self._endpoint_order_book.format(market_id)).json()

    def get_order_info(self, order_id):
        endpoint = '{}/{}'.format(self._endpoint_order, order_id)
        return self.make_get_request(endpoint, headers=self.auth_headers)

    def delete_order(self, order_id):
        return requests.delete(self._endpoint_delete_order.format(order_id))

    def make_ltc_bid(self, amount, rate):
        data = {
            "type": "bid",
            "market": "ltc_pln",
            "amount": amount,
            "rate": rate
        }
        return requests.post(
            "{}{}".format(self._base_url, self._endpoint_order),
            json=data,
            headers=self.auth_headers
        )

    def make_ltc_ask(self, amount, rate):
        data = {
            "type": "ask",
            "market": "ltc_pln",
            "amount": amount,
            "rate": rate
        }
        return requests.post(
            "{}{}".format(self._base_url, self._endpoint_order),
            json=data,
            headers=self.auth_headers
        )
