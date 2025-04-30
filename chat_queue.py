class ChatQueueList:
    def __init__(self, capacity=20, rock_items: list = []):
        self.capacity = capacity
        self.items = []
        self.rock_items = rock_items

    def add(self, item):
        if len(self.items) >= self.capacity:
            self.items.pop(0)
        self.items.append(item)

    def __iter__(self):
        return iter(self.rock_items + self.items)

    def __str__(self):
        return str(self.items)
