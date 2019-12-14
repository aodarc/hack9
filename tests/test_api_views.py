import requests


class TestBase:
    endpoint_url = 'http://localhost:8000/'


class TestSwitchPrice(TestBase):

    def test_reset_endpoint(self, benchmark):
        response = benchmark.pedantic(requests.get, args=(self.endpoint_url,), iterations=3, rounds=1000)
        assert response.status_code == 200

    def test_get_switch_price_endpoint(self, benchmark):
        number = 42
        price = 42
        url = f'{self.endpoint_url}switch/price?number={number}&price={price}'
        response = benchmark.pedantic(requests.get, args=(url,), iterations=3, rounds=1000)
        assert response.status_code == 200


class TestFinancial(TestBase):
    pass
