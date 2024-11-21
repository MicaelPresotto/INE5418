class Transaction:
    def __init__(self, operations, items, values, transaction_id):
        """
        :param operations: Lista de operações (e.g., ["write", "read", "commit"]).
        :param items: Lista de itens associados às operações (e.g., ["x", "y"]).
        :param values: Lista de valores (apenas para operações de escrita).
        :param transaction_id: ID da transação.
        """
        self.operations = operations
        self.items = items
        self.values = values
        self.id = transaction_id
        self.result = None

    def get_op(self, i):
        """Obtém a operação no índice i."""
        if i < len(self.operations):
            return self.operations[i]
        return None

    def get_item(self, i):
        """Obtém o item associado à operação no índice i."""
        if i < len(self.items):
            return self.items[i]
        return None

    def get_value(self, i):
        """Obtém o valor associado à operação no índice i (somente para 'write')."""
        if i < len(self.values):
            return self.values[i]
        return None
