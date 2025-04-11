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
        # Small button style for the remove metadata button
        self.style.configure("Small.TButton", font=("Segoe UI", 10), padding=(2, 2))

        # Global style for Labels and Entry fields
        # (Other labels in your app may be affected, so if you want to change only a few labels you can set the font explicitly.)
        self.style.configure("TLabel", font=("Segoe UI", 20, "bold"), background="#f0f0f0")
        self.style.configure("TEntry", font=("Segoe UI", 16))  # Increased font size from 14 to 16

        # Stored values for persistence
        self.saved_exp_name = ""
        self.saved_participant_name = ""
        self.saved_metadata = [] 

        self.show_main_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_main_screen(self):
        self.clear_screen()
        
        # Header Frame for title and buttons
        header_frame = tk.Frame(self.root, bg="#f0f0f0")
        header_frame.pack(expand=True, pady=50)
        
        # Main title
        title_label = ttk.Label(header_frame, text="Visual Search Experiment Launcher", anchor="center")
        title_label.pack(pady=(0, 30))
        
        # Button Frame for main actions
        button_frame = tk.Frame(header_frame, bg="#f0f0f0")
        button_frame.pack()
        
        create_button = ttk.Button(button_frame, text="Create Experiment", command=self.show_create_screen)
        create_button.grid(row=0, column=0, padx=20, pady=20)
        
        launch_button = ttk.Button(button_frame, text="Launch Experiment")
        launch_button.grid(row=0, column=1, padx=20, pady=20)

    def show_create_screen(self):
        self.clear_screen()
        self.metadata_entries = []

        # Main container
        main_frame = tk.Frame(self.root, bg="#f0f0f0", padx=40, pady=40)
        main_frame.pack(expand=True, fill="both")
        
        header_label = ttk.Label(main_frame, text="Create New Experiment", font=("Segoe UI", 24, "bold"))
        header_label.pack(pady=(0, 30))
        
        # Error label for validation messages
        self.error_label = ttk.Label(main_frame, text="", foreground="red", font=("Segoe UI", 12))
        self.error_label.pack(pady=(0, 10))
        
        # Form container for Experiment Name and Participant Default Name fields
        form_frame = tk.Frame(main_frame, bg="#f0f0f0")
        form_frame.pack(pady=10)
        
        # Configure grid columns for centering fields
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)
        
        # Experiment Name field with larger label text
        exp_label = ttk.Label(form_frame, text="Experiment Name:", font=("Segoe UI", 18, "bold"), background="#f0f0f0")
        exp_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.exp_name_entry = ttk.Entry(form_frame, width=50)  # Increased width for larger field
        self.exp_name_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.exp_name_entry.insert(0, self.saved_exp_name)
        
        # Participant Default Name field with larger label text
        part_label = ttk.Label(form_frame, text="Participant Default Name:", font=("Segoe UI", 18, "bold"), background="#f0f0f0")
        part_label.grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.participant_entry = ttk.Entry(form_frame, width=50)  # Increased width for larger field
        self.participant_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.participant_entry.insert(0, self.saved_participant_name)
        
        # Metadata section container to synchronize label and field
        metadata_container = tk.Frame(main_frame, bg="#f0f0f0")
        metadata_container.pack(pady=10, padx=20, fill="x")
        
        # Metadata label: center-aligned text
        metadata_label = ttk.Label(metadata_container, text="Metadata:", font=("Segoe UI", 24, "bold"), background="#f0f0f0", anchor="center")
        metadata_label.pack(pady=(0,5), anchor="center")
        
        # Metadata field container: fixed (narrower) width and centered
        self.metadata_frame = tk.Frame(metadata_container, bg="#ffffff", bd=2, relief="groove", padx=10, pady=10, width=500)
        self.metadata_frame.pack(anchor="center")
        
        # Force the metadata frame to have at least one row by default.
        if not self.saved_metadata:
            self.add_metadata_row()
        else:
            for name in self.saved_metadata:
                self.add_metadata_row(name)
        
        # Add Metadata button
        add_button = ttk.Button(main_frame, text="+ Add Metadata", command=self.add_metadata_row)
        add_button.pack(pady=10)
        
        # Action buttons at the bottom
        action_frame = tk.Frame(main_frame, bg="#f0f0f0")
        action_frame.pack(pady=20)
        
        back_button = ttk.Button(action_frame, text="Back", command=self.show_main_screen)
        back_button.grid(row=0, column=0, padx=20)
        create_button = ttk.Button(action_frame, text="Create", command=self.validate_and_proceed)
        create_button.grid(row=0, column=1, padx=20)

    def add_metadata_row(self, name_text=""):
        row_frame = tk.Frame(self.metadata_frame, bg="#ffffff")
        row_frame.pack(fill="x", pady=5)
        
        name_entry = ttk.Entry(row_frame, width=40)
        name_entry.pack(side="left", padx=5)
        name_entry.insert(0, name_text)
        
        # Remove metadata button with smaller height using "Small.TButton" style
        remove_btn = ttk.Button(row_frame, text="Remove", command=lambda: self.remove_metadata_row(row_frame), style="Small.TButton")
        remove_btn.pack(side="left", padx=5)
        
        self.metadata_entries.append((row_frame, name_entry))

    def remove_metadata_row(self, row_frame):
        row_frame.destroy()
        self.metadata_entries = [row for row in self.metadata_entries if row[0] != row_frame]

    def validate_and_proceed(self):
        exp_name = self.exp_name_entry.get().strip()
        participant_name = self.participant_entry.get().strip()

        if not exp_name or not participant_name:
            self.error_label.config(text="Please fill in both the experiment name and participant name.")
            return

        self.error_label.config(text="")  # Clear error message

        # Save values
        self.saved_exp_name = exp_name
        self.saved_participant_name = participant_name
        self.saved_metadata = []
        for _, name_entry in self.metadata_entries:
            name = name_entry.get().strip()
            if name:
                self.saved_metadata.append(name)

        show_editor_screen(self)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExperimentApp(root)
    root.mainloop()


