from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from .models import StorageManager
from config import Config
from datetime import datetime
import os

bp = Blueprint('main', __name__)

def get_storage():
    return StorageManager(Config.DATABASE_PATH)

@bp.route('/')
def index():
    storage = get_storage()
    labs = ["physics", "chemistry", "biology"]
    lab_stats = {}
    
    for lab in labs:
        collection = storage.get_collection(lab)
        lab_stats[lab] = len(collection)
    
    return render_template('index.html', labs=labs, lab_stats=lab_stats)

@bp.route('/lab/<lab_name>')
def lab_inventory(lab_name):
    storage = get_storage()
    collection = storage.get_collection(lab_name)
    
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

@bp.route('/lab/<lab_name>/add', methods=['GET', 'POST'])
def add_item(lab_name):
    storage = get_storage()
    fields = storage.get_lab_fields(lab_name)
    
    if request.method == 'POST':
        item_data = {field: request.form.get(field) for field in fields}
        item_id = storage.add_item(lab_name, item_data)
        flash(f"Item added successfully with ID: {item_id}", "success")
        return redirect(url_for('main.lab_inventory', lab_name=lab_name))
    
    return render_template('add_edit_item.html', lab_name=lab_name, fields=fields, item=None)

@bp.route('/lab/<lab_name>/edit/<item_id>', methods=['GET', 'POST'])
def edit_item(lab_name, item_id):
    storage = get_storage()
    collection = storage.get_collection(lab_name)
    fields = storage.get_lab_fields(lab_name)
    
    if item_id not in collection:
        flash("Item not found", "danger")
        return redirect(url_for('main.lab_inventory', lab_name=lab_name))
    
    if request.method == 'POST':
        updated_data = {field: request.form.get(field) for field in fields}
        collection[item_id] = updated_data
        storage.update_collection(lab_name, collection)
        flash("Item updated successfully", "success")
        return redirect(url_for('main.lab_inventory', lab_name=lab_name))
    
    item = collection[item_id]
    return render_template('add_edit_item.html', lab_name=lab_name, fields=fields, item=item, item_id=item_id)

@bp.route('/lab/<lab_name>/delete/<item_id>')
def delete_item(lab_name, item_id):
    storage = get_storage()
    if storage.delete_item(lab_name, item_id):
        flash("Item deleted successfully", "success")
    else:
        flash("Item not found", "danger")
    return redirect(url_for('main.lab_inventory', lab_name=lab_name))

@bp.route('/lab/<lab_name>/export', methods=['GET', 'POST'])
def export_lab(lab_name):
    storage = get_storage()
    collection = storage.get_collection(lab_name)
    
    if request.method == 'POST':
        format_type = request.form.get('format', 'csv')
        filename = f"{lab_name}_inventory_{datetime.now().strftime('%Y%m%d')}.{format_type}"
        export_path = os.path.join(Config.EXPORTS_DIR, filename)
        
        if not collection:
            flash("No data to export", "warning")
            return redirect(url_for('main.lab_inventory', lab_name=lab_name))
        
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