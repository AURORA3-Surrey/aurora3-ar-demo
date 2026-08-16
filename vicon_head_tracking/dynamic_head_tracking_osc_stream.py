"""
Streams real-time head-tracking data from a Vicon motion capture system
to a different application via OSC.

Variables:
    osc_ip (str): The destination IP address for the OSC messages.
    receiver_port (int): The destination network port for the OSC messages.
    vicon_ip (str): The network address and port of the Vicon software broadcasting data.
    vicon_subject (str): The name of the overall tracked subject/object ie the rigid body, exactly
        as it is configured in the Vicon software ("head_tracker" here).
    vicon_segment (str): The specific rigid body or individual segment on that subject
        to track (single rigid body/segment here, both named "head_tracker").
    osc_client (SimpleUDPClient): Handles sending the OSC messages over the network.
    vicon_client (ViconDataStream.Client): Handles receiving the data from Vicon.
    position_data (tuple): Raw Vicon translation data ([x, y, z] in mm, occlusion flag).
    orientation_data (tuple): Raw Vicon rotation data (in radians).
    markers_occluded (bool): Flag indicating if the cameras cannot see the markers.
    head_position (list): The tracked [x, y, z] position in mm.
    head_orientation_* (float): The yaw, pitch, and roll angles in degrees.

Variables sent via OSC:
    /head_position (list of floats): Sends the position in millimeters in the x, y, and z axes.
    /head_orientation (list of floats): Sends the yaw, pitch, roll orientation in degrees.
"""

from vicon_dssdk import ViconDataStream
from pythonosc import udp_client
import numpy as np
import time

# Vicon and OSC setup
osc_ip = "127.0.0.1"
receiver_port = 9000
vicon_ip = "localhost:801" # Vicon and OSC streaming on the same machine
vicon_subject = "head_tracker"  # The rigid body name setup in Vicon
vicon_segment = "head_tracker" # Vicon needs a segment for internal organisation

def main():
    osc_client = udp_client.SimpleUDPClient(osc_ip, receiver_port)  # Setup OSC client
    vicon_client = ViconDataStream.Client() # Setup Vicon client
    vicon_client.Connect(vicon_ip) # Connect to Vicon
    if not vicon_client.IsConnected():
        print("Unable to connect to Vicon.")
        return
    print(f"Connected to Vicon.")
    vicon_client.EnableSegmentData() # Limit Vicon data streaming to the segment used

    try:
        while vicon_client.IsConnected():
            if vicon_client.GetFrame(): # Latest frame of tracking data from Vicon
                try:
                    # Get position data from Vicon
                    position_data = vicon_client.GetSegmentGlobalTranslation(vicon_subject, vicon_segment)
                    markers_occluded = position_data[1]

                    if not markers_occluded: # Otherwise position is snapped to origin when markers are not visible
                        # Convert raw position from Vicon in mm to m
                        # Also convert to python list as OSC client requires a standard Python list
                        head_position = position_data[0] # position [x, y, z] in mm

                        # Get head-orientation data from Vicon
                        orientation_data = vicon_client.GetSegmentGlobalRotationEulerXYZ(vicon_subject, vicon_segment)
                        # Extract head-orientation angles, in radians by default.
                        # Converted to degrees in the range (-180 to 180)
                        # This is in [roll, pitch, yaw] order
                        (head_orientation_roll_deg, head_orientation_pitch_deg,
                         head_orientation_yaw_deg) = np.degrees(orientation_data[0])

                        # Send head-position and orientation via OSC
                        osc_client.send_message("/head_position", head_position) # Sending position [x, y, z] m
                        osc_client.send_message("/head_orientation", [head_orientation_yaw_deg,
                                  head_orientation_pitch_deg,
                                  head_orientation_roll_deg]) # head-position [yaw, pitch, roll] in degrees

                except Exception:
                    pass
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nHead-tracking stopped.")
    finally:
        vicon_client.Disconnect()
        print("Disconnected from Vicon.")

if __name__ == "__main__":
    main()