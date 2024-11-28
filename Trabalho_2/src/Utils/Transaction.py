class Transaction:
    def __init__(self, operations, items, values, sleep_time, transaction_id):
        """
        :param operations: List of operations (e.g., ["write", "read", "commit"]).
        :param items: List of items associated with the operations (e.g., ["x", "y"]).
        :param values: List of values (only for write operations).
        :param transaction_id: Transaction ID.
        """
        self.operations = operations
        self.items = items
        self.values = values
        self.id = transaction_id
        self.result = None
        self.sleep_time = sleep_time

    def get_op(self, i):
        """Gets the operation at index i."""
        if i < len(self.operations):
            return self.operations[i]
        return None

    def get_item(self, i):
        """Gets the item associated with the operation at index i."""
        if i < len(self.items):
            return self.items[i]
        return None

    def get_value(self, i):
        """Gets the value associated with the operation at index i (only for 'write')."""
        if i < len(self.values):
            return self.values[i]
        return None
