import csv
import json
import os
from datetime import datetime

class ExportManager:
    @staticmethod
    def to_csv(data, file_path):
        """Export data to CSV file"""
        with open(file_path, 'w', newline='') as f:
            if data:
                # Get all field names
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
                    writer.writerow({'id': item_id, **item})
    
    @staticmethod
    def to_json(data, file_path):
        """Export data to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def export_lab(lab_name, collection, format_type, exports_dir):
        """Export lab data to specified format"""
        if not collection:
            return None, "No data to export"
        
        filename = f"{lab_name}_inventory_{datetime.now().strftime('%Y%m%d')}.{format_type}"
        file_path = os.path.join(exports_dir, filename)
        
        try:
            if format_type == 'csv':
                ExportManager.to_csv(collection, file_path)
            else:  # json
                ExportManager.to_json(collection, file_path)
            
            return file_path, None
        except Exception as e:
            return None, str(e)