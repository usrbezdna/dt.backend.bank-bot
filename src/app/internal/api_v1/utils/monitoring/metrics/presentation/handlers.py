from prometheus_client import Counter


class PrometheusMetrics:
    fav_counter = Counter("list_fav_calls", "Number of calls of /list_fav from Telegram")

    @classmethod
    def inc_fav_counter(cls):
        cls.fav_counter.inc()
