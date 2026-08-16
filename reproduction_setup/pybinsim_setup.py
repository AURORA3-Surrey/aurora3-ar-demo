"""
Loads a configuration txt file and begins the audio stream using pybinsim.
"""
import pybinsim
import logging

pybinsim.logger.setLevel(logging.WARNING)
with pybinsim.BinSim('path/config.txt') as binsim:
    binsim.stream_start()