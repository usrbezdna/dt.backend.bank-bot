from prometheus_client import Counter, Gauge

class PrometheusMetrics:


    send_to_user_counter = Counter("counter_for_send_to_user", "Shows number of /send_to_user calls")
    @classmethod
    def inc_send_to_user_counter(cls):
        cls.send_to_user_counter.inc()

    send_to_account_counter = Counter("counter_for_send_to_account", "Represents number of /send_to_account calls")
    @classmethod
    def inc_send_to_account_counter(cls):
        cls.send_to_account_counter.inc()

    send_to_card_counter = Counter("counter_for_send_to_card", "Number of /send_to_card calls")
    @classmethod
    def inc_send_to_card_counter(cls):
        cls.send_to_card_counter.inc()


    tx_values_gauge = Gauge("gauge_for_tx_values", "Payment transactions values")
    @classmethod
    def set_tx_values_gauge(cls, tx_value):
        cls.tx_values_gauge.set(tx_value)


    cards_number_gauge = Gauge("gauge_for_current_number_of_cards", "Displays current number of user Cards in DB")
    @classmethod
    def set_cards_number_gauge(cls, current_card_number):
        cls.cards_number_gauge.set(current_card_number)

    accounts_number_gauge = Gauge("gauge_for_current_number_of_accounts", "Returns current number of payment Accounts in DB")
    @classmethod
    def set_cards_number_gauge(cls, current_account_number):
        cls.accounts_number_gauge.set(current_account_number)
        
    
