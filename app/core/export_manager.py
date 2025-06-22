import csv
import os
import json
from datetime import datetime

class ExportManager:
    @staticmethod
    def to_csv(data, filename, lab_name):
        """Export lab data to CSV file"""
        os.makedirs("exports", exist_ok=True)
        filepath = f"exports/{filename}"
        
        if not data:
            return "No data to export"
        
        try:
            with open(filepath, 'w', newline='') as f:
                # Get all possible field names
                all_fields = set()
                for item in data.values():
                    all_fields.update(item.keys())
                
                # Preserve some order for common fields
                ordered_fields = ['id', 'name', 'quantity', 'last_updated']
                other_fields = sorted(all_fields - set(ordered_fields))
                fieldnames = ordered_fields + other_fields
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for item_id, item in data.items():
                    row = {'id': item_id, **item}
                    writer.writerow(row)
            
            return f"Exported {len(data)} items to {filepath}"
        
        except Exception as e:
            return f"Export error: {str(e)}"
    
    @staticmethod
    def to_json(data, filename, lab_name):
        """Export lab data to JSON file"""
        os.makedirs("exports", exist_ok=True)
        filepath = f"exports/{filename}"
        
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return f"Exported to {filepath}"
        
        except Exception as e:
            return f"Export error: {str(e)}"