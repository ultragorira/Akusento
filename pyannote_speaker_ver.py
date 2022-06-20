import torch
from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
model = PretrainedSpeakerEmbedding(
    "speechbrain/spkrec-ecapa-voxceleb",
    device=torch.device("cpu"))

from pyannote.audio import Audio
from pyannote.core import Segment
audio = Audio(sample_rate=16000, mono=True)

# extract embedding for a speaker speaking between t=3s and t=6s
speaker1 = Segment(.5, 1.)
waveform1, sample_rate = audio.crop("test4.wav", speaker1)
embedding1 = model(waveform1[None])

# extract embedding for a speaker speaking between t=7s and t=12s
speaker2 = Segment(2.3, 3.6)
waveform2, sample_rate = audio.crop("test4.wav", speaker2)
embedding2 = model(waveform2[None])

# compare embeddings using "cosine" distance
from scipy.spatial.distance import cdist
from sklearn.metrics.pairwise import cosine_similarity
distance = cdist(embedding1, embedding2, metric="cosine")
print(distance)
cos_sim = cosine_similarity(embedding1, embedding2)
print(cos_sim)
