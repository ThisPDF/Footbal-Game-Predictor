import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import os
import threading


# Define placeholders for default CSV paths (to be filled later)
default_csv1 = "./data/robotics_competitions_data.csv"  # Replace with actual path
default_csv2 = "./data/romanian_football_data.csv"  # Replace with actual path

# Paths to scripts
project_dir = '../'  # Adjust if needed
scraper_py_path = os.path.join(project_dir, 'scraper.py')
scraper_robotica_py_path = os.path.join(project_dir, 'scraper_robotica.py')
main_py_path = os.path.join(project_dir, 'main.py')


def run_script_in_thread(script_path, csv_path=None, output_widget=None):
    """Run a script and capture its output in a thread."""
    def task():
        command = ['python3', script_path]
        if csv_path:
            command.append(csv_path)

        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            for line in process.stdout:
                if output_widget:
                    output_widget.insert(tk.END, line)
                    output_widget.see(tk.END)
            for line in process.stderr:
                if output_widget:
                    output_widget.insert(tk.END, line, "error")
                    output_widget.see(tk.END)
            process.wait()
            if process.returncode == 0:
                messagebox.showinfo("Success", f"{os.path.basename(script_path)} executed successfully!")
            else:
                messagebox.showerror("Error", f"{os.path.basename(script_path)} failed with return code {process.returncode}.")
        except Exception as e:
            if output_widget:
                output_widget.insert(tk.END, f"An error occurred: {str(e)}\n", "error")
                output_widget.see(tk.END)

    threading.Thread(target=task).start()


def select_and_run():
    """Execute the selected scraper or set the default CSV, then run main.py."""
    selection = scraper_choice.get()

    if selection == "Get new footbal data(warnig replaces old one)":
        run_script_in_thread(scraper_py_path, output_widget=console_output)
        csv_path = "../data/romanian_football_data.csv"  # Replace with scraper output path
    elif selection == "Get new robotics data(warnig replaces old one)":
        run_script_in_thread(scraper_robotica_py_path, output_widget=console_output)
        csv_path = "../data/robotics_competitions_data.csv"  # Replace with scraper output path
    elif selection == "Robotics Default":
        csv_path = default_csv1
        console_output.insert(tk.END, f"Using default: {default_csv1}\n")
    elif selection == "Footbal Default":
        csv_path = default_csv2
        console_output.insert(tk.END, f"Using default: {default_csv2}\n")
    else:
        messagebox.showerror("Error", "Please select an option!")
        return

    # Run main.py with the selected CSV
    run_script_in_thread(main_py_path, csv_path, output_widget=console_output)


# Create the GUI application
app = tk.Tk()
app.title("Retea Neuronala Manager")
app.geometry("600x400")

# Dropdown menu for selecting scraper or default CSV
scraper_choice = tk.StringVar(value="Select an option")
choices = ["Get new footbal data(warnig replaces old one)", "Get new robotics data(warnig replaces old one)", "Robotics Default", "Footbal Default"]
ttk.Label(app, text="Select an option to update data or use default:", font=("Arial", 12)).pack(pady=10)
dropdown = ttk.Combobox(app, textvariable=scraper_choice, values=choices, state="readonly")
dropdown.pack(pady=10)

# Button to confirm selection
ttk.Button(app, text="Run", command=select_and_run).pack(pady=20)

# ScrolledText widget to display console output
console_output = scrolledtext.ScrolledText(app, wrap=tk.WORD, height=15)
console_output.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

# Configure error tag for console output
console_output.tag_config("error", foreground="red")

# Start the GUI loop
app.mainloop()
