import subprocess
import time
import os
import csv

def check_dependencies():
    required_commands = {
        "sudo": ["sudo", "-V"],  # Check sudo version
        "airodump-ng": ["airodump-ng", "--help"],
        "iw": ["iw", "help"],
        "ip": ["ip", "help"]
    }
    missing_commands = []
    for cmd, check_cmd in required_commands.items():
        try:
            # Use shell=True for commands that might be shell built-ins or require shell features
            # For simple command existence, it's generally safer to avoid shell=True
            # but for --help or help, it's usually fine.
            subprocess.run(check_cmd, capture_output=True, check=True, text=True)
        except FileNotFoundError:
            missing_commands.append(cmd)
        except subprocess.CalledProcessError as e:
            # Command exists but returned an error, might be a bad --help flag or permission issue
            # For now, we'll assume it's found if it didn't raise FileNotFoundError
            # print(f"Warning: Command '{cmd}' exists but returned an error during check: {e.stderr.strip()}")
            pass # Command is found, just might have weird help output
        except Exception as e:
            print(f"An unexpected error occurred while checking for '{cmd}': {e}")
            missing_commands.append(cmd)

    if missing_commands:
        print(f"Error: The following required commands are not found or not working correctly: {', '.join(missing_commands)}.")
        print("Please install them and ensure they are in your system's PATH.")
        return False
    return True

def enable_monitor_mode(interface, sudo_password):
    print(f"Enabling monitor mode on {interface}...")
    try:
        # Bring down the interface
        command_down = ["sudo", "-S", "ip", "link", "set", interface, "down"]
        process_down = subprocess.Popen(command_down, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout_down, stderr_down = process_down.communicate(input=sudo_password + '\n')
        if process_down.returncode != 0:
            print(f"Error bringing down interface: {stderr_down}")
            return False

        # Enable monitor mode
        command_mode = ["sudo", "-S", "iw", "dev", interface, "set", "type", "monitor"]
        process_mode = subprocess.Popen(command_mode, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout_mode, stderr_mode = process_mode.communicate(input=sudo_password + '\n')
        if process_mode.returncode != 0:
            print(f"Error setting monitor mode: {stderr_mode}")
            return False

        # Bring up the interface
        command_up = ["sudo", "-S", "ip", "link", "set", interface, "up"]
        process_up = subprocess.Popen(command_up, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout_up, stderr_up = process_up.communicate(input=sudo_password + '\n')
        if process_up.returncode != 0:
            print(f"Error bringing up interface: {stderr_up}")
            return False

        print(f"Monitor mode enabled on {interface}")
        return True
    except FileNotFoundError:
        print("Error: 'ip' or 'iw' command not found. Make sure they are installed and in your PATH.")
        return False
    except Exception as e:
        print(f"An error occurred while enabling monitor mode: {e}")
        return False

def disable_monitor_mode(interface, sudo_password):
    print(f"Disabling monitor mode on {interface}...")
    try:
        # Bring down the interface
        command_down = ["sudo", "-S", "ip", "link", "set", interface, "down"]
        process_down = subprocess.Popen(command_down, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout_down, stderr_down = process_down.communicate(input=sudo_password + '\n')
        if process_down.returncode != 0:
            print(f"Error bringing down interface: {stderr_down}")
            return False

        # Set interface type back to managed
        command_mode = ["sudo", "-S", "iw", "dev", interface, "set", "type", "managed"]
        process_mode = subprocess.Popen(command_mode, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout_mode, stderr_mode = process_mode.communicate(input=sudo_password + '\n')
        if process_mode.returncode != 0:
            print(f"Error setting managed mode: {stderr_mode}")
            return False

        # Bring up the interface
        command_up = ["sudo", "-S", "ip", "link", "set", interface, "up"]
        process_up = subprocess.Popen(command_up, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout_up, stderr_up = process_up.communicate(input=sudo_password + '\n')
        if process_up.returncode != 0:
            print(f"Error bringing up interface: {stderr_up}")
            return False

        print(f"Monitor mode disabled on {interface}")
        return True
    except FileNotFoundError:
        print("Error: 'ip' or 'iw' command not found. Make sure they are installed and in your PATH.")
        return False
    except Exception as e:
        print(f"An error occurred while disabling monitor mode: {e}")
        return False

def scan_for_hidden_networks(interface, sudo_password, scan_time=15):
    print(f"Scanning for hidden networks on {interface} for {scan_time} seconds...")
    hidden_networks = []
    temp_filename = f"airodump-output-{int(time.time())}"
    csv_filename = f"{temp_filename}-01.csv"

    try:
        # Start airodump-ng to write to a CSV file
        command = ["sudo", "-S", "airodump-ng", "--write", temp_filename, "--output-format", "csv", interface]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
        process.stdin.write(sudo_password + '\n')
        process.stdin.flush()

        start_time = time.time()
        while time.time() - start_time < scan_time:
            if os.path.exists(csv_filename):
                with open(csv_filename, 'r') as f:
                    reader = csv.reader(f)
                    # Skip to the AP section
                    ap_section = False
                    current_networks = []
                    for row in reader:
                        if len(row) > 0 and row[0].strip() == "BSSID": # Start of AP section
                            ap_section = True
                            continue
                        if ap_section and len(row) > 13: # Ensure enough columns for ESSID
                            bssid = row[0].strip()
                            channel = row[3].strip()
                            essid = row[13].strip() # ESSID is typically the last column

                            # airodump-ng sometimes shows empty ESSID or '<length: #>' for hidden networks
                            if not essid or essid.startswith("<length:") or essid == "":
                                essid = "<hidden>"
                            current_networks.append({"bssid": bssid, "essid": essid, "channel": channel})
                # Update hidden_networks with the latest scan results
                # This handles cases where ESSIDs might become visible over time
                for new_net in current_networks:
                    found = False
                    for existing_net in hidden_networks:
                        if existing_net['bssid'] == new_net['bssid']:
                            # Update ESSID if it was hidden and now found
                            if existing_net['essid'] == "<hidden>" and new_net['essid'] != "<hidden>":
                                existing_net['essid'] = new_net['essid']
                            found = True
                            break
                    if not found:
                        hidden_networks.append(new_net)

            time.sleep(1) # Check CSV every second

        # Terminate airodump-ng
        process.terminate()
        process.wait()

    except FileNotFoundError:
        print("Error: 'airodump-ng' command not found. Make sure it's installed and in your PATH.")
    except Exception as e:
        print(f"An error occurred during hidden network scan: {e}")
    finally:
        # Clean up temporary files
        for ext in [".cap", ".csv", ".kismet.csv", ".kismet.netxml"]:
            if os.path.exists(temp_filename + ext):
                os.remove(temp_filename + ext)
            if os.path.exists(csv_filename):
                os.remove(csv_filename)
        return hidden_networks

if __name__ == "__main__":
    if not check_dependencies():
        exit()

    # This part is for testing the functions independently
    test_interface = "wlan0" # Replace with your wireless interface
    test_sudo_password = input("Enter your sudo password for testing: ")

    if enable_monitor_mode(test_interface, test_sudo_password):
        print("Waiting for 5 seconds before scanning...")
        time.sleep(5)
        found_networks = scan_for_hidden_networks(test_interface, test_sudo_password, scan_time=20) # Increased scan time for better results
        print("\nFound Networks:")
        if found_networks:
            for net in found_networks:
                print(f"  BSSID: {net['bssid']}, ESSID: {net['essid']}, Channel: {net['channel']}")
        else:
            print("  No networks found or error during scan.")
        
        print("Waiting for 5 seconds before disabling monitor mode...")
        time.sleep(5)
        disable_monitor_mode(test_interface, test_sudo_password)
    else:
        print("Failed to enable monitor mode. Cannot proceed with scan.")
