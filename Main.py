import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class ExperimentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Emotional visual search experiment Launcher")
        self.root.geometry("1200x800")
        self.root.minsize(600, 400)
        #self.root.configure(bg="#dcdcdc")  # light gray background

        self.saved_exp_name = ""
        self.saved_participant_name = ""
        self.saved_metadata = []

        self.show_main_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    def show_main_screen(self):
        self.clear_screen()

        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 16), padding=10)
        style.configure("TLabel", font=("Segoe UI", 24, "bold"))
        # Main title
        title_label = ttk.Label(self.root, text="Visual search experiment launcher")
        title_label.place(relx=0.5, rely=0.2, anchor="center")

        # Create experiment button (centered below title)
        create_button = ttk.Button(self.root, text="Create experiment", width=25,command=self.show_create_screen)
        create_button.place(relx=0.5, rely=0.4, anchor="center")

        # Launch experiment button (further below)
        launch_button = ttk.Button(self.root, text="Launch experiment", width=25)
        launch_button.place(relx=0.5, rely=0.55, anchor="center")

    def show_create_screen(self):
        self.clear_screen()
        self.metadata_entries = []

        self.error_label = tk.Label(self.root, text="", fg="red", bg="#dcdcdc", font=("Segoe UI", 10, "italic"))
        self.error_label.place(relx=0.5, rely=0.25, anchor="n")

        form_frame = tk.Frame(self.root, bg="#dcdcdc")
        form_frame.place(relx=0.5, rely=0.05, anchor="n")

        ttk.Label(form_frame, text="Experiment name:", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="e", padx=10, pady=10)
        self.exp_name_entry = ttk.Entry(form_frame, width=40)
        self.exp_name_entry.grid(row=0, column=1, padx=10, pady=10)
        self.exp_name_entry.insert(0, self.saved_exp_name)

        ttk.Label(form_frame, text="Participant default name:", font=("Segoe UI", 12, "bold")).grid(row=1, column=0, sticky="e", padx=10, pady=10)
        self.participant_entry = ttk.Entry(form_frame, width=40)
        self.participant_entry.grid(row=1, column=1, padx=10, pady=10)
        self.participant_entry.insert(0, self.saved_participant_name)

        metadata_container = tk.Frame(self.root, bg="#dcdcdc")
        metadata_container.place(relx=0.5, rely=0.3, anchor="n")

        tk.Label(metadata_container, text="Metadata:", font=("Segoe UI", 11, "italic"), bg="#dcdcdc").pack(anchor="w", padx=5)

        self.metadata_frame = tk.Frame(metadata_container, bg="#fceeee", padx=10, pady=10)
        self.metadata_frame.pack(pady=10, fill="x", expand=True)

        # Recreate metadata entries from saved data
        for name in self.saved_metadata:
            self.add_metadata_row(name)

        add_button = tk.Button(metadata_container, text="+ Add metadata", command=self.add_metadata_row, bg="#fef6f6")
        add_button.pack()

        button_frame = tk.Frame(self.root, bg="#dcdcdc")
        button_frame.place(relx=0.5, rely=0.9, anchor="center")

        back_button = tk.Button(button_frame, text="Back", font=("Segoe UI", 12, "bold"), width=12,
                                bg="#fef6f6", command=self.show_main_screen)
        back_button.pack(side="left", padx=40)

        create_button = tk.Button(button_frame, text="Create", font=("Segoe UI", 12, "bold"), width=12,
                                  bg="#fef6f6", command=self.validate_and_proceed)
        create_button.pack(side="right", padx=40)

    def add_metadata_row(self, name_text=""):
        row_frame = tk.Frame(self.metadata_frame, bg="#fceeee")
    
        name_entry = ttk.Entry(row_frame, width=40)
        name_entry.insert(0, name_text)

        remove_btn = tk.Button(row_frame, text="Remove", command=lambda: self.remove_metadata_row(row_frame), bg="#fef6f6")

        name_entry.pack(side="left", padx=5, pady=5)
        remove_btn.pack(side="left", padx=5)

        row_frame.pack(anchor="w", pady=2)
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

        self.error_label.config(text="")  # Clear error

        # Save values
        self.saved_exp_name = exp_name
        self.saved_participant_name = participant_name
        self.saved_metadata = []
        for _, name_entry in self.metadata_entries:
            name = name_entry.get().strip()
            if name:
                self.saved_metadata.append(name)


        self.show_editor_screen()
    
    def show_editor_screen(self):
        self.clear_screen()

        # Go Back Arrow
        back_btn = tk.Button(self.root, text="←", font=("Arial", 16), bg="#fef6f6", command=self.show_create_screen)
        back_btn.place(x=10, y=10)

        # Main white canvas
        editor_frame = tk.Frame(self.root, bg="white", bd=2, relief="flat")
        editor_frame.place(relx=0.025, rely=0.025, relwidth=0.7, relheight=0.65)

        # Timeline or bottom white area
        timeline_frame = tk.Frame(self.root, bg="white", bd=2, relief="flat")
        timeline_frame.place(relx=0.025, rely=0.7, relwidth=0.7, relheight=0.2)

        # Start block
        start_block = tk.Frame(timeline_frame, width=60, height=60, bg="green")
        start_block.pack(padx=20, pady=10, anchor="nw")
        tk.Label(timeline_frame, text="Start", bg="white").place(x=22, y=75)

        # Component panel
        components_panel = tk.Frame(self.root, bg="white", bd=2, relief="flat")
        components_panel.place(relx=0.75, rely=0.025, relwidth=0.22, relheight=0.65)

        tk.Label(components_panel, text="Components", font=("Segoe UI", 12, "bold"), bg="#dcdcdc").pack(fill="x")

        comp_data = [
            ("Text", "gray"),
            ("Stimulus", "yellow"),
            ("Stimulus notification", "purple"),
            ("End", "red")
        ]

        for label, color in comp_data:
            block = tk.Frame(components_panel, bg=color, width=60, height=60)
            block.pack(pady=10)
            tk.Label(components_panel, text=label, font=("Segoe UI", 10, "bold"), bg="white").pack()

        # Create button
        create_button = tk.Button(self.root, text="Create", font=("Segoe UI", 12), bg="#fef6f6", width=12)
        create_button.place(relx=0.82, rely=0.8)
        
root = tk.Tk()
app = ExperimentApp(root)
root.mainloop()

