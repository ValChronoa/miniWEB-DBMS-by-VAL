from flask import render_template, request, redirect, url_for, flash, send_file
from app.core.storage_manager import StorageManager
from app.core.query_handler import QueryHandler
from app.core.storage_manager import StorageManager
import json
import os
from datetime import datetime

import os
from flask import render_template, request, redirect, url_for, flash, send_file
from app.core.storage_manager import StorageManager
from datetime import datetime

def init_routes(app):
    # Create storage manager with correct path
    storage = StorageManager(os.path.join(app.config['DATA_DIR'], 'database.json'))
    
    # Initialize lab schemas
    init_lab_schemas(storage)
    
    @app.route('/')
    def index():
        labs = ["physics", "chemistry", "biology"]
        lab_stats = {}
        
        for lab in labs:
            collection = storage.get_collection(lab)
            lab_stats[lab] = len(collection) if collection else 0
        
        return render_template('index.html', labs=labs, lab_stats=lab_stats)
    
    @app.route('/lab/<lab_name>')
    def lab_inventory(lab_name):
        collection = storage.get_collection(lab_name)
        if collection is None:
            flash(f"Lab '{lab_name}' not found", "danger")
            return redirect(url_for('index'))
        
        items = []
        for item_id, item in collection.items():
            status = "OK"
            if "expiration_date" in item and item["expiration_date"]:
                try:
                    exp_date = datetime.strptime(item["expiration_date"], "%Y-%m-%d")
                    if exp_date < datetime.now():
                        status = "EXPIRED"
                except ValueError:
                    status = "INVALID DATE"
            
            # For physics equipment
            if lab_name == "physics" and "calibration_due" in item and item["calibration_due"]:
                try:
                    cal_date = datetime.strptime(item["calibration_due"], "%Y-%m-%d")
                    if cal_date < datetime.now():
                        status = "CALIBRATION DUE"
                except ValueError:
                    pass
            
            items.append({
                "id": item_id,
                "name": item.get("name", ""),
                "quantity": item.get("quantity", ""),
                "status": status
            })
        
        return render_template('lab.html', lab_name=lab_name, items=items)
    
    @app.route('/lab/<lab_name>/add', methods=['GET', 'POST'])
    def add_item(lab_name):
        if request.method == 'POST':
            item_data = {field: request.form.get(field) for field in get_lab_fields(lab_name)}
            item_id = storage.add_item(lab_name, item_data)
            flash(f"Item added successfully with ID: {item_id}", "success")
            return redirect(url_for('lab_inventory', lab_name=lab_name))
        
        fields = get_lab_fields(lab_name)
        return render_template('add_edit_item.html', lab_name=lab_name, fields=fields, item=None)
    
    @app.route('/lab/<lab_name>/edit/<item_id>', methods=['GET', 'POST'])
    def edit_item(lab_name, item_id):
        collection = storage.get_collection(lab_name)
        if not collection or item_id not in collection:
            flash("Item not found", "danger")
            return redirect(url_for('lab_inventory', lab_name=lab_name))
        
        if request.method == 'POST':
            updated_data = {field: request.form.get(field) for field in get_lab_fields(lab_name)}
            collection[item_id] = updated_data
            storage.update_collection(lab_name, collection)
            flash("Item updated successfully", "success")
            return redirect(url_for('lab_inventory', lab_name=lab_name))
        
        item = collection[item_id]
        fields = get_lab_fields(lab_name)
        return render_template('add_edit_item.html', lab_name=lab_name, fields=fields, item=item, item_id=item_id)
    
    @app.route('/lab/<lab_name>/delete/<item_id>')
    def delete_item(lab_name, item_id):
        if storage.delete_item(lab_name, item_id):
            flash("Item deleted successfully", "success")
        else:
            flash("Item not found", "danger")
        return redirect(url_for('lab_inventory', lab_name=lab_name))
    
    @app.route('/lab/<lab_name>/export', methods=['GET', 'POST'])
    def export_lab(lab_name):
        if request.method == 'POST':
            format_type = request.form.get('format')
            filename = f"{lab_name}_inventory_{datetime.now().strftime('%Y%m%d')}.{format_type}"
            export_path = os.path.join(app.config['EXPORTS_DIR'], filename)
            
            collection = storage.get_collection(lab_name)
            if not collection:
                flash("No data to export", "warning")
                return redirect(url_for('lab_inventory', lab_name=lab_name))
            
            try:
                if format_type == 'csv':
                    with open(export_path, 'w') as f:
                        f.write("id,name,quantity,status\n")
                        for item_id, item in collection.items():
                            status = "OK"
                            if "expiration_date" in item and item["expiration_date"]:
                                try:
                                    exp_date = datetime.strptime(item["expiration_date"], "%Y-%m-%d")
                                    if exp_date < datetime.now():
                                        status = "EXPIRED"
                                except ValueError:
                                    status = "INVALID DATE"
                            
                            f.write(f"{item_id},{item.get('name','')},{item.get('quantity','')},{status}\n")
                else:  # JSON
                    with open(export_path, 'w') as f:
                        json.dump(collection, f, indent=2)
                
                return send_file(export_path, as_attachment=True)
            except Exception as e:
                flash(f"Export failed: {str(e)}", "danger")
        
        return render_template('export.html', lab_name=lab_name)

def get_lab_fields(lab_name):
    fields = {
        "chemistry": [
            "name", "quantity", "supplier_name", "supplier_address", 
            "supplier_phone", "cas_number", "signal_word", "hazards", 
            "pictogram", "precautionary_statements", "supplemental_info",
            "distributor_name", "distributor_phone", "date_purchased",
            "date_opened", "expiration_date"
        ],
        "biology": [
            "name", "quantity", "storage_conditions", "biohazard_level", 
            "supplier_name", "supplier_contact", "catalog_number", 
            "expiration_date", "date_received", "date_opened", 
            "last_used", "used_by", "disposal_method", "notes"
        ],
        "physics": [
            "name", "quantity", "manufacturer", "model_number", 
            "serial_number", "location", "calibration_due", 
            "last_calibration", "condition", "current_user", 
            "usage_log", "notes"
        ]
    }
    return fields.get(lab_name, [])

def init_lab_schemas(storage):
    labs = ["physics", "chemistry", "biology"]
    for lab in labs:
        if not storage.get_collection(lab):
            storage.update_collection(lab, {})