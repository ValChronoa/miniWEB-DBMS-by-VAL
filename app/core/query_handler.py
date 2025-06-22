class QueryHandler:
    def __init__(self, storage):
        self.storage = storage
    
    def add_item(self, lab, item_data):
        """Add a new item to the specified lab"""
        return self.storage.add_item(lab, item_data)
    
    def get_collection(self, lab):
        """Get all items in a lab collection"""
        return self.storage.get_collection(lab)
    
    def delete_item(self, lab, item_id):
        """Delete an item from a lab collection"""
        return self.storage.delete_item(lab, item_id)
    
    def search_items(self, lab, field, value):
        """Search items in a lab collection"""
        return self.storage.search_items(lab, field, value)