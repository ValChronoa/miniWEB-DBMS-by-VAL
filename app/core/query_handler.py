import json
import csv
import os
from datetime import datetime

class QueryHandler:
    def __init__(self, storage):
        self.storage = storage
        self.commands = {
            "ADD": self._add_item,
            "GET": self._get_items,
            "DELETE": self._delete_item,
            "SEARCH": self._search_items,
            "IMPORT": self._import_csv,
            "EXPORT": self._export_csv
        }
    
    def execute(self, command):
        cmd = command[0].upper()
        if cmd in self.commands:
            return self.commands[cmd](command[1:])
        return f"Error: Unknown command '{cmd}'"
    
    def _add_item(self, args):
        if len(args) < 2:
            return "ADD requires lab and item data"
        
        lab = args[0].lower()
        item_data = args[1]
        
        # Add timestamp
        item_data['last_updated'] = datetime.now().isoformat()
        
        item_id = self.storage.add_item(lab, item_data)
        return f"Item added to {lab} with ID: {item_id}"
    
    def _get_items(self, args):
        if len(args) < 1:
            return "GET requires lab name"
        
        lab = args[0].lower()
        collection = self.storage.get_collection(lab)
        
        if not collection:
            return f"No data found for {lab} lab"
        
        if len(args) == 1:
            # Return summary of all items
            summary = {item_id: item['name'] for item_id, item in collection.items()}
            return json.dumps(summary, indent=2)
        else:
            # Return specific item
            item_id = args[1]
            item = collection.get(item_id)
            return json.dumps(item, indent=2) if item else "Item not found"
    
    def _delete_item(self, args):
        if len(args) < 2:
            return "DELETE requires lab and item ID"
        
        lab = args[0].lower()
        item_id = args[1]
        
        if self.storage.delete_item(lab, item_id):
            return f"Item {item_id} deleted from {lab}"
        return "Item not found"
    
    def _search_items(self, args):
        if len(args) < 3:
            return "SEARCH requires lab, field, and value"
        
        lab = args[0].lower()
        field = args[1]
        value = " ".join(args[2:])
        
        results = self.storage.search_items(lab, field, value)
        return json.dumps(results, indent=2) if results else "No matching items found"
    
    def _import_csv(self, args):
        if len(args) < 2:
            return "IMPORT requires lab and filename"
        
        lab = args[0].lower()
        filename = args[1]
        
        try:
            with open(filename, 'r', newline='') as f:
                reader = csv.DictReader(f)
                count = 0
                
                for row in reader:
                    # Convert empty strings to None
                    item_data = {k: v if v != '' else None for k, v in row.items()}
                    self.storage.add_item(lab, item_data)
                    count += 1
                
                return f"Imported {count} items to {lab} lab"
                
        except FileNotFoundError:
            return f"File not found: {filename}"
        except Exception as e:
            return f"Import error: {str(e)}"
    
    def _export_csv(self, args):
        if len(args) < 2:
            return "EXPORT requires lab and filename"
        
        lab = args[0].lower()
        filename = args[1]
        
        # Ensure exports directory exists
        os.makedirs("exports", exist_ok=True)
        export_path = f"exports/{filename}"
        
        collection = self.storage.get_collection(lab)
        if not collection:
            return f"No data found for {lab} lab"
        
        try:
            with open(export_path, 'w', newline='') as f:
                if collection:
                    # Get field names from first item
                    fieldnames = list(next(iter(collection.values()))).keys()
                    writer = csv.DictWriter(f, fieldnames=['id'] + fieldnames)
                    writer.writeheader()
                    
                    for item_id, item in collection.items():
                        writer.writerow({'id': item_id, **item})
            
            return f"Exported {len(collection)} items to {export_path}"
        
        except Exception as e:
            return f"Export error: {str(e)}"