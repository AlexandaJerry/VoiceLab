import math

from Voicelab.pipeline.Node import Node
from parselmouth.praat import call
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode

###################################################################################################
# MEASURE DURATION NODE
# WARIO pipeline node for measuring the duration of a voice.
###################################################################################################
# ARGUMENTS
# 'voice'   : sound file generated by parselmouth praat
###################################################################################################
# RETURNS
# 'snr'  : Signal to noise Ratio
###################################################################################################


class MeasureSNRNode(VoicelabNode):
    def __init__(self, *args, **kwargs):
        """
        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)

        self.args = {
            "minimum_dB": -25,  # Negative number
            "minimum_silent_interval_duration": 0.1,  # positive number
            "maximum_silent_interval_duration": 0.05,  # positive number
            "tier1_label": "silent",  # string
            "tier2_label": "sounding", # string
        }

    ###############################################################################################
    # process: WARIO hook called once for each voice file.
    ###############################################################################################

    def process(self):
        """signal_to_noise_ratio"""
        try:
            minimum_dB = self.args["minimum_dB"]
            minimum_silent_interval_duration = self.args["minimum_silent_interval_duration"]
            maximum_silent_interval_duration = self.args["maximum_silent_interval_duration"]
            tier1_label = self.args["tier1_label"]
            tier2_label = self.args["tier2_label"]
            file_path: str = self.args["file_path"]
            signal, sampling_rate = self.args['voice']
            voice: parselmouth.Sound = parselmouth.Sound(signal, sampling_rate)
            #voice = self.args["voice"]
            start_time = 0
            end_time = 0  # Zero start and end time means select all in Praat
            interpolation = "None"
            signal = call(
                voice, "Get absolute extremum", start_time, end_time, interpolation
            )
            intensity = voice.to_intensity()

            text_grid = call(
                intensity,
                "To TextGrid (silences)",
                minimum_dB,
                minimum_silent_interval_duration,
                maximum_silent_interval_duration,
                tier1_label,
                tier2_label,
            )

            # -25 sets the silence to be detected when the minimum is 50dB lower than the maximum (25dB)
            # This 50dB threshold is used throughout the software in all analyses
            start_time = call(text_grid, "Get start time of interval", 1, 1)
            end_time = call(text_grid, "Get end time of interval", 1, 1)
            noise = abs(call(voice, "Get absolute extremum", start_time, end_time, "None"))
            snr = 20 * math.log10(signal / noise)
            return {"snr": snr}
        except:
            return {"snr": "snr measurement failed"}
