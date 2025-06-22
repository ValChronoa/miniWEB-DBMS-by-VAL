import json
import os
from pathlib import Path
import uuid
import threading

class StorageManager:
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.lock = threading.Lock()
        self._ensure_structure()
    
    def _ensure_structure(self):
        """Create data directory and empty database if needed"""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.write_text('{}')
    
    def read_data(self):
        """Read entire database atomically"""
        with self.lock:
            with open(self.file_path, 'r') as f:
                return json.load(f)
    
    def write_data(self, data):
        """Write entire database atomically"""
        with self.lock:
            # Write to temporary file first
            temp_path = self.file_path.with_suffix('.tmp')
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Replace original file
            os.replace(temp_path, self.file_path)
    
    def get_collection(self, collection_name):
        """Get a specific collection or None if not exists"""
        data = self.read_data()
        return data.get(collection_name)
    
    def update_collection(self, collection_name, collection_data):
        """Update a specific collection"""
        data = self.read_data()
        data[collection_name] = collection_data
        self.write_data(data)
    
    def add_item(self, collection_name, item_data):
        """Add a new item to a collection with unique ID"""
        data = self.read_data()
        
        # Create collection if doesn't exist
        if collection_name not in data:
            data[collection_name] = {}
        
        # Generate unique ID
        item_id = str(uuid.uuid4())[:8]
        data[collection_name][item_id] = item_data
        self.write_data(data)
        return item_id
    
    def delete_item(self, collection_name, item_id):
        """Delete an item from a collection"""
        data = self.read_data()
        if collection_name in data and item_id in data[collection_name]:
            del data[collection_name][item_id]
            self.write_data(data)
            return True
        return False
    
    def search_items(self, collection_name, field, value):
        """Search items in a collection by field value"""
        data = self.read_data()
        collection = data.get(collection_name, {})
        results = {}
        
        for item_id, item in collection.items():
            if field in item and str(item[field]).lower() == str(value).lower():
                results[item_id] = item
        
        return results