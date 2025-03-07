import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import json
import difflib

# Function to load JSON data from a file
def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-16-le') as file:
            return json.load(file)
    except FileNotFoundError:
        messagebox.showerror("Error", f"File '{file_path}' not found.")
        return None
    except json.JSONDecodeError:
        messagebox.showerror("Error", f"File '{file_path}' is not a valid JSON file.")
        return None

# Function to extract regular column names from a table
def get_regular_columns(table):
    return {
        column['name'] for column in table.get('columns', [])
        if column.get('type') != 'calculated'
    }

# Function to extract calculated columns from a table
def get_calculated_columns(table):
    return {
        column['name']: column for column in table.get('columns', [])
        if column.get('type') == 'calculated'
    }

# Function to extract measures from a table
def get_measures(table):
    return {measure['name']: measure for measure in table.get('measures', [])}

# Function to extract relationships from the model
def get_relationships(model):
    return {
        (relationship['fromTable'], relationship['fromColumn'], relationship['toTable'], relationship['toColumn']): relationship
        for relationship in model.get('relationships', [])
    }

# Function to compare regular columns between two tables
def compare_regular_columns(table1, table2, table_name, result_text):
    columns1 = get_regular_columns(table1)
    columns2 = get_regular_columns(table2)

    # Find added columns (in table2 but not in table1)
    added_columns = columns2 - columns1
    # Find deleted columns (in table1 but not in table2)
    deleted_columns = columns1 - columns2

    # Display results only if there are changes
    if added_columns or deleted_columns:
        result_text.insert(tk.END, f"Table: {table_name}\n")
        if added_columns:
            result_text.insert(tk.END, f"  Added Regular Columns: {', '.join(added_columns)}\n")
        if deleted_columns:
            result_text.insert(tk.END, f"  Deleted Regular Columns: {', '.join(deleted_columns)}\n")

# Function to compare calculated columns between two tables
def compare_calculated_columns(table1, table2, table_name, result_text):
    calculated1 = get_calculated_columns(table1)
    calculated2 = get_calculated_columns(table2)

    # Find added calculated columns (in table2 but not in table1)
    added_calculated = set(calculated2.keys()) - set(calculated1.keys())
    # Find deleted calculated columns (in table1 but not in table2)
    deleted_calculated = set(calculated1.keys()) - set(calculated2.keys())
    # Find calculated columns with changed expressions
    changed_calculated = {
        name for name in calculated1.keys() & calculated2.keys()
        if (
            calculated1[name].get('expression') != calculated2[name].get('expression') or
            'expression' not in calculated1[name] or
            'expression' not in calculated2[name]
        )
    }

    # Filter out calculated columns without expressions (unless they are added or changed)
    calculated1 = {name: column for name, column in calculated1.items() if 'expression' in column or name in changed_calculated or name in deleted_calculated}
    calculated2 = {name: column for name, column in calculated2.items() if 'expression' in column or name in changed_calculated or name in added_calculated}

    # Display results only if there are changes
    if added_calculated or deleted_calculated or changed_calculated:
        result_text.insert(tk.END, f"Table: {table_name}\n")
        
        # Added Calculated Columns
        if added_calculated:
            result_text.insert(tk.END, f"  Added Calculated Columns: {', '.join(added_calculated)}\n")
        
        # Deleted Calculated Columns
        if deleted_calculated:
            result_text.insert(tk.END, f"  Deleted Calculated Columns: {', '.join(deleted_calculated)}\n")
        
        # Changed Calculated Columns
        if changed_calculated:
            result_text.insert(tk.END, f"  Changed Calculated Columns:\n")
            for name in changed_calculated:
                old_expr = calculated1[name].get('expression', ['N/A'])
                new_expr = calculated2[name].get('expression', ['N/A'])
                
                # Ensure expressions are lists
                old_expr = old_expr if isinstance(old_expr, list) else [old_expr]
                new_expr = new_expr if isinstance(new_expr, list) else [new_expr]
                
                # Use difflib to find the differences
                diff = difflib.unified_diff(old_expr, new_expr, lineterm='')
                changes = [line for line in diff if line.startswith('-') or line.startswith('+')]
                
                # Filter out blank lines and markers
                changes = [line for line in changes if line.strip() and not line.startswith('---') and not line.startswith('+++')]
                
                # Only display if there are changes
                if changes:
                    result_text.insert(tk.END, f"    {name}:\n")
                    result_text.insert(tk.END, "      Changes:\n")
                    for change in changes:
                        result_text.insert(tk.END, f"        {change}\n")

# Function to compare measures between two tables
def compare_measures(table1, table2, table_name, result_text):
    measures1 = get_measures(table1)
    measures2 = get_measures(table2)

    # Find added measures (in table2 but not in table1)
    added_measures = set(measures2.keys()) - set(measures1.keys())
    # Find deleted measures (in table1 but not in table2)
    deleted_measures = set(measures1.keys()) - set(measures2.keys())
    # Find measures with changed expressions
    changed_measures = {
        name for name in measures1.keys() & measures2.keys()
        if (
            measures1[name].get('expression') != measures2[name].get('expression') or
            'expression' not in measures1[name] or
            'expression' not in measures2[name]
        )
    }

    # Filter out measures without expressions (unless they are added or changed)
    measures1 = {name: measure for name, measure in measures1.items() if 'expression' in measure or name in changed_measures or name in deleted_measures}
    measures2 = {name: measure for name, measure in measures2.items() if 'expression' in measure or name in changed_measures or name in added_measures}

    # Display results only if there are changes
    if added_measures or deleted_measures or changed_measures:
        result_text.insert(tk.END, f"Table: {table_name}\n")
        
        # Added Measures
        if added_measures:
            result_text.insert(tk.END, f"  Added Measures: {', '.join(added_measures)}\n")
        
        # Deleted Measures
        if deleted_measures:
            result_text.insert(tk.END, f"  Deleted Measures: {', '.join(deleted_measures)}\n")
        
        # Changed Measures
        if changed_measures:
            result_text.insert(tk.END, f"  Changed Measures:\n")
            for name in changed_measures:
                old_expr = measures1[name].get('expression', ['N/A'])
                new_expr = measures2[name].get('expression', ['N/A'])
                
                # Ensure expressions are lists
                old_expr = old_expr if isinstance(old_expr, list) else [old_expr]
                new_expr = new_expr if isinstance(new_expr, list) else [new_expr]
                
                # Use difflib to find the differences
                diff = difflib.unified_diff(old_expr, new_expr, lineterm='')
                changes = [line for line in diff if line.startswith('-') or line.startswith('+')]
                
                # Filter out blank lines and markers
                changes = [line for line in changes if line.strip() and not line.startswith('---') and not line.startswith('+++')]
                
                # Only display if there are changes
                if changes:
                    result_text.insert(tk.END, f"    {name}:\n")
                    result_text.insert(tk.END, "      Changes:\n")
                    for change in changes:
                        result_text.insert(tk.END, f"        {change}\n")

# Function to compare relationships between two models
# Function to compare relationships between two models
def compare_relationships(model1, model2, result_text):
    relationships1 = get_relationships(model1)
    relationships2 = get_relationships(model2)

    # Find added relationships (in model2 but not in model1)
    added_relationships = set(relationships2.keys()) - set(relationships1.keys())
    # Find deleted relationships (in model1 but not in model2)
    deleted_relationships = set(relationships1.keys()) - set(relationships2.keys())
    # Find changed relationships
    changed_relationships = {
        key for key in relationships1.keys() & relationships2.keys()
        if relationships1[key] != relationships2[key]
    }

    # Display results only if there are changes
    if added_relationships or deleted_relationships or changed_relationships:
        result_text.insert(tk.END, "Relationships:\n")
        
        # Added Relationships
        if added_relationships:
            result_text.insert(tk.END, f"  Added Relationships:\n")
            for key in added_relationships:
                rel = relationships2[key]
                result_text.insert(tk.END, f"    {rel['fromTable']}({rel['fromColumn']}) -> {rel['toTable']}({rel['toColumn']})\n")
                # Do not show isActive flag for added relationships
        
        # Deleted Relationships
        if deleted_relationships:
            result_text.insert(tk.END, f"  Deleted Relationships:\n")
            for key in deleted_relationships:
                rel = relationships1[key]
                result_text.insert(tk.END, f"    {rel['fromTable']}({rel['fromColumn']}) -> {rel['toTable']}({rel['toColumn']})\n")
                # Do not show isActive flag for deleted relationships
        
        # Changed Relationships
        if changed_relationships:
            result_text.insert(tk.END, f"  Changed Relationships:\n")
            for key in changed_relationships:
                old_rel = relationships1[key]
                new_rel = relationships2[key]
                result_text.insert(tk.END, f"    {old_rel['fromTable']}({old_rel['fromColumn']}) -> {old_rel['toTable']}({old_rel['toColumn']})\n")
                
                # Check for changes in isActive flag
                old_active = old_rel.get('isActive', True)  # Default to True if flag is missing
                new_active = new_rel.get('isActive', True)  # Default to True if flag is missing
                
                # Only show isActive if it has changed
                if old_active != new_active:
                    if new_active:
                        result_text.insert(tk.END, f"      Relationship is now Active\n")
                    else:
                        result_text.insert(tk.END, f"      Relationship is now Inactive\n")

# Function to compare the two JSON files
def compare_files(file1, file2, result_text):
    # Load JSON data from both files
    data1 = load_json(file1)
    data2 = load_json(file2)

    # Check if files were loaded successfully
    if data1 is None or data2 is None:
        return

    # Check if 'model' key exists in both files
    if 'model' not in data1 or 'model' not in data2:
        messagebox.showerror("Error", "'model' key is missing in one or both files.")
        return

    # Get tables from both files
    tables1 = {table['name']: table for table in data1['model'].get('tables', [])}
    tables2 = {table['name']: table for table in data2['model'].get('tables', [])}

    # Compare regular columns, calculated columns, and measures for each table
    for table_name, table1 in tables1.items():
        if table_name in tables2:
            table2 = tables2[table_name]
            compare_regular_columns(table1, table2, table_name, result_text)
            compare_calculated_columns(table1, table2, table_name, result_text)
            compare_measures(table1, table2, table_name, result_text)
        else:
            result_text.insert(tk.END, f"Table: {table_name} - Removed in the second file.\n")

    # Check for new tables in the second file
    for table_name, table2 in tables2.items():
        if table_name not in tables1:
            result_text.insert(tk.END, f"Table: {table_name} - Added in the second file.\n")

    # Compare relationships
    compare_relationships(data1['model'], data2['model'], result_text)

# Function to open file dialog and set file path
def select_file(entry_widget):
    file_path = filedialog.askopenfilename(filetypes=[])  # Show all files
    if file_path:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, file_path)

# Main GUI application
class JSONComparatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON Comparator")

        # Configure grid weights for resizing
        self.root.grid_rowconfigure(3, weight=1)  # Make the result text box row expand
        self.root.grid_columnconfigure(1, weight=1)  # Make the entry columns expand

        # File 1 selection
        self.label_file1 = tk.Label(root, text="File 1:")
        self.label_file1.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_file1 = tk.Entry(root, width=50)
        self.entry_file1.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.button_file1 = tk.Button(root, text="Browse", command=lambda: select_file(self.entry_file1))
        self.button_file1.grid(row=0, column=2, padx=5, pady=5, sticky="e")

        # File 2 selection
        self.label_file2 = tk.Label(root, text="File 2:")
        self.label_file2.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_file2 = tk.Entry(root, width=50)
        self.entry_file2.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.button_file2 = tk.Button(root, text="Browse", command=lambda: select_file(self.entry_file2))
        self.button_file2.grid(row=1, column=2, padx=5, pady=5, sticky="e")

        # Compare button
        self.button_compare = tk.Button(root, text="Compare", command=self.run_comparison)
        self.button_compare.grid(row=2, column=1, padx=5, pady=5)

        # Result display
        self.result_text = scrolledtext.ScrolledText(root, width=80, height=20)
        self.result_text.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

    def run_comparison(self):
        file1 = self.entry_file1.get()
        file2 = self.entry_file2.get()

        if not file1 or not file2:
            messagebox.showerror("Error", "Please select both files.")
            return

        # Clear previous results
        self.result_text.delete(1.0, tk.END)

        # Run the comparison
        compare_files(file1, file2, self.result_text)

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = JSONComparatorApp(root)
    root.mainloop()