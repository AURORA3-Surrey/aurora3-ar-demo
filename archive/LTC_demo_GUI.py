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

ip = "127.0.0.1"
ports = [9093, 9093]
tracker_port = [9000]

button1 = tk.Button(
    root,
    text="Stop",
    command=lambda: [send_osc_message(ip, port, "/pyBinSimStopAllPlayers") for port in ports]
)
button1.grid(row=0, column=0, padx=10, pady=10)

button2 = tk.Button(
    root,
    text="Dry signal 1",
    command=lambda: [send_osc_message(ip, port, "/pyBinSimFile", 'path/SherlockHolmesCUT48kHz_mono.wav') for port in ports]
)
button2.grid(row=1, column=0, padx=10, pady=10)

button3 = tk.Button(
    root,
    text="Dry signal 2",
    command=lambda: [send_osc_message(ip, port, "/pyBinSimFile", 'path/Sax48_mono.wav') for port in ports]
)
button3.grid(row=1, column=1, padx=10, pady=10)

button4 = tk.Button(
    root,
    text="Loudspeaker 1",
    command=lambda: [send_osc_message(ip, port, "/src_idx", "0") for port in tracker_port]
) 
button4.grid(row=2, column=0, padx=10, pady=10)

button5 = tk.Button(
    root,
    text="Loudspeaker 2",
    command=lambda: [send_osc_message(ip, port, "/src_idx", "1") for port in tracker_port]
)
button5.grid(row=2, column=1, padx=10, pady=10)

button6a = tk.Button(
    root,
    text="Low reverberation time",
    command=lambda: [send_osc_message(ip, port, "/reverb_time_idx", "0") for port in tracker_port]
)
button6a.grid(row=3, column=0, padx=10, pady=10)

button6b = tk.Button(
    root,
    text="High reverberation time",
    command=lambda: [send_osc_message(ip, port, "/reverb_time_idx", "1") for port in tracker_port]
)
button6b.grid(row=3, column=1, padx=10, pady=10)

button7a = tk.Button(
    root,
    text="Volume low",
    command=lambda: [send_osc_message(ip, port, "/pyBinSimLoudness", '2') for port in ports]
)
button7a.grid(row=4, column=0, padx=10, pady=10)

button7b = tk.Button(
    root,
    text="Volume mid",
    command=lambda: [send_osc_message(ip, port, "/pyBinSimLoudness", '4') for port in ports]
)
button7b.grid(row=4, column=1, padx=10, pady=10)

button7c = tk.Button(
    root,
    text="Volume high",
    command=lambda: [send_osc_message(ip, port, "/pyBinSimLoudness", '6') for port in ports]
)
button7c.grid(row=4, column=2, padx=10, pady=10)

button8a = tk.Button(
    root,
    text="Headphone playback",
    command=lambda: [send_osc_message(ip, port, "/reverb_time_idx", "0") for port in tracker_port]
)
button8a.grid(row=5, column=0, padx=10, pady=10)

button8b = tk.Button(
    root,
    text="Loudspeaker playback",
    command=lambda: [send_osc_message(ip, port, "/reverb_time_idx", "1") for port in tracker_port]
)
button8b.grid(row=5, column=1, padx=10, pady=10)


root.mainloop()