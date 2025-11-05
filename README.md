# ⚙️ Modbus TCP/IP Tester

A modern **Python GUI application** built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) and [pymodbus](https://github.com/pymodbus-dev/pymodbus) to easily test, simulate, and debug Modbus TCP/IP communication.  
This tool can act as both **Client** and **Server**, making it ideal for development, debugging, and educational use.

![Image Alt](https://github.com/Pankaj-s-dev/Modbus_TCP_IP_Tester/blob/fcaf2dd390e9fccff165ccb1cd65ebfb9df35a90/images/server_running.png)

---

## 🧩 Features

- ✅ Run in **Client** mode to connect to remote Modbus TCP/IP servers.
- ✅ Run in **Server** mode to simulate a local Modbus server.
- ✅ Supports all major Modbus data types:
  - Coils (Digital Outputs)
  - Discrete Inputs (Digital Inputs)
  - Holding Registers (Read/Write)
  - Input Registers (Read-only)
- ✅ Per-register “Watch” switch — auto-refresh data when enabled.
- ✅ Fully configurable start address & range (via **Settings** tab).
- ✅ Input validation with smart auto-adjust of ranges.
- ✅ Live activity and error logging with adjustable font size.
- ✅ Responsive layout — UI adapts evenly to any window size.
- ✅ Clean, dark/light mode toggle.

---

## 🛠️ Installation

### 1️ Clone this repository
```bash
git clone https://github.com/Pankaj-s-dev/Modbus_TCP_IP_Tester.git
cd Modbus_TCP_IP_Tester
```

### 2️ (Optional but recommended) Create a virtual environment
```bash
python -m venv .venv
# Activate the environment
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate
```

### 3️ Install dependencies
```bash
pip install -r requirements.txt
```

**Example `requirements.txt`:**
```
customtkinter
pymodbus
```

### 4️ Run the application
```bash
python Modbus_TCP_IP_Tester.py
```

---

## 🖥️ How to Use

### **Main Tab**
This is where you interact with Modbus registers.

- **Mode**: Select between `Client` or `Server`.
- **IP Address / Port**:  
  - Client Mode → IP of remote server.  
  - Server Mode → IP/Port to host your local Modbus server.
- **Refresh(s)**: Set auto-refresh interval in seconds (`0` = manual only).
- **Start / Stop**:  
  - `Start` initiates communication.  
  - Once running, the Mode dropdown is disabled.
  - `Stop` halts communication and re-enables the Mode selector.

---

### **Register Section**
Displays the four Modbus register categories side by side:
- **Coils**
- **Discrete Inputs**
- **Holding Registers**
- **Input Registers**

Each section includes:
- A **Watch** toggle to auto-refresh that group.
- Ten editable register boxes (addresses shown on the left).

**Buttons (bottom of Main tab):**
- `Write Values` → Write to remote server (Client mode).
- `Refresh Values` → Manually read from remote server.
- `Write To Server` → Push GUI data into local server (Server mode).

---

### **Settings Tab**

Configure the address ranges per register type:
- **Start Address:** 0–9999
- **Range:** 1–10
- Press **Apply Settings** to rebuild the main register grid.

Each setting is validated live while you type.

---

### **Log Tab**
Displays real-time communication logs and system events with a readable 14pt font.  
Used to verify data transfer, connections, and internal actions.

---

## 📸  Screenshots


| Section |  Image |
|----------|--------------------------------|
| Main Tab |![Image Alt](https://github.com/Pankaj-s-dev/Modbus_TCP_IP_Tester/blob/fcaf2dd390e9fccff165ccb1cd65ebfb9df35a90/images/main_tab.png)|
| Settings Tab |![Image Alt](https://github.com/Pankaj-s-dev/Modbus_TCP_IP_Tester/blob/fcaf2dd390e9fccff165ccb1cd65ebfb9df35a90/images/settings_tab.png)|
| Log Tab |![Image Alt](https://github.com/Pankaj-s-dev/Modbus_TCP_IP_Tester/blob/fcaf2dd390e9fccff165ccb1cd65ebfb9df35a90/images/log_tab.png)|
| Server Running | ![Image Alt](https://github.com/Pankaj-s-dev/Modbus_TCP_IP_Tester/blob/fcaf2dd390e9fccff165ccb1cd65ebfb9df35a90/images/server_running.png)|
| Client Connected | ![Image Alt](https://github.com/Pankaj-s-dev/Modbus_TCP_IP_Tester/blob/fcaf2dd390e9fccff165ccb1cd65ebfb9df35a90/images/client_connected.png)|

---

## ⚡ Internals

- **UI:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)  
  - Grid layout with equal weights for consistent resizing.
  - Uses `CTkOptionMenu`, `CTkEntry`, `CTkSwitch`, and `CTkTextbox`.
- **Backend:** [pymodbus](https://pymodbus.readthedocs.io/)
  - Client: `ModbusTcpClient`
  - Server: `StartTcpServer`, `ModbusServerContext`, and `ModbusSequentialDataBlock`.
- **Addresses:**  
  - Coils → `00000`  
  - Discrete Inputs → `10000`  
  - Input Registers → `30000`  
  - Holding Registers → `40000`

---

## 🧠 Tips & Troubleshooting

- For local testing, use IP: `127.0.0.1` or your local IP.
- Use a port above 1024 if you see permission errors.
- “Watch” only the registers you want to poll — fewer reads = faster refresh.
- If you modify Settings, hit **Apply Settings** to update the main view.

---

## 💡 Future Roadmap / Discussion

I’m planning to expand this project and would love community input!

### Potential upcoming features:
- 🧰 Save/load configuration profiles.
- 📦 Export register data to CSV.
- 🔌 Add Modbus RTU-over-TCP bridge mode.
- 🧪 Integrate testing suite for Modbus transactions.
- 🖼️ Improved dark/light themes with more color options.

### Open to collaboration:
Start a discussion or issue:
- “Feature: Add CSV export”
- “Discussion: New layout ideas”
- “Bug: Server doesn’t refresh after stop/start”

---

## 🤝 Contributing

Pull requests are welcome!  
To contribute:

1. Fork the repo.
2. Create your feature branch (`git checkout -b feature/my-feature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/my-feature`).
5. Open a Pull Request.

Please include screenshots if your change affects the GUI.

---

## 🧾 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Pankaj Sharma**  
Embedded Systems & Automation Engineer  
If you have questions, suggestions, or collaboration ideas:  
- Connect on [LinkedIn](https://www.linkedin.com/in/pankaj-k-sharma/)  
- Or open a discussion in the [Issues](../../issues) tab  

---

> _If you find this project useful, please ⭐ star it on GitHub — it helps others discover it!_
