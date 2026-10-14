import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

from Identify_pitch import GetPitchFromWav
from scale import Scale
from note_name import NoteName, NoteNameInOctave

Scale_file_path = Path(__file__).with_name("scales.json")

Wav_file_path = Path(__file__).with_name("shidenbeatsmusic-acoustic-guitar-short-intro-ish-live-recording-163329.wav")

class Check_scale:

    """key: str, scale_name: str
    key: for the key of the scale (e.g., "C", "D#", "F")
    scale_name: for the name of the scale (e.g., "major", "minor", "dorian")
    """

    def __init__(self, key: str, scale_name: str):
        self.__key = key
        self.__scale_name = scale_name
        self.__scale = None
        self.__scales_from_json = None

        self.__load_json()
        self.__get_scale_data_from_json()

        self.__noteName = NoteName()
        self.__noteNameInOctave = NoteNameInOctave()

        self.pitchIdentifier = GetPitchFromWav(Wav_file_path)
        root = self.__noteNameInOctave.index(self.__key)
        # JSON notes are semitone offsets; intervals are steps between notes.
        self.__notes_in_scale_in_octave = {
            self.__noteNameInOctave.get(root + offset)
            for offset in self.__scale.notes
        }


    def check_wav_in_scale(self):
        time_of_pitch = self.pitchIdentifier.getTimeOfPitch()

        time_of_None = time_of_pitch.get(None, 0)
        time_of_pitch_in_scale = 0
        time_of_pitch_out_of_scale = 0

        for note, time in time_of_pitch.items():
            if note is None:
                continue
            if note.rstrip("0123456789") in self.__notes_in_scale_in_octave:
                time_of_pitch_in_scale += time
            else:
                time_of_pitch_out_of_scale += time
        total_time = time_of_pitch_in_scale + time_of_pitch_out_of_scale + time_of_None
        if total_time == 0:
            return 0.0  # Avoid division by zero if there are no notes detected

        return time_of_pitch_in_scale, time_of_pitch_out_of_scale, time_of_None, total_time

    def calculate_note_count_score(self):
        # Calculate the score based on the number of notes in the scale
        pitchSeparateWav = self.pitchIdentifier.getPitchSeparateWav()
        counts_note_in_scale = {}
        total_notes = 0
        for note in pitchSeparateWav:
            if note is None:
                continue
            elif note.rstrip("0123456789") in self.__notes_in_scale_in_octave:
                if note not in counts_note_in_scale.keys():
                    counts_note_in_scale[note] = 0
                counts_note_in_scale[note] += 1

            total_notes += 1
        if total_notes == 0:
            return 0.0  # Avoid division by zero if there are no notes detected

        return counts_note_in_scale, total_notes

    def count_note_transitions(self):
        # Count the number of transitions between notes in the scale
        pitchSeparateWav = self.pitchIdentifier.getPitchSeparateWav()
        transitions = 0
        previous_note = None
        for note in pitchSeparateWav:
            if note is None:
                continue
            if previous_note is not None and previous_note != note:
                transitions += 1
            previous_note = note
        return transitions

    def load_wav_and_get_pitch(self, wav_file):
        pitchIdentifier = GetPitchFromWav(wav_file)
        time_of_pitch = pitchIdentifier.getTimeOfPitch()
        return time_of_pitch

    def __get_scale_data_from_json(self):
        # Extract notes from JSON data
        name = self.__scale_name.casefold()
        name = {"minor": "natural minor"}.get(name, name)
        self.__scale = next(
            (s for s in self.__scales_from_json if s.name.casefold() == name),
            None
        )
        if self.__scale is None:
            raise ValueError(f"Unknown scale: {self.__scale_name}")
        self.scale = self.__scale

    def __load_json(self):
        json_data = None
        with open(Scale_file_path, 'r') as file:
            json_data = json.load(file)
        self.__transform_json_to_dict(json_data)
        
    def __transform_json_to_dict(self, json_data):
        self.__scales_from_json = []
        for scale in json_data:
            if "intervals" in scale and "notes" in scale:
                self.__scales_from_json.append(
                    Scale(scale["name"], scale["intervals"], scale["notes"])
                )
            else:
                for direction in ("ascending", "descending"):
                    name = scale["name"]
                    if direction == "descending":
                        name += " (descending)"
                    self.__scales_from_json.append(Scale(
                        name, scale[f"intervals_{direction}"],
                        scale[f"notes_{direction}"]
                    ))


    @property
    def key(self):
        return self.__key

    @key.setter
    def key(self, value):
        self.__key = value

    @property
    def scale_name(self):
        return self.__scale_name

    @scale_name.setter
    def scale_name(self, value):
        self.__scale_name = value
    

def main():
    # Example usage
    key = "A"
    scale_name = "major"
    wav_file = "shidenbeatsmusic-acoustic-guitar-short-intro-ish-live-recording-163329.wav"

    scale_checker = Check_scale(key, scale_name)
    time_of_pitch_in_scale, time_of_pitch_out_of_scale, time_of_None, total_time = scale_checker.check_wav_in_scale()

    print(f"Time of pitch in scale: {time_of_pitch_in_scale}")
    print(f"Time of pitch out of scale: {time_of_pitch_out_of_scale}")
    print(f"Time of None: {time_of_None}")
    print(f"Total time: {total_time}")

    counts_note_in_scale, total_notes = scale_checker.calculate_note_count_score()
    print(f"Counts of notes in scale: {counts_note_in_scale}")
    print(f"Total notes: {total_notes}")

    count_transitions = scale_checker.count_note_transitions()
    print(f"Number of transitions between notes in scale: {count_transitions}")


if __name__ == "__main__":
    main()
