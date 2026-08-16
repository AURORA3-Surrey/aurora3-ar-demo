"""
A GUI for controlling the AURORA3 AR demo.

"""

import tkinter as tk
from pythonosc.udp_client import SimpleUDPClient

def send_osc_message(ip, port, address, *args):
    try:
        client = SimpleUDPClient(ip, port)
        client.send_message(address, args)
        print(f"Message sent to {ip}:{port} - {address} {args}")
    except Exception as e:
        print(f"Failed to send message to {ip}:{port} - {e}")

root = tk.Tk()
root.title("AURORA3 AR demo controller")
root.geometry("750x300")
root.config(padx=15, pady=15)
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)

ip = "127.0.0.1"
ports = [9093, 9093]
tracker_port = [9000]

# Master
master_frame = tk.LabelFrame(root, text="Main", font=("Arial", 10, "bold"), padx=10, pady=10)
master_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

# 2. Audio Source
source_frame = tk.LabelFrame(root, text="Dry signal", font=("Arial", 10, "bold"), padx=10, pady=10)
source_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
source_frame.columnconfigure(0, weight=1)
source_frame.columnconfigure(1, weight=1)

# 3. Loudspeaker
spatial_frame = tk.LabelFrame(root, text="Loudspeaker", font=("Arial", 10, "bold"), padx=10, pady=10)
spatial_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
spatial_frame.columnconfigure(0, weight=1)
spatial_frame.columnconfigure(1, weight=1)

# 4. Acoustics Environment
acoustics_frame = tk.LabelFrame(root, text="Reverberation time", font=("Arial", 10, "bold"), padx=10, pady=10)
acoustics_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
acoustics_frame.columnconfigure(0, weight=1)
acoustics_frame.columnconfigure(1, weight=1)

# 5. Playback Routing
playback_frame = tk.LabelFrame(root, text="Playback  device", font=("Arial", 10, "bold"), padx=10, pady=10)
playback_frame.grid(row=2, column=1, sticky="nsew", padx=10, pady=10)
playback_frame.columnconfigure(0, weight=1)
playback_frame.columnconfigure(1, weight=1)

# Master
button1 = tk.Button(
    master_frame,
    text="Stop",
    width=15,
    command=lambda: [send_osc_message(ip, port, "/pyBinSimStopAllPlayers") for port in ports]
)
button1.grid(row=0, column=0, padx=(5, 30), pady=5)

tk.Label(master_frame, text="Volume:").grid(row=0, column=1, padx=(10, 5), pady=5)

button7a = tk.Button(
    master_frame,
    text="Low",
    width=10,
    command=lambda: [send_osc_message(ip, port, "/pyBinSimLoudness", '2') for port in ports]
)
button7a.grid(row=0, column=2, padx=5, pady=5)

button7b = tk.Button(
    master_frame,
    text="Mid",
    width=10,
    command=lambda: [send_osc_message(ip, port, "/pyBinSimLoudness", '4') for port in ports]
)
button7b.grid(row=0, column=3, padx=5, pady=5)

button7c = tk.Button(
    master_frame,
    text="High",
    width=10,
    command=lambda: [send_osc_message(ip, port, "/pyBinSimLoudness", '6') for port in ports]
)
button7c.grid(row=0, column=4, padx=5, pady=5)

# Dry signal used
button2 = tk.Button(
    source_frame,
    text="Dry signal 1",
    command=lambda: [send_osc_message(ip, port, "/pyBinSimFile", 'path/SherlockHolmesCUT48kHz_mono.wav') for port in ports]
)
button2.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

button3 = tk.Button(
    source_frame,
    text="Dry signal 2",
    command=lambda: [send_osc_message(ip, port, "/pyBinSimFile", 'path/Sax48_mono.wav') for port in ports]
)
button3.grid(row=0, column=1, padx=5, pady=5, sticky="ew")


# Select loudspeaker
button4 = tk.Button(
    spatial_frame,
    text="Loudspeaker 1",
    command=lambda: [send_osc_message(ip, port, "/src_idx", "0") for port in tracker_port]
)
button4.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

button5 = tk.Button(
    spatial_frame,
    text="Loudspeaker 2",
    command=lambda: [send_osc_message(ip, port, "/src_idx", "1") for port in tracker_port]
)
button5.grid(row=0, column=1, padx=5, pady=5, sticky="ew")


# Reverberation time
button6a = tk.Button(
    acoustics_frame,
    text="Low reverb",
    command=lambda: [send_osc_message(ip, port, "/reverb_time_idx", "0") for port in tracker_port]
)
button6a.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

button6b = tk.Button(
    acoustics_frame,
    text="High reverb",
    command=lambda: [send_osc_message(ip, port, "/reverb_time_idx", "1") for port in tracker_port]
)
button6b.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

# Playback routing
button8a = tk.Button(
    playback_frame,
    text="Headphones",
    command=lambda: [send_osc_message(ip, port, "/reverb_time_idx", "0") for port in tracker_port]
)
button8a.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

button8b = tk.Button(
    playback_frame,
    text="Loudspeakers",
    command=lambda: [send_osc_message(ip, port, "/reverb_time_idx", "1") for port in tracker_port]
)
button8b.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

root.mainloop()