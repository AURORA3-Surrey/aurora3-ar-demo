clc
clear

%% Import BRIR data
h_side_struct = load('../raw_aurora3_brir_dataset/FM.mat');
h_front_struct = load('../raw_aurora3_brir_dataset/FM.mat');

h_side_raw = h_side_struct.BRIRS.Data.IR(:, :, :, [1 2 4 6:11]);
h_front_raw = h_front_struct.BRIRS.Data.IR;
% both these are of shape (48000, 2, 144, 9)
h_side = permute(h_side_raw, [4 3 2 1]);
h_front = permute(h_front_raw, [4 3 2 1]);
% now these are of shape (9, 144, 2, 48000)
clear h_side_struct h_front_struct

% Import headphone filter
load('setup/mushroom_HP_filter');

%% Positional setup
r_x = 0:0.25:2;
r = [r_x(:), zeros(numel(r_x),1), zeros(numel(r_x),1)] * 100;
% r is in cm

%% Head orientation setup
% Here, I have assumed that the BRIRs were measued clockwise
% I have changed to counter clockwise to match the reproduction system
yaws = 0:2.5:357.5;
% thetas * 10 to get integer angular values due pybimsim issues
yaws_rev = [yaws(1), fliplr(yaws(2:end))] * 10;
theta = [yaws_rev(:), zeros(numel(yaws_rev),1), zeros(numel(yaws_rev),1)];

%% Filtermap setup and export
len_BRIR = 24000;
N_pos = size(r, 1);
N_theta = size(theta, 1);
N = N_pos * N_theta;
type = repmat({'DS'}, N, 1);

% Listener positions and orientations
listener_position = repelem(r, N_theta, 1);
listener_position = listener_position(1:(N_pos * N_theta), :);
listener_position = num2cell(round(listener_position), 2);
listener_orientation = repmat(num2cell(round(theta), 2), N_pos, 1);

% Source position and orientation + custom messages
source_position_front = repmat({[0, 0, 0]}, N, 1); % for front loudspeaker
source_position_side = repmat({[1, 0, 0]}, N, 1); % for side loudspeaker
source_orientation = repmat({[0, 0, 0]}, N, 1);
custom = repmat({[0, 0, 0]}, N, 1);

% Generate filters for each loudspeaker
filter_speaker_1 = make_filter(h_front, N_pos, N_theta, len_BRIR, N);
filter_speaker_2 = make_filter(h_side, N_pos, N_theta, len_BRIR, N);

% Generate pybinsim structs
binsim_front_speaker = struct('type', type, ...
    'listenerOrientation', listener_orientation, ...
    'listenerPosition', listener_position, ...
    'sourceOrientation', source_orientation, ...
    'sourcePosition', source_position_front, ...
    'custom', custom, ...
    'filter', filter_speaker_1)';

binsim_side_speaker = struct('type', type, ...
    'listenerOrientation', listener_orientation, ...
    'listenerPosition', listener_position, ...
    'sourceOrientation', source_orientation, ...
    'sourcePosition', source_position_side, ...
    'custom', custom, ...
    'filter', filter_speaker_2)';

% Export final filtermap
save_path = 'setup/FM_LTC_direct_demo.mat';
save(save_path, 'binsim_side_speaker', ...
                'binsim_front_speaker', ...
                'hp')

%% Mapping function
function fil = make_filter(filter_map, N_pos, N_theta, len_er, N)
    fil = cell(N, 1);
    index = 1;
    for i = 1:N_pos
        for j = 1:N_theta
            if index <= N
                fil{index} = single(squeeze(filter_map(i, j, :, 1:len_er)))';
                index = index + 1;
            end
        end
    end
end