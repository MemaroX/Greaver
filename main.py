
import tkinter as tk
from tkinter import ttk
import subprocess
import threading

class ReaverGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Reaver GUI")
        self.geometry("800x600")

        self.create_widgets()

    def create_widgets(self):
        # Frame for options
        options_frame = ttk.LabelFrame(self, text="Reaver Options")
        options_frame.pack(padx=10, pady=10, fill="x")

        # BSSID
        ttk.Label(options_frame, text="BSSID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.bssid_entry = ttk.Entry(options_frame, width=30)
        self.bssid_entry.grid(row=0, column=1, padx=5, pady=5)

        # Interface
        ttk.Label(options_frame, text="Interface:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.interface_combobox = ttk.Combobox(options_frame, width=28)
        self.interface_combobox.grid(row=1, column=1, padx=5, pady=5)
        self.populate_interfaces()

        # Start button
        self.start_button = ttk.Button(self, text="Start Reaver", command=self.start_reaver)
        self.start_button.pack(pady=10)

        # Output text area
        self.output_text = tk.Text(self, height=25, width=100)
        self.output_text.pack(padx=10, pady=10)

    def get_interfaces(self):
        try:
            output = subprocess.check_output(["iwconfig"], text=True)
            interfaces = []
            for line in output.split("\n"):
                if line and not line.startswith(" "):
                    if "no wireless extensions" not in line:
                        interfaces.append(line.split()[0])
            return interfaces
        except FileNotFoundError:
            return [] # iwconfig not found
        except Exception as e:
            print(f"Error getting interfaces: {e}")
            return []

    def populate_interfaces(self):
        interfaces = self.get_interfaces()
        self.interface_combobox['values'] = interfaces
        if interfaces:
            self.interface_combobox.current(0)

    def start_reaver(self):
        bssid = self.bssid_entry.get()
        interface = self.interface_combobox.get()

        if not bssid or not interface:
            self.output_text.insert(tk.END, "BSSID and Interface are required.\n")
            return

        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"Starting Reaver with BSSID: {bssid} and Interface: {interface}\n")

        # Disable start button while running
        self.start_button.config(state="disabled")

        # Run reaver in a separate thread to avoid blocking the GUI
        reaver_thread = threading.Thread(target=self.run_reaver_process, args=(bssid, interface))
        reaver_thread.start()

    def run_reaver_process(self, bssid, interface):
        try:
            command = ["reaver", "-i", interface, "-b", bssid, "-vv"]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)

            for line in process.stdout:
                self.output_text.insert(tk.END, line)
                self.output_text.see(tk.END)
                self.update_idletasks()

            process.wait()

        except FileNotFoundError:
            self.output_text.insert(tk.END, "Error: 'reaver' command not found. Make sure it's installed and in your PATH.\n")
        except Exception as e:
            self.output_text.insert(tk.END, f"An error occurred: {e}\n")
        finally:
            # Re-enable start button
            self.start_button.config(state="normal")

if __name__ == "__main__":
    app = ReaverGUI()
    app.mainloop()
