import tkinter as tk
from tkinter import ttk
from editor_screen import show_editor_screen

class ExperimentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Emotional Visual Search Experiment Launcher")
        self.root.geometry("1200x800")
        self.root.minsize(600, 400)
        self.root.configure(bg="#f0f0f0")  # Light, neutral background

        # Configure ttk styles
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Main button style
        self.style.configure("TButton", font=("Segoe UI", 14), padding=10)
        # Small button style for the remove metadata button and list item removal
        self.style.configure("Small.TButton", font=("Segoe UI", 10), padding=(2, 2))

        # Global style for Labels and Entry fields
        self.style.configure("TLabel", font=("Segoe UI", 20, "bold"), background="#f0f0f0")
        self.style.configure("TEntry", font=("Segoe UI", 16))  # Increased font size
        
        # Custom smaller style for the "Add Item" button
        self.style.configure("AddItem.TButton", font=("Segoe UI", 8), padding=(1, 1))

        # Stored values for persistence
        self.saved_exp_name = ""
        self.saved_participant_name = ""
        self.saved_metadata = [] 

        # List to store metadata rows (each row is represented as a dictionary of widget references)
        self.metadata_entries = []

        self.show_main_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_main_screen(self):
        self.clear_screen()
        
        # Header Frame for title and buttons
        header_frame = tk.Frame(self.root, bg="#f0f0f0")
        header_frame.pack(expand=True, pady=50)
        
        title_label = ttk.Label(header_frame, text="Visual Search Experiment Launcher", anchor="center")
        title_label.pack(pady=(0, 30))
        
        button_frame = tk.Frame(header_frame, bg="#f0f0f0")
        button_frame.pack()
        
        create_button = ttk.Button(button_frame, text="Create Experiment", command=self.show_create_screen)
        create_button.grid(row=0, column=0, padx=20, pady=20)
        
        launch_button = ttk.Button(button_frame, text="Launch Experiment")
        launch_button.grid(row=0, column=1, padx=20, pady=20)

    def show_create_screen(self):
        self.clear_screen()
        self.metadata_entries = []  # Reset metadata entries

        # Main container for the create screen
        main_frame = tk.Frame(self.root, bg="#f0f0f0", padx=40, pady=40)
        main_frame.pack(expand=True, fill="both")
        
        header_label = ttk.Label(main_frame, text="Create New Experiment", font=("Segoe UI", 24, "bold"))
        header_label.pack(pady=(0, 30))
        
        self.error_label = ttk.Label(main_frame, text="", foreground="red", font=("Segoe UI", 12))
        self.error_label.pack(pady=(0, 10))
        
        # Form container for Experiment Name and Participant Default Name fields
        form_frame = tk.Frame(main_frame, bg="#f0f0f0")
        form_frame.pack(pady=10)
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)
        
        exp_label = ttk.Label(form_frame, text="Experiment Name:", font=("Segoe UI", 18, "bold"), background="#f0f0f0")
        exp_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.exp_name_entry = ttk.Entry(form_frame, width=50)
        self.exp_name_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.exp_name_entry.insert(0, self.saved_exp_name)
        
        part_label = ttk.Label(form_frame, text="Participant Default Name:", font=("Segoe UI", 18, "bold"), background="#f0f0f0")
        part_label.grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.participant_entry = ttk.Entry(form_frame, width=50)
        self.participant_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.participant_entry.insert(0, self.saved_participant_name)
        
        # Metadata section container to hold metadata rows
        metadata_container = tk.Frame(main_frame, bg="#f0f0f0")
        metadata_container.pack(pady=10, padx=20, fill="x")
        
        metadata_label = ttk.Label(metadata_container, text="Metadata:", font=("Segoe UI", 24, "bold"),
                                   background="#f0f0f0", anchor="center")
        metadata_label.pack(pady=(0,5), anchor="center")
        
        # Container frame for metadata entries (with a set width, made narrower)
        self.metadata_frame = tk.Frame(metadata_container, bg="#ffffff", bd=2, relief="groove",
                                       padx=10, pady=10, width=500)
        self.metadata_frame.pack(anchor="center", fill="x")
        
        # Add an initial metadata row
        self.add_metadata_row()

        # Button to add more metadata rows
        add_button = ttk.Button(main_frame, text="+ Add Metadata", command=self.add_metadata_row)
        add_button.pack(pady=10)
        
        # Action buttons at the bottom (Back and Create)
        action_frame = tk.Frame(main_frame, bg="#f0f0f0")
        action_frame.pack(pady=20)
        
        back_button = ttk.Button(action_frame, text="Back", command=self.show_main_screen)
        back_button.grid(row=0, column=0, padx=20)
        create_button = ttk.Button(action_frame, text="Create", command=self.validate_and_proceed)
        create_button.grid(row=0, column=1, padx=20)

    def add_metadata_row(self, initial_data=None):
        """
        Adds a metadata row that allows entering a metadata name and choosing whether its value is a
        single entry or a list of items.
        """
        row_frame = tk.Frame(self.metadata_frame, bg="#ffffff")
        row_frame.pack(fill="x", pady=5)

        # Metadata name entry field
        name_entry = ttk.Entry(row_frame, width=20)
        name_entry.pack(side="left", padx=5)
        if initial_data and "name" in initial_data:
            name_entry.insert(0, initial_data["name"])

        # Combobox to select type: "Value" or "List"
        type_var = tk.StringVar(value="Value")
        type_combobox = ttk.Combobox(
            row_frame,
            textvariable=type_var,
            values=["Value", "List"],
            state="readonly",
            width=6
        )
        type_combobox.pack(side="left", padx=5)

        # Content frame that will hold either a single value entry or list items
        content_frame = tk.Frame(row_frame, bg="#ffffff")
        content_frame.pack(side="left", padx=5, fill="x", expand=True)

        # When metadata type is "List", create list input controls.
        # Otherwise (for "Value"), create a single value entry widget.
        if initial_data and initial_data.get("type", "Value") == "List":
            type_var.set("List")
            list_container = tk.Frame(content_frame, bg="#ffffff")
            list_container.pack(fill="x")
            list_entries = []
            for item in initial_data.get("value", []):
                entry = self._create_list_item(list_container, initial_text=item)
                list_entries.append(entry)
            if not list_entries:
                entry = self._create_list_item(list_container)
                list_entries.append(entry)
            add_item_button = ttk.Button(
                content_frame,
                text="+ Add Item",
                style="AddItem.TButton",  # Use the custom smaller style
                command=lambda: self._add_list_item(list_container, list_entries)
            )
            add_item_button.pack(pady=5)
            row_data = {
                "frame": row_frame,
                "name_entry": name_entry,
                "type_combobox": type_combobox,
                "content_frame": content_frame,
                "list_container": list_container,
                "list_entries": list_entries,
                "value_entry": None  # No separate value entry in List mode
            }
        else:
            # For "Value" mode, create a white rectangle placeholder.
            type_var.set("Value")
            placeholder = tk.Frame(content_frame, bg="white", width=200, height=30)  # adjust size as desired
            placeholder.pack(side="left", padx=5, pady=5)
            placeholder.pack_propagate(False)  # Prevent it from resizing to its contents
            
            # Instead of a value entry, store the placeholder.
            row_data = {
                "frame": row_frame,
                "name_entry": name_entry,
                "type_combobox": type_combobox,
                "content_frame": content_frame,
                "list_container": None,
                "list_entries": [],
                "value_entry": None,   # No entry widget since it is just a placeholder.
                "value_placeholder": placeholder
            }
        # Remove metadata button for this row
        remove_btn = ttk.Button(row_frame, text="Remove", command=lambda: self.remove_metadata_row(row_frame),
                                  style="Small.TButton")
        remove_btn.pack(side="left", padx=5)

        # Bind a callback when the type is changed to update the content frame accordingly.
        type_combobox.bind("<<ComboboxSelected>>", lambda event, d=row_data: self._on_type_change(d))

        self.metadata_entries.append(row_data)

    def _create_list_item(self, container, initial_text=""):
        """
        Creates a single list item entry within a metadata row (for list-type metadata).
        """
        row = tk.Frame(container, bg="#ffffff")
        row.pack(fill="x", pady=2)
        entry = ttk.Entry(row, width=35)
        entry.pack(side="left", padx=5)
        entry.insert(0, initial_text)
        remove_btn = ttk.Button(row, text="Remove", style="Small.TButton", command=row.destroy)
        remove_btn.pack(side="left", padx=5)
        return entry

    def _add_list_item(self, container, list_entries):
        """
        Adds an additional list item entry to the list container.
        """
        entry = self._create_list_item(container)
        list_entries.append(entry)

    def _on_type_change(self, row_data):
        """
        Callback when the metadata type is changed between "Value" and "List".
        This method clears the current content and recreates the appropriate widget(s).
        """
        type_val = row_data["type_combobox"].get()
        # Clear any children from the content frame.
        for widget in row_data["content_frame"].winfo_children():
            widget.destroy()

        if type_val == "Value":
            # First, clear any existing widgets from the content frame.
            for widget in row_data["content_frame"].winfo_children():
                widget.destroy()

            # Create a white rectangle placeholder.
            placeholder = tk.Frame(row_data["content_frame"], bg="white", width=200, height=30)  # adjust size as needed
            placeholder.pack(side="left", padx=5, pady=5)
            # Prevent the placeholder frame from shrinking to fit its contents.
            placeholder.pack_propagate(False)
            
            # Store the placeholder widget for later reference, if needed.
            row_data["value_placeholder"] = placeholder

            # Optionally reset list-related data.
            row_data["list_container"] = None
            row_data["list_entries"] = []

        elif type_val == "List":
            list_container = tk.Frame(row_data["content_frame"], bg="#ffffff")
            list_container.pack(fill="x")
            list_entries = []
            # Create an initial list item entry
            entry = self._create_list_item(list_container)
            list_entries.append(entry)
            # Use the custom style for the add item button here as well
            add_item_button = ttk.Button(
                row_data["content_frame"],
                text="+ Add Item",
                style="AddItem.TButton",
                command=lambda: self._add_list_item(list_container, list_entries)
            )
            add_item_button.pack(pady=5)
            row_data["value_entry"] = None
            row_data["list_container"] = list_container
            row_data["list_entries"] = list_entries

    def remove_metadata_row(self, row_frame):
        row_frame.destroy()
        self.metadata_entries = [row for row in self.metadata_entries if row["frame"] != row_frame]

    def validate_and_proceed(self):
        exp_name = self.exp_name_entry.get().strip()
        participant_name = self.participant_entry.get().strip()

        if not exp_name or not participant_name:
            self.error_label.config(text="Please fill in both the experiment name and participant name.")
            return

        self.error_label.config(text="")  # Clear error message

        # Save experiment and participant info and collect metadata details.
        self.saved_exp_name = exp_name
        self.saved_participant_name = participant_name
        self.saved_metadata = []

        for row in self.metadata_entries:
            name = row["name_entry"].get().strip()
            type_val = row["type_combobox"].get()
            if type_val == "Value":
                # Retrieve value from the entry; if none, set to empty.
                value = row["value_entry"].get().strip() if row["value_entry"] else ""
                metadata_item = {"name": name, "type": "Value", "value": value}
            else:
                # Get all non-empty list item entries.
                list_values = [entry.get().strip() for entry in row["list_entries"] if entry.get().strip()]
                metadata_item = {"name": name, "type": "List", "value": list_values}
            self.saved_metadata.append(metadata_item)

        # Proceed with the editor screen using collected information.
        show_editor_screen(self)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExperimentApp(root)
    root.mainloop()