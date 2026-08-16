"""
This script connects to a Vicon motion capture system, retrieves a single valid frame
of tracking data for a specific subject and segment, and prints the results.
It connects to the specified IP and enables segment data streaming via vicon_client.EnableSegmentData().
Raw position data is converted from mm to m and the raw orientation data is converted from radians to degrees.

Variables:
    vicon_ip (str): The network address and port of the Vicon software broadcasting data.
    vicon_subject (str): The name of the overall tracked subject/object ie the rigid body, exactly
        as it is configured in the Vicon software ("head_tracker" here).
    vicon_segment (str): The specific rigid body or individual segment on that subject
        to track (single rigid body/segment here, both named "head_tracker").
    position_data (tuple): Raw Vicon translation data ([x, y, z] in mm, occlusion flag).
    orientation_data (tuple): Raw Vicon rotation data (in radians).
    markers_occluded (bool): Flag indicating if the cameras have lost sight of the tracker.
    head_position (list): The converted [x, y, z] position in meters.
    head_orientation_* (float): The converted yaw, pitch, and roll angles in degrees.

Outputs:
    Prints the 3D Position [x, y, z] in m.
    Prints the 3D Orientation [yaw, pitch, roll] in degrees.
"""
from vicon_dssdk import ViconDataStream
import numpy as np
import time

# Vicon setup
vicon_ip = "localhost:801" # Vicon and OSC streaming on the same machine
vicon_subject = "head_tracker"  # The rigid body name setup in Vicon (see Vicon setup notes for more info)
vicon_segment = "head_tracker" # Vicon needs a segment for internal organisation

def main():
    vicon_client = ViconDataStream.Client() # Setup Vicon client
    vicon_client.Connect(vicon_ip) # Connect to Vicon
    if not vicon_client.IsConnected():
        print("Unable to connect to Vicon.")
        return
    print("Connected to Vicon.")
    vicon_client.EnableSegmentData() # Limit Vicon data streaming to the segment used

    try:
        while vicon_client.IsConnected():
            if vicon_client.GetFrame(): # Latest frame of tracking data from Vicon
                try:
                    # Get position data from Vicon
                    position_data = vicon_client.GetSegmentGlobalTranslation(vicon_subject, vicon_segment)
                    markers_occluded = position_data[1]

                    if not markers_occluded:  # Otherwise position is snapped to origin when markers are not visible
                        # Convert raw position from Vicon in mm to m
                        # Also convert to python list as OSC client requires a standard Python list
                        head_position = (np.array(position_data[0]) / 1000.).tolist()

                        # Get head-orientation data from Vicon
                        orientation_data = vicon_client.GetSegmentGlobalRotationEulerXYZ(vicon_subject, vicon_segment)
                        # Extract head-orientation angles, in radians by default.
                        # Converted to degrees in the range (-180 to 180)
                        # This is in [roll, pitch, yaw] order
                        (head_orientation_roll_deg, head_orientation_pitch_deg,
                         head_orientation_yaw_deg) = np.degrees(orientation_data[0])

                        # Print captured position and orientation
                        print(f"Position [x, y, z] in m: [{head_position[0]:}, {head_position[1]:}, {head_position[2]:}]")
                        print(f"Orientation [yaw, pitch, roll] in degrees: [{head_orientation_yaw_deg:.1f}, "
                              f"{head_orientation_pitch_deg:.1f}, "
                              f"{head_orientation_roll_deg:.1f}]\n")
                        break
                except Exception:
                    pass
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nTracking stopped.")
    finally:
        vicon_client.Disconnect()
        print("Disconnected from Vicon.")

if __name__ == "__main__":
    main()