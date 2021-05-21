import argparse
import time
import numpy as np
from pylsl import StreamInlet, resolve_stream


class Saver:
    def __init__(self):
        self.MAPPER = {
            # 'play': 0,
            # 'pause': 1,
            # 'event': 1,
            # 'stop': 0,
            'start_encoding': 1,
            'end_encoding': 2,
            'start_retrival': 3,
            'end_retrival': 4,
            'end_quit': -1,
            None: 0
        }
        self.info = []
        self.counter = 1
        self.chunk = []
        self.status = False
        self.flagTarget = False

    @staticmethod
    def get_timestamp():
        return int(time.time())

    def check_reading(self, event):
        if event == 'start_encoding':
            print("start_encoding")
            self.status = True
        # elif event == 'pause':
        #     print("start-pause")
        #     self.status = False

    def check_reading_final(self, event):
        if event == 'end_quit':
            print('end_quit')
            self.info = []
            self.chunk = []
            self.counter = 1
            self.status = False
        elif event =='end_retrival':
            self.chunk = []
            self.status = False

    def validate_ones(self, current):
        # TODO: validate if same number twice in target value
        if len(self.info) == 0:
            return current

        last = self.info[-1]

        return current

    def add_data(self, timestamp, brain_info, video_info):
        if brain_info is None:
            return

        event_val = self.MAPPER[video_info]
        brain_info.append(event_val)
        brain_info.insert(0, timestamp)

        # brain_info = self.validate_ones(brain_info)
        self.info.append(brain_info)
        self.chunk.append(brain_info)

        return

    def save_data(self, event):
        if event != 'end_quit':
            return

        info_np = np.asarray(self.info)
        file_name = f"full-{self.get_timestamp()}.csv"
        np.savetxt(file_name, info_np, delimiter=",", fmt='%f')
        print(f"saved-data-{len(self.info)}")
        self.info = []
        print(len(self.info))

    def save_chunk(self, event):
        if event in ['end_retrival']:
            info_np = np.asarray(self.chunk)
            file_name = f"chunck-{self.get_timestamp()}-{self.counter}.csv"
            np.savetxt(file_name, info_np, delimiter=",", fmt='%f')
            print(f"saved-chunk-{len(self.chunk)}")
            self.chunk = []
            print(len(self.chunk))
            self.counter += 1


print("looking for an EEG stream...")
brain_stream = resolve_stream("name", "AURA_power")
video_stream = resolve_stream("name", "AURA_corsi")
print("found streams")


brain_inlet = StreamInlet(brain_stream[0])
video_inlet = StreamInlet(video_stream[0])
brain_inlet.open_stream()
video_inlet.open_stream()

saver = Saver()
video_info = None
print("While entered")

try:
    timestamp = None
    while True:
        brain_info, timestamp = brain_inlet.pull_sample()
        if video_inlet.samples_available():
            video_info, _ = video_inlet.pull_sample()
            video_info = video_info[0]
        saver.check_reading(video_info)
        saver.save_chunk(video_info)
        if saver.status:
            saver.add_data(timestamp, brain_info, video_info)
        saver.save_data(video_info)
        saver.check_reading_final(video_info)
        video_info = None
except KeyboardInterrupt:
    brain_inlet.close_stream()
    video_inlet.close_stream()
except Exception as e:
    print(e)
    brain_inlet.close_stream()
    video_inlet.close_stream()
