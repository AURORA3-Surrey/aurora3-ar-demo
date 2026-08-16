"""
Streams, processes, and quantizes real-time head tracking data from a
Vicon motion capture system to an OSC-compatible application (such as pybinsim).
Tt converts position data to meters, allows for x/y axis inversion,
snaps the x and y co-ordinates to the closest point in a pre-defined measurement
grid (the BRIR measurement points), maps the yaw angle to a 0-360 degree scale, and snaps the
yaw angle to 2.5-degree increments. The processed data is then steamed via OSC.

Global Configuration Variables:
    osc_ip (str): The destination IP address for the OSC messages.
    receiver_port (int): The destination network port for the OSC messages.
    vicon_ip (str): The network address and port of the Vicon software.
    vicon_subject (str): The exact name of the tracked subject/object in Vicon.
    vicon_segment (str): The specific rigid body or segment on the subject.
    invert_x_axis (bool): If True, multiplies the final x position by -1.
    invert_y_axis (bool): If True, multiplies the final y position by -1.
    sampling_resolution (float): The distance (in m) between measurement
        points. x and y positions are rounded to the nearest multiple of this value.

Internal Data Variables (inside main):
    osc_client (SimpleUDPClient): Handles sending the OSC messages over the network.
    vicon_client (ViconDataStream.Client): Handles receiving the data from Vicon.
    position_data (tuple): Raw Vicon translation data ([x, y, z] in mm, occlusion flag).
    orientation_data (tuple): Raw Vicon rotation data (in radians).
    markers_occluded (bool): Flag indicating if the cameras have lost sight of the tracker.
    head_position (list): The tracked [x, y, z] position, converted to meters.
        X and Y are snapped to the `sampling_resolution`.
    head_orientation_* (float): The yaw, pitch, and roll angles converted to degrees.
        Yaw is specifically mapped to 0-360 degrees and rounded to the nearest 2.5 degrees.

OSC Outputs:
    /head_position (list of floats): Sends the processed [X, Y, Z] position in meters.
    /head_orientation (list of floats): Sends the processed [Yaw, Pitch, Roll]
        orientation in degrees.
"""

from vicon_dssdk import ViconDataStream # Do we need anything else from the vicon end?
from pythonosc import udp_client
import numpy as np
import time

# Vicon and OSC setup
osc_ip = "127.0.0.1"
receiver_port = 9000
vicon_ip = "localhost:801" # Vicon and OSC streaming on the same machine
vicon_subject = "head_tracker"  # The rigid body name setup in Vicon (see Vicon setup notes for more info)
vicon_segment = "head_tracker" # Vicon needs a segment for internal organisation

# Setup x and y axes flipping and specify spatial sampling resolution on the demo line
invert_x_axis = False
invert_y_axis = False
sampling_resolution = 0.2 # Distance between measurement points on the line, in m

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
                        head_position = (np.array(position_data[0])/1000.).tolist() # position [x, y, z] m
                        # Apply axis inversions to position (if they are required)
                        if invert_x_axis:
                            head_position[0] *= -1.
                        if invert_y_axis:
                            head_position[1] *= -1.
                        # Snap x and y positions to the closest BRIR measurement point
                        head_position[0] = round(head_position[0] / sampling_resolution) * sampling_resolution
                        head_position[1] = round(head_position[1] / sampling_resolution) * sampling_resolution

                        # Get head-orientation data from Vicon
                        orientation_data = vicon_client.GetSegmentGlobalRotationEulerXYZ(vicon_subject, vicon_segment)
                        # Extract head-orientation angles, in radians by default.
                        # Converted to degrees in the range (-180 to 180)
                        # This is in [roll, pitch, yaw] order
                        (head_orientation_roll_deg, head_orientation_pitch_deg,
                         head_orientation_yaw_deg) = np.degrees(orientation_data[0])
                        # Convert yaw to 0 to 360 scale (to match pybinsim format)
                        head_orientation_yaw_deg = (head_orientation_yaw_deg + 360) % 360
                        # Round yaw to the closest 2.5 degrees
                        head_orientation_yaw_deg = round(head_orientation_yaw_deg / 2.5) * 2.5
                        # head_orientation_yaw_deg = head_orientation_yaw_deg % 360

                        # Send head-position and orientation via OSC
                        osc_client.send_message("/head_position", head_position) # Sending position [x, y, z] m
                        osc_client.send_message("/head_orientation", [head_orientation_yaw_deg,
                                  head_orientation_pitch_deg,
                                  head_orientation_roll_deg]) # Head-position [yaw, pitch, roll] in degrees

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