from pylsl import StreamInfo, StreamOutlet
from uuid import uuid4

info = StreamInfo('AURA_corsi', 'EEG', 1, 250, 'string', str(uuid4()))

outlet = StreamOutlet(info)
