#!/bin/python3
# Florin Idita
import re
import sys

def process_log_file(log_file_path):
    try:
        with open(log_file_path, 'r') as file:
            for log_line in file:
                if "NVRM: Xid (PCI:" in log_line and ": 74," in log_line:
                    print("Relevant line:", log_line.strip())

                    # Extract PCI bus
                    pci_bus_match = re.search(r"PCI:([0-9a-fA-F:]+)", log_line)
                    if pci_bus_match:
                        pci_bus = pci_bus_match.group(1)
                        print("PCI bus:", pci_bus)

                    # Extract link
                    link_match = re.search(r"link (\d+)\(", log_line)
                    if link_match:
                        link = link_match.group(1)
                        print("Link:", link)

                    # Extract hex code
                    hex_match = re.search(r"\(0x[0-9a-fA-F]+", log_line)
                    if hex_match:
                        hex_value = hex_match.group(0)[1:]  # Remove the opening parenthesis
                        print("Hex code:", hex_value)

                        # Convert to binary
                        decimal_value = int(hex_value, 16)
                        binary_value = bin(decimal_value)[2:].zfill(32)

                        # Print binary code in groups of 4 digits
                        grouped_binary = ' '.join(binary_value[i:i+4] for i in range(0, 32, 4))
                        print("Binary code:", grouped_binary)

                        # Analyze binary code
                        analyze_binary(binary_value, link)

                    # Found the first relevant line, exit
                    break

    except FileNotFoundError:
        print(f"Error: File {log_file_path} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def analyze_binary(binary_code, link):
    print("Analyzing binary code...")

    any_bit_set = False
    set_bits = []

    # Bits 4 and 5 (counting from LSB)
    bits_to_check = [4, 5]
    for bit_index in bits_to_check:
        if binary_code[31-bit_index] == '1':
            print(f"  Link {link}: Likely HW issue with ECC/Parity. If seen more than 2 times on the same link, report a bug. Bit {bit_index} is set.")
            any_bit_set = True

    # Bits 21 and 22
    bits_to_check = [21, 22]
    for bit_index in bits_to_check:
        if binary_code[31-bit_index] == '1':
            print(f"  Link {link}: Marginal channel SI issue. Check link mechanical connections. If other errors accompany, follow the resolution for those. Bit {bit_index} is set.")
            any_bit_set = True

    # Bits 8, 9, 12, 16, 17, 24, 28
    bits_to_check = [8, 9, 12, 16, 17, 24, 28]
    for bit_index in bits_to_check:
        if binary_code[31-bit_index] == '1':
            print(f"  Link {link}: Could possibly be a HW issue; Check link mechanical connections and re-seat if a field resolution is required. Run diags if issue persists. Bit {bit_index} is set.")
            any_bit_set = True

    # Check all bits and record those that are set
    for i, bit in enumerate(binary_code):
        if bit == '1':
            set_bits.append(31 - i) #calculate bit number from index.

    if not any_bit_set:
        if set_bits:
            print(f"  Link {link}: No specific error bits were set. Set bits: {set_bits}")
        else:
            print(f" Link {link}: No bits were set.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <log_file_path>")
    else:
        log_file_path = sys.argv[1]
        process_log_file(log_file_path)
