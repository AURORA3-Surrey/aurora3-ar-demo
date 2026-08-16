"""
Processes raw Binaural Room Impulse Responses (BRIRs) and formats them into a
pybinsim-compatible filtermap dataset.

This script reads raw BRIR data (measured from front and side loudspeakers)
and a headphone equalization filter stored in HDF5 (.mat) format. It handles
the complex reshaping, transposing, and coordinate mapping required to translate
raw MATLAB data into the specific NumPy structured arrays expected by pybinsim.
Spatial parameters are explicitly defined: positional movement along the X-axis
(converted to cm) and 360-degree head orientations (converted to counter-clockwise,
scaled by 10 for pybinsim integer compatibility). The filters are truncated to
24,000 samples and exported alongside spatial metadata (listener/source positions
and orientations) into a final pybinsim-ready .mat file.

Inputs:
    ../raw_aurora3_brir_dataset/data_speaker_1.mat: Raw BRIRs for the side speaker.
    ../raw_aurora3_brir_dataset/data_speaker_2.mat: Raw BRIRs for the front speaker.
    setup/mushroom_HP_filter.mat: Headphone filter.

Data processing variables:
    h_side / h_front (ndarray): The reshaped BRIR matrices of shape
        (num_positions, num_orientations, 2_channels, 48000_samples).
    r (ndarray): Listener positions along the X-axis (0 to 2.0 meters, in 25cm increments),
        converted to centimeters [x, 0, 0].
    yaws_rev (ndarray): Head orientations (0 to 360 in 2.5-degree increments),
        reversed to map clockwise measurements to a counter-clockwise reproduction
        system, and multiplied by 10 to match pybinsim format.
    theta (ndarray): The final [yaw, pitch, roll] angular coordinate arrays.
    len_BRIR (int): Length of the impulse responses to process.
    binsim_front_speaker (ndarray): Structured array containing spatial metadata
        (type, listener/source co-ords) and the BRIR payload for the front speaker (source at [0,0,0]).
    binsim_side_speaker (ndarray): Structured array containing spatial metadata
        and the BRIR payload for the side speaker (source at [1,0,0]).

Output:
    Saves '../demo_setup/pybinsim_filtermap_aurora3_ar_demo.mat', containing the BRIR filters
    for dynamic binaural reproduction via pybinsim.
"""
import numpy as np
import scipy.io as sio
import h5py

# Import BRIR data
f_side = h5py.File('../raw_aurora3_brir_dataset/data_speaker_1.mat', 'r')
f_front = h5py.File('../raw_aurora3_brir_dataset/data_speaker_2.mat', 'r')

ir_data_side = np.array(f_side['BRIRs']).T
ir_data_front = np.array(f_front['BRIRs']).T
h_side_raw = ir_data_side[:, :, :, [0, 1, 3, 4, 5, 6]]
h_front_raw = ir_data_front
h_side = h_side_raw.transpose((3, 2, 1, 0))
h_front = h_front_raw.transpose((3, 2, 1, 0))
# now these are of shape (9, 144, 2, 48000)

# Import headphone filter
f_hp = h5py.File('setup/mushroom_HP_filter.mat', 'r')
hp = np.array(f_hp['hp']).T
f_hp.close()

# Positional setup
r_x = np.arange(0, 2.25, 0.25) # 2.25 ensures it stops at 2.0 inclusive
r = np.column_stack((r_x, np.zeros(len(r_x)), np.zeros(len(r_x)))) * 100
# r is in cm now

# Head orientation setup
# Here, I have assumed that the BRIRs were measued clockwise
# I have changed to counter clockwise to match the reproduction system
yaws = np.arange(0, 360, 2.5)

# thetas * 10 to get integer angular values due pybimsim issues
yaws_rev = np.concatenate(([yaws[0]], yaws[1:][::-1])) * 10
theta = np.column_stack((yaws_rev, np.zeros(len(yaws_rev)), np.zeros(len(yaws_rev))))

# Mapping function (Defined before we use it in Python)
def make_filter(filter_map, N_pos, N_theta, len_er, N):
    fil = [None] * N
    index = 0  # Python indices start at 0
    for i in range(N_pos):
        for j in range(N_theta):
            if index < N:
                # fil{index} = single(squeeze(filter_map(i, j, :, 1:len_er)))';
                fil[index] = filter_map[i, j, :, 0:len_er].astype(np.float32).T
                index += 1
    return fil

# Filtermap setup and export
len_BRIR = 24000
N_pos = r.shape[0]     # size(r, 1)
N_theta = theta.shape[0] # size(theta, 1)
N = N_pos * N_theta
type_cell = [['DS'] for _ in range(N)]

# Listener positions and orientations
listener_position = np.repeat(r, N_theta, axis=0)
listener_position = listener_position[0:(N_pos * N_theta), :]
listener_position_cell = np.round(listener_position).astype(int).tolist()
theta_cell = np.round(theta).astype(int).tolist()
listener_orientation_cell = theta_cell * N_pos
source_position_front = [[0, 0, 0] for _ in range(N)]
source_position_side = [[1, 0, 0] for _ in range(N)]
source_orientation = [[0, 0, 0] for _ in range(N)]
custom = [[0, 0, 0] for _ in range(N)]

# Generate filters for each loudspeaker
filter_speaker_1 = make_filter(h_front, N_pos, N_theta, len_BRIR, N)
filter_speaker_2 = make_filter(h_side, N_pos, N_theta, len_BRIR, N)

# Generate pybinsim structs
# To perfectly emulate an array of structs in Python -> MATLAB, we use a structured array
struct_dtype = [
    ('type', 'O'),
    ('listenerOrientation', 'O'),
    ('listenerPosition', 'O'),
    ('sourceOrientation', 'O'),
    ('sourcePosition', 'O'),
    ('custom', 'O'),
    ('filter', 'O')
]

binsim_front_speaker = np.empty((N, 1), dtype=struct_dtype)
binsim_side_speaker = np.empty((N, 1), dtype=struct_dtype)

for i in range(N):
    binsim_front_speaker[i, 0]['type'] = type_cell[i][0]
    binsim_front_speaker[i, 0]['listenerOrientation'] = np.array(listener_orientation_cell[i], dtype=float).reshape(1, 3)
    binsim_front_speaker[i, 0]['listenerPosition'] = np.array(listener_position_cell[i], dtype=float).reshape(1, 3)
    binsim_front_speaker[i, 0]['sourceOrientation'] = np.array(source_orientation[i], dtype=float).reshape(1, 3)
    binsim_front_speaker[i, 0]['sourcePosition'] = np.array(source_position_front[i], dtype=float).reshape(1, 3)
    binsim_front_speaker[i, 0]['custom'] = np.array(custom[i], dtype=float).reshape(1, 3)
    binsim_front_speaker[i, 0]['filter'] = filter_speaker_1[i]

    binsim_side_speaker[i, 0]['type'] = type_cell[i][0]
    binsim_side_speaker[i, 0]['listenerOrientation'] = np.array(listener_orientation_cell[i], dtype=float).reshape(1, 3)
    binsim_side_speaker[i, 0]['listenerPosition'] = np.array(listener_position_cell[i], dtype=float).reshape(1, 3)
    binsim_side_speaker[i, 0]['sourceOrientation'] = np.array(source_orientation[i], dtype=float).reshape(1, 3)
    binsim_side_speaker[i, 0]['sourcePosition'] = np.array(source_position_side[i], dtype=float).reshape(1, 3)
    binsim_side_speaker[i, 0]['custom'] = np.array(custom[i], dtype=float).reshape(1, 3)
    binsim_side_speaker[i, 0]['filter'] = filter_speaker_2[i]

# Export
save_path = 'setup/pybinsim_filtermap_aurora3_ar_demo.mat'
sio.savemat(save_path, {
    'binsim_side_speaker': binsim_side_speaker,
    'binsim_front_speaker': binsim_front_speaker,
    'hp': hp
})