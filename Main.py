import tkinter as tk
from tkinter import ttk
import os
from tkinter import filedialog
import sys
import json
from translations import translations
from editor_screen import show_editor_screen
from launch_screen import show_launch_screen
from styles import apply_theme
from styles import ENTRY_FONT,COMBO_FONT,METADATA_ENTRY,SELECT_METADATA,CANVAS_BG
STATE_FILE = "create_screen_state.json"

class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        apply_theme(container)
        self.canvas = tk.Canvas(self, bg="#ffffff", highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)
        self.current_screen = "main"  # default screen

        # Inner frame placed in the canvas
        self.scrollable_frame = tk.Frame(self.canvas, bg="#ffffff")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Bind enter/leave on both frame and canvas
        for w in (self, self.canvas):
            w.bind("<Enter>", self._bind_mousewheel)
            w.bind("<Leave>", self._unbind_mousewheel)

    def _on_mousewheel(self, event):
        # only scroll if content taller than viewport
        bbox = self.canvas.bbox("all")
        if bbox:
            content_height = bbox[3] - bbox[1]
            view_height = self.canvas.winfo_height()
            if content_height <= view_height:
                return  # nothing to scroll
        
        delta = event.delta
        if sys.platform == "darwin":
            self.canvas.yview_scroll(-1 * delta, "units")
        else:
            # Windows: delta is multiple of 120
            self.canvas.yview_scroll(-1 * (delta // 120), "units")

    def _bind_mousewheel(self, _):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, _):
        self.canvas.unbind_all("<MouseWheel>")

class ExperimentApp:
    def __init__(self, root):
        self.root = root
        self.root.app = self
        self.root.title("Emotional Visual Search Experiment Launcher")
        self.root.geometry("1200x800")
        self.root.minsize(600, 400)
        self.root.configure(bg="#f0f0f0")  # Light, neutral background
        apply_theme(self.root)  

        # Initialize persistent values
        self.saved_exp_name = "Default_Experiment_name"
        self.saved_participant_name = "Participant"
        self.saved_save_location = os.path.join(os.getcwd(), "experiments")
        self.saved_metadata = [] 

        # List to store metadata rows (each row is represented as a dictionary of widget references)
        self.metadata_entries = []

        self.translations = translations
        self.languages = list(self.translations.keys())  # Get languages dynamically
        self.current_language = "EN"  # Default language

        self.imported_stimulus_sets = {}
        self.load_create_screen_state()
        self.show_main_screen()

        self.fullscreen = False
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', self.exit_fullscreen)

        self.root.title("Emotional Visual Search Experiment Launcher")
     # Toggle fullscreen mode
    def toggle_fullscreen(self, event=None):
        """
        Toggle fullscreen mode on or off.
        """
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)
     # Exit fullscreen mode
    def exit_fullscreen(self, event=None):
        """
        Exit fullscreen mode.
        """
        self.fullscreen = False
        self.root.attributes('-fullscreen', False)
    # Translation helper
    def tr(self, key):
        return self.translations[self.current_language].get(key, key)
    # Clear all widgets from the root window
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
     # Change application language
    def change_language(self):
        def set_language(new_lang):
            self.current_language = new_lang
            self.show_main_screen()  # Refresh current screen
            popup.destroy()

        popup = tk.Toplevel(self.root)
        popup.title(self.tr("change_language"))
        popup.geometry("300x200")
        tk.Label(popup, text=self.tr("change_language")).pack(pady=10)

        for lang in self.languages:
            btn = ttk.Button(popup, text=lang, command=lambda l=lang: set_language(l))
            btn.pack(pady=5)
    # Handle language change from dropdown
    def on_language_change(self, event=None):
        selected_language = self.language_var.get()
        self.current_language = selected_language
        # Reopen the correct screen
        if self.current_screen == "main":
            self.show_main_screen()
        elif self.current_screen == "create":
            self.show_create_screen()
        elif self.current_screen == "launch":
            self.show_launch_screen()
        elif self.current_screen == "session_start":
            from experiment_session_start import show_experiment_session_start
            show_experiment_session_start(self, self.experiment_name, self.experiment_path, self.continue_mode)
     
    # Show the main screen UI
    def show_main_screen(self):
        self.current_screen = "main"
        self.clear_screen()
        self.root.configure(bg="#f0f0f0")

        # TOP BAR (Language selection)
        top_bar = tk.Frame(self.root, bg="#f0f0f0")
        top_bar.pack(fill="x", side="top", anchor="nw", padx=20, pady=10)  

        self.language_var = tk.StringVar(value=self.current_language)
        lang_dropdown = ttk.Combobox(
            top_bar,
            textvariable=self.language_var,
            values=self.languages,
            state="readonly",
            font=SELECT_METADATA,
            style="Language.TCombobox",
            width=12
        )
        lang_dropdown.pack(side="left")
        lang_dropdown.bind("<<ComboboxSelected>>", self.on_language_change)

        # Header Frame for title and buttons
        header_frame = tk.Frame(self.root, bg="#f0f0f0")
        header_frame.pack(expand=True, pady=50)
        title_label = ttk.Label(header_frame, text=self.tr("visual_search_launcher"), anchor="center")
        title_label.pack(pady=(0, 30))

        button_frame = tk.Frame(header_frame, bg="#f0f0f0")
        button_frame.pack()
        
        create_button = ttk.Button(button_frame, text=self.tr("create_experiment"), command=self.show_create_screen)
        create_button.grid(row=0, column=0, padx=20, pady=20)
        
        launch_button = ttk.Button(button_frame, text=self.tr("launch_experiment"), command=self.show_launch_screen)
        launch_button.grid(row=0, column=1, padx=20, pady=20)
    # Open directory chooser and update the entry
    def choose_save_location(self):
        directory = filedialog.askdirectory(initialdir=self.save_location_entry.get() or os.getcwd())
        if directory:
            self.save_location_entry.delete(0, tk.END)
            self.save_location_entry.insert(0, directory)
            self.saved_save_location = directory 
     # Map translated metadata type to internal value
    def get_real_type(self, displayed_type):
        """
        Maps translated type (displayed text) back to internal real type: 'Value' or 'List'
        """
        if displayed_type == self.tr("value"):
            return "Value"
        elif displayed_type == self.tr("list"):
            return "List"
        else:
            return displayed_type  # fallback (shouldn't happen)
    
    def show_create_screen(self):
        self.current_screen = "create"
        self.clear_screen()
        self.metadata_entries = []  # Reset metadata entries
        # TOP BAR (Language selection for Create Screen)
        top_bar = tk.Frame(self.root, bg="#f0f0f0")
        top_bar.pack(fill="x", side="top", anchor="nw", padx=20, pady=10)

        self.language_var = tk.StringVar(value=self.current_language)
        lang_dropdown = ttk.Combobox(
            top_bar,
            textvariable=self.language_var,
            values=self.languages,
            state="readonly",
            font=SELECT_METADATA,
            style="Language.TCombobox",
            width=12
        )
        lang_dropdown.pack(side="left")
        lang_dropdown.bind("<<ComboboxSelected>>", self.on_language_change)


        # Main container for the create screen
        main_frame = tk.Frame(self.root, bg="#f0f0f0", padx=40, pady=40)
        main_frame.pack(expand=True, fill="both")
        
        header_label = ttk.Label(main_frame, text=self.tr("create_new_experiment"), font=("Segoe UI", 24, "bold"))
        header_label.pack(pady=(0, 30))
        
        self.error_label = ttk.Label(main_frame, text="", foreground="red", font=("Segoe UI", 12))
        self.error_label.pack(pady=(0, 10))
        
        # Form container for Experiment Name and Participant Default Name fields
        form_frame = tk.Frame(main_frame, bg="#f0f0f0")
        form_frame.pack(pady=10)
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)

        # Save Location row
        save_label = ttk.Label(form_frame, text=self.tr("save_location"), font=("Segoe UI", 18, "bold"), background="#f0f0f0")
        save_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.save_location_entry = ttk.Entry(form_frame, width=50,font=ENTRY_FONT,style="TEntry")
        self.save_location_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.save_location_entry.insert(0, self.saved_save_location)
        choose_button = ttk.Button(form_frame, text=self.tr("choose"),command=self.choose_save_location,style="Small.TButton")
        choose_button.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        
        exp_label = ttk.Label(form_frame, text=self.tr("experiment_name"), font=("Segoe UI", 18, "bold"), background="#f0f0f0")
        exp_label.grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.exp_name_entry = ttk.Entry(form_frame, width=50,font=ENTRY_FONT,style="TEntry")
        self.exp_name_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.exp_name_entry.insert(0, self.saved_exp_name)
        
        part_label = ttk.Label(form_frame, text=self.tr("participant_default_name"), font=("Segoe UI", 18, "bold"), background="#f0f0f0")
        part_label.grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.participant_entry = ttk.Entry(form_frame, width=50,font=ENTRY_FONT,style="TEntry")
        self.participant_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.participant_entry.insert(0, self.saved_participant_name)
        
        # Metadata section container to hold metadata rows
        metadata_container = tk.Frame(main_frame, bg="#f0f0f0")
        metadata_container.pack(pady=10, padx=20, fill="both")
        metadata_container.configure(height=200)
        metadata_container.pack_propagate(False)

        scrollable = ScrollableFrame(metadata_container, bd=2, relief="groove", padx=10, pady=10)
        scrollable.pack(fill="both", expand=True)

        self.metadata_frame = scrollable.scrollable_frame
        # --- end scrollable setup ---

        # Load saved metadata rows or one empty row
        if self.saved_metadata:
            for md in self.saved_metadata:
                self.add_metadata_row(initial_data=md)
        else:
            self.add_metadata_row()

        # + Add Metadata button, action buttons, etc.
        add_button = ttk.Button(main_frame, text=self.tr("add_metadata"), command=self.add_metadata_row)
        add_button.pack(pady=10)

        action_frame = tk.Frame(main_frame, bg="#f0f0f0")
        action_frame.pack(pady=20)
        back_button = ttk.Button(action_frame, text=self.tr("back"), command=self.back_to_main)
        back_button.grid(row=0, column=0, padx=20)
        create_button = ttk.Button(action_frame, text=self.tr("create"), command=self.validate_and_proceed)
        create_button.grid(row=0, column=1, padx=20)
    # Show launch screen
    def show_launch_screen(self):
        show_launch_screen(self)


    def add_metadata_row(self, initial_data=None):
        """
        Adds a metadata row that allows entering a metadata name and choosing whether its value is a
        single entry (Value) or a list of items (List). Both the white placeholder (for Value)
        and the list container (for List) are created; it shows one and hide the other.
        """
        row_frame = tk.Frame(self.metadata_frame, bg="#ffffff")
        row_frame.pack(fill="x", pady=5)

        # Metadata name entry field
        name_entry = ttk.Entry(row_frame, width=20,font=COMBO_FONT)
        name_entry.pack(side="left", padx=5)
        if initial_data and "name" in initial_data:
            name_entry.insert(0, initial_data["name"])

       # Determine initial mode (default to "Value")
        internal_mode = initial_data.get("type", "Value") if initial_data else "Value"

        # build the translated values list
        value_label = self.tr("value")
        list_label  = self.tr("list")
        values = [value_label, list_label]

        # create the combobox 
        type_combobox = ttk.Combobox(
            row_frame,
            values=values,
            state="readonly",
            width=10,
            font=SELECT_METADATA,
            style="Listbox.TCombobox"
        )
        type_combobox.pack(side="left", padx=5)

        # pick the right one
        if internal_mode == "Value":
            type_combobox.current(0)
        else:
            type_combobox.current(1)
        # Content frame that will hold either the white placeholder or list input controls.
        content_frame = tk.Frame(row_frame, bg="#ffffff")
        content_frame.pack(side="left", padx=5, fill="x", expand=True)

        # Create the white rectangle placeholder (for Value mode)
        placeholder = tk.Frame(content_frame, bg="white", width=200, height=30)
        placeholder.pack_propagate(False)

        # Create the list container (for List mode) along with an "Add Item" button.
        list_container = tk.Frame(content_frame, bg="#ffffff")
        list_entries = []
        add_item_button = ttk.Button(
            content_frame,
            text=self.tr("add_item"),
            style="AddItem.TButton",
            command=lambda: self._add_list_item(list_container, list_entries)
        )

        # Determine the initial mode (default to "Value")
        initial_mode = initial_data.get("type", "Value") if initial_data else "Value"
        if initial_mode == "List":
            # Populate list container with provided data if available.
            if initial_data and "value" in initial_data:
                for item in initial_data["value"]:
                    entry = self._create_list_item(list_container, initial_text=item)
                    list_entries.append(entry)
            # If no initial list items, create an empty one.
            if not list_entries:
                entry = self._create_list_item(list_container)
                list_entries.append(entry)
            # Show list container and add item button
            list_container.pack(side="left", fill="x", padx=5, pady=5)
            add_item_button.pack(side="left", padx=5, pady=5)
            # Hide the placeholder
            placeholder.pack_forget()
        else:
            # Mode is "Value": show the placeholder and hide list elements.
            placeholder.pack(side="left", padx=5, pady=5)
            list_container.pack_forget()
            add_item_button.pack_forget()

        # Store widget references in a dictionary.
        row_data = {
            "frame": row_frame,
            "name_entry": name_entry,
            "type_combobox": type_combobox,
            "content_frame": content_frame,
            "value_placeholder": placeholder,
            "list_container": list_container,
            "list_entries": list_entries,
            "add_item_button": add_item_button
        }

        # Remove metadata button for this row.
        remove_btn = ttk.Button(
            row_frame,
            text=self.tr("remove"),
            command=lambda: self.remove_metadata_row(row_frame),
            style="Small.TButton"
        )
        remove_btn.pack(side="left", padx=5)

        # Bind a callback when the type is changed.
        type_combobox.bind("<<ComboboxSelected>>", lambda event, d=row_data: self._on_type_change(d))

        self.metadata_entries.append(row_data)

    def _create_list_item(self, container, initial_text=""):
        """
        Creates a single list item entry within a metadata row (for list-type metadata).
        """
        row = tk.Frame(container, bg="#ffffff")
        row.pack(fill="x", pady=2)
        entry = ttk.Entry(row, width=35,font=METADATA_ENTRY)
        entry.pack(side="left", padx=5)
        entry.insert(0, initial_text)
        remove_btn = ttk.Button(row, text=self.tr("remove"), style="Small.TButton", command=row.destroy)
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
        type_val = self.get_real_type(row_data["type_combobox"].get())
        if type_val == "Value":
            # Show the white placeholder.
            row_data["value_placeholder"].pack(side="left", padx=5, pady=5)
            # Hide the list container and its add button.
            row_data["list_container"].pack_forget()
            row_data["add_item_button"].pack_forget()
        elif type_val == "List":
            # Hide the white placeholder.
            row_data["value_placeholder"].pack_forget()
            # Show the list container and its add button.
            row_data["list_container"].pack(side="left", fill="x", padx=5, pady=5)
            row_data["add_item_button"].pack(side="left", padx=5, pady=5)

    def remove_metadata_row(self, row_frame):
        row_frame.destroy()
        self.metadata_entries = [row for row in self.metadata_entries if row["frame"] != row_frame]

    def validate_and_proceed(self):
        exp_name = self.exp_name_entry.get().strip()
        participant_name = self.participant_entry.get().strip()

        if not exp_name or not participant_name:
            self.error_label.config(text=self.tr("please_fill_fields"))
            return

        # Clear any previous error message
        self.error_label.config(text="")

        # Save experiment and participant info and collect metadata details.
        self.saved_exp_name = exp_name
        self.saved_participant_name = participant_name
        self.saved_save_location = self.save_location_entry.get().strip()
        self.saved_metadata = []

        for row in self.metadata_entries:
            name = row["name_entry"].get().strip()
            # Validate the main metadata field is not empty.
            if not name:
                self.error_label.config(text=self.tr("metadata_field_empty"))
                return

            type_val = self.get_real_type(row["type_combobox"].get())
            if type_val == "Value":
                # In your code the "Value" mode uses a placeholder.
                # If you later add an input widget for this mode, replace "N/A" with its content.
                value = "N/A"
                metadata_item = {"name": name, "type": "Value", "value": value}
            else:  # When in "List" mode.
                # Get all non-empty list item entries.
                list_values = [entry.get().strip() for entry in row["list_entries"] if entry.get().strip()]
                if not list_values:
                    self.error_label.config(text=f"{self.tr('at_least_one_list_item')} '{name}'.")
                    return
                metadata_item = {"name": name, "type": "List", "value": list_values}
            self.saved_metadata.append(metadata_item)

        self.save_current_create_screen_state()
        # Proceed with the editor screen using the collected information.
        show_editor_screen(self)
    # Save current create screen state to file
    def save_current_create_screen_state(self):
        data = {
            "exp_name": self.saved_exp_name,
            "participant_name": self.saved_participant_name,
            "save_location": self.saved_save_location,
            "metadata": self.saved_metadata
        }
        with open(STATE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    # Load saved create screen state from file
    def load_create_screen_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r") as f:
                    data = json.load(f)
                    self.saved_exp_name = data.get("exp_name", "Default_Experiment_name")
                    self.saved_participant_name = data.get("participant_name", "Participant")
                    self.saved_save_location = data.get("save_location", os.getcwd())
                    self.saved_metadata = data.get("metadata", [])
            except Exception as e:
                print(f"Error loading saved create screen state: {e}")

     # Go back to main screen
    def back_to_main(self):
        """
        Saves the current create screen state and then returns to the main screen.
        """
        self.save_current_create_screen_state()
        self.show_main_screen()

if __name__ == "__main__":
    root = tk.Tk()
    root.option_add('*TCombobox*Listbox.font', SELECT_METADATA)
    root.option_add('*TCombobox*Listbox.background', CANVAS_BG)
    root.option_add('*TCombobox*Listbox.foreground', '#000000')
    apply_theme(root)
    app = ExperimentApp(root)
    root.mainloop()
