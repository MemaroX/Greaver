# Gui_reaver

This project provides two Python scripts for wireless network auditing:

1.  `main.py`: A graphical user interface (GUI) for the `reaver` tool, used for WPS attacks.
2.  `hidden_network_scanner.py`: A script to scan for hidden Wi-Fi networks.

## Dependencies

Before running these scripts, you need to install the following tools:

*   `python`
*   `python-tk` (for the GUI)
*   `reaver`
*   `airodump-ng` (from the `aircrack-ng` suite)
*   `iw`
*   `ip` (from `iproute2`)
*   `iwlist` (from `wireless-tools`)

On Arch Linux, you can install these using:

```bash
sudo pacman -Syu python python-tk reaver aircrack-ng iw iproute2 wireless-tools
```

## Running the GUI for Reaver (`main.py`)

1.  **Run the script:**
    ```bash
    python3 main.py
    ```
2.  **Enter your sudo password** in the "Sudo Password" field.
3.  **Select your wireless interface** from the dropdown menu.
4.  **Click "Scan for Networks"** to see a list of available Wi-Fi networks.
5.  **Select a network** from the list to populate the BSSID, ESSID, and Channel fields.
6.  **Click "Start Reaver"** to begin the WPS attack.
7.  **Click "Stop Reaver"** to terminate the attack.

## Scanning for Hidden Networks (`hidden_network_scanner.py`)

1.  **Make executable:**
    ```bash
    chmod +x hidden_network_scanner.py
    ```
2.  **Run with sudo:**
    ```bash
    sudo python3 hidden_network_scanner.py
    ```
3.  **Enter your sudo password** when prompted.
4.  The script will scan for hidden networks and print them to the console.

**Note:** You may need to edit the `test_interface` variable in `hidden_network_scanner.py` to match your wireless interface name (e.g., `wlan0`, `wlan1`).
