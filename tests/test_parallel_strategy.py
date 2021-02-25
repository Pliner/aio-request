from aio_request import Deadline, DefaultResponseClassifier, RequestStrategiesFactory, get, linear_delays
from tests.conftest import FakeRequestSender, FakeResponseConfiguration


async def test_timeout_because_of_expiration():
    strategies_factory = RequestStrategiesFactory(
        FakeRequestSender(
            [
                FakeResponseConfiguration(status=200, delay_seconds=5),
                FakeResponseConfiguration(status=200, delay_seconds=5),
                FakeResponseConfiguration(status=200, delay_seconds=5),
            ],
        ),
        base_url="http://service.com",
    )
    forking_strategy = strategies_factory.parallel()
    deadline = Deadline.from_timeout(1)
    async with forking_strategy.request(get("hello"), deadline=deadline) as response:
        assert response.status == 408
        assert deadline.expired


async def test_succeed_response_received_first_slow_request():
    strategies_factory = RequestStrategiesFactory(
        FakeRequestSender([FakeResponseConfiguration(status=200, delay_seconds=5), 200]),
        base_url="http://service.com",
    )
    forking_strategy = strategies_factory.parallel()
    deadline = Deadline.from_timeout(1)
    async with forking_strategy.request(get("hello"), deadline=deadline) as response:
        assert response.status == 200
        assert not deadline.expired


async def test_succeed_response_received():
    strategies_factory = RequestStrategiesFactory(
        request_sender=FakeRequestSender([489, 200]),
        response_classifier=DefaultResponseClassifier(),
        base_url="http://service.com",
    )
    forking_strategy = strategies_factory.parallel()
    deadline = Deadline.from_timeout(1)
    async with forking_strategy.request(get("hello"), deadline=deadline) as response:
        assert response.status == 200
        assert not deadline.expired


async def test_succeed_response_not_received_too_many_failures():
    strategies_factory = RequestStrategiesFactory(
        request_sender=FakeRequestSender([499, 499, 499]),
        response_classifier=DefaultResponseClassifier(),
        base_url="http://service.com",
    )
    forking_strategy = strategies_factory.parallel(attempts_count=3, delays_provider=linear_delays())
    deadline = Deadline.from_timeout(1)
    async with forking_strategy.request(get("hello"), deadline=deadline) as response:
        assert response.status == 499
        assert not deadline.expired
