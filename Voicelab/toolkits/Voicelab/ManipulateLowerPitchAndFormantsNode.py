from Voicelab.pipeline.Node import Node
from parselmouth.praat import call
from Voicelab.toolkits.Voicelab.VoicelabNode import VoicelabNode

###################################################################################################
# MANIPULATE PITCH AND FORMANTS NODE
# WARIO pipeline node for manipulating voice formants and pitch
###################################################################################################
# ARGUMENTS
# 'voice'   : sound file generated by parselmouth praat
###################################################################################################
# RETURNS
###################################################################################################


class ManipulateLowerPitchAndFormantsNode(VoicelabNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.args = {"unit": ("percent", ["percent"]),
                     "formant_factor": 0.85,
                     "pitch_factor":   0.85,
                     "pitch_range_factor": 1,
                     "duration_factor": 1,
                     "normalize amplitude": True,
                     }

    ###############################################################################################
    # process: WARIO hook called once for each voice file.
    ###############################################################################################
    def process(self):

        sound = self.args["voice"]
        formant_factor = self.args["formant_factor"]
        pitch_factor = self.args["pitch_factor"]
        duration = sound.get_total_duration()
        file_path = self.args["file_path"]
        pitch_range_factor = self.args["pitch_range_factor"]
        duration_factor = 1
        pitch_range_factor = 1
        f0min, f0max = self.pitch_bounds(sound)
        self.args['f0min'], self.args['f0max'] = f0min, f0max
        print(f0min, f0max)
        pitch = sound.to_pitch()
        median_pitch = call(pitch, "Get quantile", 0, duration, 0.5, "Hertz")

        new_pitch_median = pitch_factor * median_pitch

        output_file_name = file_path.split("/")[-1].split(".wav")[0]
        output_file_name = (
            f"{output_file_name}_lower_pitch_and_formants_{pitch_factor}_{formant_factor}"
        )
        number_of_channels = call(sound, 'Get number of channels')
        if number_of_channels == 2:
            sound = call(sound, 'Convert to mono')

        manipulated_sound = call(
            sound,
            "Change gender",
            f0min,
            f0max,
            formant_factor,
            new_pitch_median,
            pitch_range_factor,
            duration_factor,
        )

        if self.args["normalize amplitude"]:
            manipulated_sound.scale_intensity(70)

        manipulated_sound.name = output_file_name

        return {"voice": manipulated_sound}
