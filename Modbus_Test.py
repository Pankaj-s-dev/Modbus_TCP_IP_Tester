import customtkinter as ctk
from tkinter import messagebox
from pymodbus.client import ModbusTcpClient
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
import threading
import logging
import time
import socket

logging.basicConfig(level=logging.INFO)


class ModbusTesterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("⚙️ Modbus TCP/IP Tester")
        self.geometry("1200x700")
        # self.resizable(False, False)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        

        self.client = None
        self.is_running = False
        self.server_thread = None
        self.auto_interval = 0

        self.start_addr_holding = 0
        self.start_addr_input = 0
        self.start_addr_coils = 0
        self.start_addr_Dis_input = 0
        self._ip = "127.0.0.1"
        self._port = 1024

        self.create_ui()

    def create_ui(self):
        # --- Tabs ---
        self.tabview = ctk.CTkTabview(self)
        self.tab_main = self.tabview.add("Main")
        self.tab_log = self.tabview.add("Log")
        self.tab_settings = self.tabview.add("Settings")
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)

        # --- Top Controls ---
        top_frame = ctk.CTkFrame(self.tab_main)
        top_frame.pack(pady=10, padx=10, fill="x")

        for i in range(10):
            top_frame.grid_columnconfigure(i, weight=1, uniform="equal")

        self.mode_var = ctk.StringVar(value="Client")

        # --- Mode ---
        ctk.CTkLabel(
            top_frame, 
            text="Mode:", 
            font=("Consolas", 15, "bold"),
            anchor="center"
            ).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        
        self.mode_menu = ctk.CTkOptionMenu(
            top_frame,
            variable=self.mode_var,
            values=["Client", "Server"],
            width=130,
            command=self.on_mode_change
        )
        self.mode_menu.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # --- IP Address ---
        ctk.CTkLabel(
            top_frame, 
            text="IP Address:",
            font=("Consolas", 15, "bold"),
            anchor="center"
            ).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        
        self.ip_entry = ctk.CTkEntry(top_frame, placeholder_text=self._ip, width=220)
        self.ip_entry.insert(0, self._ip)
        self.ip_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # --- Port ---
        ctk.CTkLabel(
            top_frame, 
            text="Port:",
            font=("Consolas", 15, "bold"),
            anchor="center"
            ).grid(row=0, column=4, padx=5, pady=5, sticky="e")
        
        self.port_entry = ctk.CTkEntry(top_frame, placeholder_text=self._port)
        self.port_entry.insert(0, self._port)
        self.port_entry.grid(row=0, column=5, padx=5, pady=5, sticky="ew")

        # --- Auto Refresh ---
        ctk.CTkLabel(
            top_frame, 
            text="Refresh(s):",
            font=("Consolas", 15, "bold"),
            anchor="center",
            width=180
            ).grid(row=0, column=6, padx=5, pady=5, sticky="e")
        
        self.interval_entry = ctk.CTkEntry(top_frame, width=40)
        self.interval_entry.insert(0, "00")
        self.interval_entry.grid(row=0, column=7, padx=5, pady=5, sticky="ew")

        # --- Start / Stop Buttons ---
        self.start_btn = ctk.CTkButton(
            top_frame,
            text="Start",
            command=self.start_communication,
            fg_color="green"
        )
        self.start_btn.grid(row=0, column=8, padx=10, pady=5, sticky="ew")

        self.stop_btn = ctk.CTkButton(
            top_frame,
            text="Stop",
            command=self.stop_communication,
            fg_color="red",
            state="disabled"
        )
        self.stop_btn.grid(row=0, column=9, padx=5, pady=5, sticky="ew")


        # --- Register Section ---
        self.reg_frame = ctk.CTkFrame(self.tab_main)
        self.reg_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.reg_types = ["Coils", "Discrete Inputs", "Holding Registers", "Input Registers"]
        self.reg_entries = {}
        self.watch_vars = {}

        self.create_register_section()

        # --- Bottom Controls ---
        bottom_frame = ctk.CTkFrame(self.tab_main)
        bottom_frame.pack(side="bottom", fill="x", padx=10, pady=5)

        # --- Buttons for Client ---
        self.write_btn = ctk.CTkButton(bottom_frame, text="Write Values", width=120,  command=self.write_registers )
        self.refresh_btn = ctk.CTkButton(bottom_frame, text="Refresh Values", width=120, command=self.update_registers)
        
        # --- Buttons for Server ---
        self.write_to_server_btn = ctk.CTkButton(bottom_frame, text="Write To Server", width=120,  command=self.write_to_server )

        self.write_btn.pack(side="right", padx=20)
        self.refresh_btn.pack(side="right", padx=20)

        self.status_label = ctk.CTkLabel(bottom_frame, text="● Disconnected", text_color="red")
        self.status_label.pack(side="left", padx=10)

        # --- Log Tab ---
        self.log_text = ctk.CTkTextbox(self.tab_log, font=("Consolas", 14))
        self.log_text.pack(expand=True, fill="both", padx=10, pady=10)
        self.log("Ready.")

        
        # --- Container for vertical layout ---
        settings_main_frame = ctk.CTkFrame(self.tab_settings)
        settings_main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # --- Top Settings Register Section ---
        self.settings_reg_frame = ctk.CTkFrame(settings_main_frame)
        self.settings_reg_frame.pack(anchor="n", fill="x", pady=(5, 10))
        self.settings_reg_entries = {}
        self.settings_create_register_section()

        # --- Main Content ---
        settings_content_frame = ctk.CTkFrame(settings_main_frame)
        settings_content_frame.pack(expand=True, fill="both", pady=(5, 10))

        # --- Bottom Controls ---
        settings_bottom_frame = ctk.CTkFrame(settings_main_frame)
        settings_bottom_frame.pack(side="bottom", fill="x", pady=5)

        self.apply_btn = ctk.CTkButton(settings_bottom_frame, text="Apply Settings", command=self.apply_settings_to_registers)
        self.apply_btn.pack(side="left", padx=10)

        # Appearance mode dropdown (bottom right)
        self.appearance_mode = ctk.StringVar(value="Light")
        self.appearance_menu = ctk.CTkOptionMenu(
            settings_bottom_frame,
            variable=self.appearance_mode,
            values=["Light", "Dark"],
            width=100,
            command=self.change_appearance_mode
        )
        self.appearance_menu.pack(side="right", padx=(0, 10))

        theme_label = ctk.CTkLabel(settings_bottom_frame, text="Theme:")
        theme_label.pack(side="right", padx=(0, 5))

    def change_appearance_mode(self, mode):
        ctk.set_appearance_mode(mode.lower())
        self.log(f"Appearance changed to {mode} Mode")

    def apply_settings_to_registers(self):
        """Rebuild the register display (Main tab) using updated Settings values."""
        # Clear current register frame
        for widget in self.reg_frame.winfo_children():
            widget.destroy()

        # Recreate register section based on updated settings
        self.create_register_section()

        self.log("Settings applied to main register view.")


    def settings_create_register_section(self):
        """Create settings section for defining start addresses and ranges."""
        # --- Validation Functions (defined once at top of this function) ---
        def validate_start_addr(P):
            if P == "":
                return True  # allow clearing
            if P.isdigit():
                val = int(P)
                return 0 <= val <= 9999
            return False

        def validate_range(P):
            if P == "":
                return True
            if P.isdigit():
                val = int(P)
                return 1 <= val <= 10
            return False

        # Register these validation commands with tkinter
        validate_start_cmd = self.register(validate_start_addr)
        validate_range_cmd = self.register(validate_range)

        # --- Now create one column per register type ---
        for col, reg_type in enumerate(self.reg_types):
            frame = ctk.CTkFrame(self.settings_reg_frame)
            frame.grid(row=0, column=col, padx=10, pady=10, sticky="nsew")

            self.settings_reg_frame.grid_columnconfigure(col, weight=1)
            frame.grid_columnconfigure(0, weight=2)
            frame.grid_columnconfigure(1, weight=1)

            # Header label
            ctk.CTkLabel(
                frame,
                text=reg_type,
                font=("Consolas", 17, "bold"),
                anchor="center"
            ).grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="ew")

            self.settings_reg_entries[reg_type] = {}

            # Default values
            start_addr_default = 0
            range_default = 10

            # --- Start Address ---
            ctk.CTkLabel(frame, text="Start Address:", anchor="w").grid(row=1, column=0, padx=5, pady=5, sticky="ew")
            start_entry = ctk.CTkEntry(
                frame,
                width=80,
                validate="key",
                validatecommand=(validate_start_cmd, "%P")
            )
            start_entry.insert(0, str(start_addr_default))
            start_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
            self.settings_reg_entries[reg_type]["start_addr"] = start_entry

            # --- Range ---
            ctk.CTkLabel(frame, text="Range:", anchor="w").grid(row=2, column=0, padx=5, pady=5, sticky="ew")
            range_entry = ctk.CTkEntry(
                frame,
                width=80,
                validate="key",
                validatecommand=(validate_range_cmd, "%P")
            )
            range_entry.insert(0, str(range_default))
            range_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
            self.settings_reg_entries[reg_type]["addr_range"] = range_entry

    def create_register_section(self):
        """Create register rows in the main tab (uses settings for start and range)."""
        for col, reg_type in enumerate(self.reg_types):
            frame = ctk.CTkFrame(self.reg_frame)
            frame.grid(row=0, column=col, padx=10, pady=10, sticky="nsew")

            self.reg_frame.grid_columnconfigure(col, weight=1)
            frame.grid_columnconfigure(0, weight=2)
            frame.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                frame,
                text=reg_type,
                font=("Consolas", 17, "bold"),
                anchor="center"
            ).grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="ew")

            # Watch Switch
            self.watch_vars[reg_type] = ctk.BooleanVar(value=False)
            ctk.CTkSwitch(
                frame,
                text="Watch",
                variable=self.watch_vars[reg_type],
                font=("Consolas", 15),
                onvalue=True,
                offvalue=False,
                width=60,
                height=25,
                switch_width=30,
                switch_height=15,
            ).grid(row=1, column=0, columnspan=2, pady=(0, 10))

            # Read range and start address (default 0, 10)
            try:
                start_addr = int(self.settings_reg_entries[reg_type]["start_addr"].get())
                count = int(self.settings_reg_entries[reg_type]["addr_range"].get())
            except Exception:
                start_addr, count = 0, 10

            # Register rows
            entries = []
            for i in range(count):
                Reg_type_addr = self.complete_address(reg_type=reg_type, start=start_addr + i)
                ctk.CTkLabel(frame, text=f"{Reg_type_addr}:").grid(row=i + 2, column=0, padx=5, pady=2, sticky="ew")

                entry = ctk.CTkEntry(frame)
                entry.grid(row=i + 2, column=1, padx=5, pady=5, sticky="w")
                entries.append(entry)

            self.reg_entries[reg_type] = entries

        self.reg_frame.grid_rowconfigure(0, weight=1)

    
    def complete_address(self, reg_type, start):
        Reg_type_addr = 0
        match reg_type:
            case "Coils":
                Reg_type_addr = f"0{start}"
            
            case "Discrete Inputs":
                Reg_type_addr = 10000+start

            
            case "Holding Registers":
                Reg_type_addr = 40000+start

            case "Input Registers":
                Reg_type_addr = 30000+start
            case _:
                self.log("error : unknown value.")
        
        return Reg_type_addr

    def log(self, message):
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")

    def on_mode_change(self, mode):
        if mode == "Client":
            self.write_btn.pack(side="right", padx=10)
            self.refresh_btn.pack(side="right", padx=10)
            self.interval_entry.delete(0, "end")
            self.interval_entry.insert(0, "00")
            self.write_to_server_btn.pack_forget()
        else:
            self.auto_interval = 2
            self.interval_entry.delete(0, "end")
            self.interval_entry.insert(0, self.auto_interval)
            self.write_btn.pack_forget()
            self.refresh_btn.pack_forget()

            self.write_to_server_btn.pack(side="right", padx=20)

    def clear_all_entries(self):
        """Clear all register entry boxes (set to 0)."""
        for self.reg_type, entries in self.reg_entries.items(): 
            for entry in entries: 
                entry.delete(0, "end")


    def disable_or_enable_all_entries(self, in_state="disabled"):
        """Disable or enable all entry widgets stored in self.reg_entries."""
        print(in_state)
        if in_state == "enable":
            in_state = "normal"

        for self.reg_type, entries in self.reg_entries.items(): 
            for entry in entries: 
                entry.configure(state=in_state)


    def start_communication(self):
        ip = self.ip_entry.get().strip()
        port = int(self.port_entry.get().strip())
        mode = self.mode_var.get()

        try:
            self.auto_interval = float(self.interval_entry.get())
        except ValueError:
            self.auto_interval = 0

        if mode == "Client":
            self.start_client(ip=ip, port=port)
        else:
            self.start_server(ip=ip, port=port)

    def is_port_open(self, ip, port, timeout=2):
        """Server check if the port is open and server has started"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
            s.connect((ip, port))
            s.close()
            return True
        except (socket.error, ConnectionRefusedError):
            return False
        
    def start_client(self, ip, port):
            self.client = ModbusTcpClient(ip, port=port)
            if self.client.connect():
                self.disable_or_enable_all_entries("normal")
                self.start_btn.configure(state="disabled")
                self.stop_btn.configure(state="normal")
                self.is_running = True
                self.log(f"Connected as Client to {ip}:{port}")
                self.status_label.configure(text="● Connected", text_color="green")
                if self.auto_interval > 0:
                    self.after(int(self.auto_interval * 1000), self.update_registers)
            else:
                self.status_label.configure(text="● Failed", text_color="red")
                self.log("Failed to connect to Modbus server, Please check the IP address.")
                self.mode_menu.configure(state="normal")

    def start_server(self, ip, port):
        self.log(f"Starting Modbus Server on {ip}:{port}")
        store = ModbusSlaveContext(
            di=ModbusSequentialDataBlock(0, [0]*100),
            co=ModbusSequentialDataBlock(0, [0]*100),
            hr=ModbusSequentialDataBlock(0, [0]*100),
            ir=ModbusSequentialDataBlock(0, [0]*100),
        )
        self.context = ModbusServerContext(slaves=store, single=True)
        self.server_thread = threading.Thread(
            target=StartTcpServer,
            kwargs={"context": self.context, "address": (ip, port)},
            daemon=True
        )
        self.server_thread.start()
        # Wait briefly for the server to initialize
        time.sleep(1)
        if self.is_port_open(ip=ip, port=port):
            self.disable_or_enable_all_entries("normal")
            self.status_label.configure(text="● Server Running", text_color="green")
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.log(f"Server running at {ip}:{port}")

            self.mode_menu.configure(state="disabled")

            self._update_server_values_loop()
        else:
            self.mode_menu.configure(state="normal") 
            self.status_label.configure(text="● Server Failed", text_color="red")
            self.log(f"Failed to start Modbus Server on {ip}:{port}, Please check the IP address.")

    def stop_communication(self):
        self.is_running = False
        if self.client:
            self.client.close()
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text="● Disconnected", text_color="red")

        self.mode_menu.configure(state="normal")

        self.clear_all_entries()
        self.disable_or_enable_all_entries()
        self.log("Communication stopped.")

    def write_to_server(self):
        """Write data from GUI entries to the Modbus server context based on enabled watch switches."""
        try:
            if not hasattr(self, "context") or self.context is None:
                self.log("Server context not initialized.")
                return

            # Iterate over each register type
            for reg_type in self.reg_types:
                # Skip if switch is OFF
                if not self.watch_vars[reg_type].get():
                    continue

                # --- Get start address and range from Settings tab ---
                try:
                    start_addr = int(self.settings_reg_entries[reg_type]["start_addr"].get())
                    count = int(self.settings_reg_entries[reg_type]["addr_range"].get())
                except ValueError:
                    self.log(f"Invalid address range for {reg_type}. Skipping.")
                    continue

                # --- Get values from GUI entry boxes ---
                try:
                    values = []
                    for entry in self.reg_entries[reg_type][:count]:
                        val_str = entry.get().strip()
                        # Handle bool for coils and discrete
                        if reg_type in ["Coils", "Discrete Inputs"]:
                            val = 1 if val_str.lower() in ["1", "true", "on"] else 0
                        else:
                            val = int(val_str) if val_str.isdigit() else 0
                        values.append(val)
                except Exception as e:
                    self.log(f"Error reading GUI values for {reg_type}: {e}")
                    continue

                # --- Write to Modbus server memory ---
                try:
                    slave_id = 0  # default single slave
                    if reg_type == "Coils":
                        self.context[slave_id].setValues(1, start_addr, values)
                    elif reg_type == "Discrete Inputs":
                        self.context[slave_id].setValues(2, start_addr, values)
                    elif reg_type == "Holding Registers":
                        self.context[slave_id].setValues(3, start_addr, values)
                    elif reg_type == "Input Registers":
                        self.context[slave_id].setValues(4, start_addr, values)

                    self.log(f"Wrote {len(values)} values to {reg_type} starting at {start_addr}")

                except Exception as e:
                    self.log(f"Error writing {reg_type} to server: {e}")

            self.log("Write to server completed successfully.")

        except Exception as e:
            self.log(f"Error in write_to_server: {e}")


    def update_registers(self):
        if not self.is_running or not self.client:
            return
        
        try:
            for reg_type in self.reg_types:
                if not self.watch_vars[reg_type].get():
                    print(self.watch_vars[reg_type].get())
                    continue
                    
                if reg_type == "Holding Registers":
                    rr = self.client.read_holding_registers(address=0, count=10)
                    if not rr.isError():
                        for i, val in enumerate(rr.registers):
                            print(f"i : {i} || val {val}")
                            self.reg_entries[reg_type][i].delete(0, "end")
                            self.reg_entries[reg_type][i].insert(0, str(val))

                if reg_type == "Input Registers":
                    rr = self.client.read_input_registers(address=0, count=10)
                    if not rr.isError():
                        for i, val in enumerate(rr.registers):
                            self.reg_entries[reg_type][i].delete(0, "end")
                            self.reg_entries[reg_type][i].insert(0, str(val))

                if reg_type == "Coils":
                    rr = self.client.read_coils(address=0, count=10)
                    print(len(rr.bits))
                    print(rr.bits)
                    if not rr.isError():
                        bits = rr.bits[:10]
                        for i, val in enumerate(bits):
                            self.reg_entries[reg_type][i].delete(0, "end")
                            self.reg_entries[reg_type][i].insert(0, bool(val))

                if reg_type == "Discrete Inputs":
                    rr = self.client.read_discrete_inputs(address=0, count=10)
                    if not rr.isError():
                        bits = rr.bits[:10]
                        for i, val in enumerate(bits):
                            self.reg_entries[reg_type][i].delete(0, "end")
                            self.reg_entries[reg_type][i].insert(0, bool(val))

            self.log("Registers refreshed.")

        except Exception as e:
            print("Error Occured")
            self.log(f"Error: {e}")

        # Auto refresh if interval > 0
        if self.auto_interval > 0 and self.is_running:
            self.after(int(self.auto_interval * 1000), self.update_registers)

    def write_registers(self):
        if not self.client:
            self.log("Client not connected.")
            return

        try:
            for reg_type in self.reg_types:
                if not self.watch_vars[reg_type].get():
                    continue

                values = [int(e.get()) for e in self.reg_entries[reg_type]]
                if reg_type == "Holding Registers":
                    print(f"Value : {values}")
                    self.client.write_registers(0, values)
                elif reg_type == "Coils":
                    self.client.write_coils(0, [bool(v) for v in values])

            self.log("Registers written successfully.")

        except Exception as e:
            self.log(f"Error writing registers: {e}")

    def _update_server_values_loop(self):
        if hasattr(self, "context") and self.context is not None:
            try:
                # Read holding registers
                hr = self.context[0].getValues(3, self.start_addr_holding, count=10)
                ir = self.context[0].getValues(4, self.start_addr_input, count=10)
                co = self.context[0].getValues(1, self.start_addr_coils, count=10)
                di = self.context[0].getValues(2, self.start_addr_Dis_input, count=10)

                if  not self._switch_disable_check("Holding Registers"):
                    self._update_entries("Holding Registers", hr)
                if  not self._switch_disable_check("Input Registers"):
                    self._update_entries("Input Registers", ir)
                if  not self._switch_disable_check("Coils"):
                    self._update_entries("Coils", co)
                if  not self._switch_disable_check("Discrete Inputs"):
                    self._update_entries("Discrete Inputs", di)

            except Exception as e:
                self.log(f"Error updating UI: {e}")

        # Schedule next update in 1000ms (1 second)
        self.after((int(self.auto_interval*1000)), self._update_server_values_loop)

    def _switch_disable_check(self, reg_type_check):
        for reg_type in self.reg_types:
            if not self.watch_vars[reg_type].get():
                continue

            if  reg_type == reg_type_check:
                return True
            return False 

    def _update_entries(self, reg_type, values):
        if reg_type not in self.reg_entries:
            return
        for i, val in enumerate(values[:len(self.reg_entries[reg_type])]):
            entry = self.reg_entries[reg_type][i]
            entry.delete(0, "end")
            entry.insert(0, str(val))

if __name__ == "__main__":
    app = ModbusTesterApp()
    app.mainloop()
