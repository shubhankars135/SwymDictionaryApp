"""
An oversimplified implementation of the Python interface for Redis
"""
class Redis:
    def __init__(self, db=0):
        self.db = db
        self.data = {self.db: {}}
        self.size = 0
    def get(self, key):
        """Gets the value associated with a key"""
        return self.data.get(self.db, {}).get(key)
    def set(self, key, value):
        """Sets a key-to-value association"""
        self.data[self.db][key] = value
        self.size += 1
        return True
    def delete(self, key):
        """Deletes a key"""
        del self.data[self.db][key]
        return True
    def avaiable_words(self, list_of_words):
        return set(w for w in list_of_words if w in self.data[self.db])
        