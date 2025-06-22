import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pathlib import Path
from datetime import datetime

class UIManager:
    THEMES = {
        "light": {
            "bg": "#F0F0F0", "fg": "#222222", "accent": "#4A90E2",
            "btn_bg": "#E1E1E1", "btn_fg": "#000000",
            "font": ("Segoe UI", 10)
        },
        "dark": {
            "bg": "#2D2D30", "fg": "#E1E1E1", "accent": "#007ACC",
            "btn_bg": "#3F3F46", "btn_fg": "#FFFFFF",
            "font": ("Segoe UI", 10)
        },
        "blue": {
            "bg": "#E6F4FF", "fg": "#00334D", "accent": "#0078D7",
            "btn_bg": "#B8DAFF", "btn_fg": "#002240",
            "font": ("Segoe UI", 10)
        }
    }
    
    def __init__(self, config_path='settings/ui_config.json'):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.storage = None
        self.root = None
        self.notebook = None
        self.tabs = {}
        self.trees = {}
        self.labs = ["physics", "chemistry", "biology"]
        
    def _load_config(self):
        """Load or create UI configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
        except:
            pass
        
        # Create default config
        default_config = {
            "theme": "light",
            "font_size": 10,
            "recent_files": [],
            "window_size": "800x600"
        }
        
        os.makedirs(self.config_path.parent, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
            
        return default_config
    
    def save_config(self):
        """Save UI configuration"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def apply_theme(self, window):
        """Apply selected theme to a window"""
        theme_name = self.config.get("theme", "light")
        theme = self.THEMES.get(theme_name, self.THEMES["light"])
        
        # Apply to window
        window.configure(bg=theme['bg'])
        
        # Apply style to all widgets
        style = ttk.Style()
        style.configure('TFrame', background=theme['bg'])
        style.configure('TLabel', background=theme['bg'], foreground=theme['fg'])
        style.configure('TButton', 
                        background=theme['btn_bg'], 
                        foreground=theme['btn_fg'],
                        font=theme['font'])
        style.configure('Treeview', 
                        background="#FFFFFF", 
                        fieldbackground="#FFFFFF",
                        font=theme['font'])
        style.configure('Treeview.Heading', font=theme['font'])
        style.map('Treeview', background=[('selected', theme['accent'])])
    
    def launch_ui(self, storage):
        """Launch the graphical user interface"""
        self.storage = storage
        self.root = tk.Tk()
        self.root.title("Laboratory Inventory Management System")
        self.root.geometry(self.config.get("window_size", "800x600"))
        
        # Apply theme
        self.apply_theme(self.root)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main layout
        self.create_main_layout()
        
        # Bind window resize event
        self.root.bind("<Configure>", self.on_window_resize)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()
    
    def create_menu_bar(self):
        """Create the menu bar"""
        menu_bar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Refresh Data", command=self.refresh_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # View menu
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="Light Theme", command=lambda: self.change_theme("light"))
        view_menu.add_command(label="Dark Theme", command=lambda: self.change_theme("dark"))
        view_menu.add_command(label="Blue Theme", command=lambda: self.change_theme("blue"))
        menu_bar.add_cascade(label="View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menu_bar)
    
    def create_main_layout(self):
        """Create the main UI layout"""
        # Create notebook for labs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs for each lab
        self.tabs = {}
        self.trees = {}
        
        for lab in self.labs:
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=lab.capitalize())
            self.tabs[lab] = tab
            self.create_lab_tab(tab, lab)
    
    def create_lab_tab(self, parent, lab):
        """Create UI components for a specific lab"""
        # Create treeview for inventory
        columns = ("id", "name", "quantity", "status")
        tree = ttk.Treeview(parent, columns=columns, show='headings', selectmode='browse')
        
        # Set column headings
        tree.heading("id", text="ID")
        tree.heading("name", text="Name")
        tree.heading("quantity", text="Quantity")
        tree.heading("status", text="Status")
        
        # Set column widths
        tree.column("id", width=80)
        tree.column("name", width=200)
        tree.column("quantity", width=100)
        tree.column("status", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        scrollbar.pack(side='right', fill='y')
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Store tree reference
        self.trees[lab] = tree
        
        # Load data
        self.load_lab_data(lab)
        
        # Create button frame
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        # Add buttons with proper command binding
        ttk.Button(button_frame, text="Add Item", 
                  command=lambda lab=lab: self.add_item_dialog(lab)).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Edit Item", 
                  command=lambda lab=lab: self.edit_item_dialog(lab)).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Item", 
                  command=lambda lab=lab: self.delete_item_dialog(lab)).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Refresh", 
                  command=lambda lab=lab: self.load_lab_data(lab)).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Export CSV", 
                  command=lambda lab=lab: self.export_csv_dialog(lab)).pack(side='right', padx=5)
    
    def load_lab_data(self, lab):
        """Load data for a specific lab into its treeview"""
        tree = self.trees[lab]
        
        # Clear existing data
        for item in tree.get_children():
            tree.delete(item)
        
        # Load new data
        collection = self.storage.get_collection(lab)
        if collection:
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
                if lab == "physics" and "calibration_due" in item and item["calibration_due"]:
                    try:
                        cal_date = datetime.strptime(item["calibration_due"], "%Y-%m-%d")
                        if cal_date < datetime.now():
                            status = "CALIBRATION DUE"
                    except ValueError:
                        pass
                
                tree.insert("", "end", iid=item_id, values=(
                    item_id, 
                    item.get("name", ""),
                    item.get("quantity", ""),
                    status
                ))
    
    def add_item_dialog(self, lab):
        """Show dialog to add new item"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Add Item to {lab.capitalize()} Lab")
        dialog.geometry("500x400")
        self.apply_theme(dialog)
        
        # Create form fields based on lab type
        fields = self.get_lab_fields(lab)
        entries = {}
        
        # Create scrollable frame
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add form fields
        for i, field in enumerate(fields):
            label = ttk.Label(scrollable_frame, text=field.replace("_", " ").title() + ":")
            label.grid(row=i, column=0, padx=10, pady=5, sticky="e")
            
            entry = ttk.Entry(scrollable_frame, width=30)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
            entries[field] = entry
        
        # Add button to submit
        def submit():
            item_data = {field: entry.get() for field, entry in entries.items()}
            item_id = self.storage.add_item(lab, item_data)
            
            # Refresh the treeview
            self.load_lab_data(lab)
            
            dialog.destroy()
            messagebox.showinfo("Success", f"Item added with ID: {item_id}")
        
        ttk.Button(scrollable_frame, text="Add Item", command=submit).grid(
            row=len(fields), column=0, columnspan=2, pady=10)
    
    def edit_item_dialog(self, lab):
        """Show dialog to edit existing item"""
        tree = self.trees[lab]
        selected = tree.selection()
        
        if not selected:
            messagebox.showwarning("No Selection", "Please select an item to edit")
            return
        
        item_id = selected[0]
        collection = self.storage.get_collection(lab)
        item_data = collection.get(item_id)
        
        if not item_data:
            messagebox.showerror("Error", "Selected item not found in database")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Item in {lab.capitalize()} Lab")
        dialog.geometry("500x400")
        self.apply_theme(dialog)
        
        # Create form fields based on lab type
        fields = self.get_lab_fields(lab)
        entries = {}
        
        # Create scrollable frame
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add form fields with existing data
        for i, field in enumerate(fields):
            label = ttk.Label(scrollable_frame, text=field.replace("_", " ").title() + ":")
            label.grid(row=i, column=0, padx=10, pady=5, sticky="e")
            
            entry = ttk.Entry(scrollable_frame, width=30)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
            
            # Pre-fill with existing data
            if field in item_data:
                entry.insert(0, item_data[field])
            
            entries[field] = entry
        
        # Add button to submit
        def submit():
            updated_data = {field: entry.get() for field, entry in entries.items()}
            
            # Update the item in storage
            collection = self.storage.get_collection(lab)
            if item_id in collection:
                collection[item_id] = updated_data
                self.storage.update_collection(lab, collection)
                
                # Refresh the treeview
                self.load_lab_data(lab)
                
                dialog.destroy()
                messagebox.showinfo("Success", "Item updated successfully")
            else:
                messagebox.showerror("Error", "Item not found in database")
        
        ttk.Button(scrollable_frame, text="Save Changes", command=submit).grid(
            row=len(fields), column=0, columnspan=2, pady=10)
    
    def delete_item_dialog(self, lab):
        """Confirm and delete selected item"""
        tree = self.trees[lab]
        selected = tree.selection()
        
        if not selected:
            messagebox.showwarning("No Selection", "Please select an item to delete")
            return
        
        item_id = selected[0]
        item_name = tree.item(item_id, "values")[1]
        
        # Confirm deletion
        response = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete '{item_name}' (ID: {item_id})?",
            icon='warning'
        )
        
        if response:
            # Delete from storage
            if self.storage.delete_item(lab, item_id):
                # Remove from treeview
                tree.delete(item_id)
                messagebox.showinfo("Success", "Item deleted successfully")
            else:
                messagebox.showerror("Error", "Failed to delete item from database")
    
    def get_lab_fields(self, lab):
        """Get field names for a specific lab"""
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
        return fields.get(lab, [])
    
    def export_csv_dialog(self, lab):
        """Show dialog to export CSV"""
        filename = simpledialog.askstring(
            "Export Data", 
            f"Enter filename for {lab} export:",
            initialvalue=f"{lab}_inventory_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        
        if filename:
            if not filename.endswith(".csv"):
                filename += ".csv"
            
            collection = self.storage.get_collection(lab)
            if collection:
                # Simple export implementation
                try:
                    os.makedirs("exports", exist_ok=True)
                    export_path = f"exports/{filename}"
                    
                    with open(export_path, 'w', encoding='utf-8') as f:
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
                    
                    messagebox.showinfo("Export Successful", f"Data exported to {export_path}")
                except Exception as e:
                    messagebox.showerror("Export Failed", f"Error: {str(e)}")
            else:
                messagebox.showwarning("No Data", f"No data found for {lab} lab")
    
    def refresh_data(self):
        """Refresh all lab data"""
        if self.notebook:
            current_tab = self.notebook.tab(self.notebook.select(), "text").lower()
            for lab in self.labs:
                self.load_lab_data(lab)
            
            # Return to the originally selected tab
            self.notebook.select(self.tabs[current_tab])
            messagebox.showinfo("Refreshed", "All data has been refreshed")
    
    def change_theme(self, theme_name):
        """Change the application theme"""
        self.config["theme"] = theme_name
        self.save_config()
        
        # Recreate the UI with new theme
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.create_menu_bar()
        self.create_main_layout()
        messagebox.showinfo("Theme Changed", f"Switched to {theme_name} theme")
    
    def show_about(self):
        """Show about dialog"""
        about_text = (
            "Laboratory Inventory Management System (LIMS)\n"
            "Version 1.0\n\n"
            "Developed for Physics, Chemistry, and Biology Labs\n"
            "© 2023 School Laboratory Department"
        )
        messagebox.showinfo("About LIMS", about_text)
    
    def on_window_resize(self, event):
        """Save window size when resized"""
        if event.widget == self.root:
            self.config["window_size"] = f"{self.root.winfo_width()}x{self.root.winfo_height()}"
            self.save_config()
    
    def on_close(self):
        """Handle window close event"""
        self.save_config()
        self.root.destroy()