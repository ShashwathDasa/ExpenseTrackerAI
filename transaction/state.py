class PendingTransactionStore:
    def __init__(self):
        self.transactions = {}

    def create(self, chat_id, transaction):
        self.transactions[chat_id] = transaction

    def get(self, chat_id):
        return self.transactions.get(chat_id)

    def update(self, chat_id, **fields):
        if chat_id not in self.transactions:
            return None

        self.transactions[chat_id].update(fields)
        return self.transactions[chat_id]

    def clear(self, chat_id):
        self.transactions.pop(chat_id, None)