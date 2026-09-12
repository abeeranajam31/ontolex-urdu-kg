"""
Whisper-based ASR wrapper for the speech-to-knowledge-graph pipeline.

Wraps a Hugging Face Whisper checkpoint (defaults to the project author's own
fine-tuned Urdu model, abeeranajam31/whisper-small-urdu-v2) so downstream
stages (term extraction, OntoLex triplification) have a single, swappable
speech-to-text entry point regardless of which checkpoint or language is
actually configured.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import soundfile as sf
from transformers import WhisperForConditionalGeneration, WhisperProcessor


@dataclass
class TranscriptionResult:
    text: str
    model_id: str
    sample_rate: int


class WhisperTranscriber:
    def __init__(self, model_id: str = "abeeranajam31/whisper-small-urdu-v2"):
        self.model_id = model_id
        self.processor = WhisperProcessor.from_pretrained(model_id)
        self.model = WhisperForConditionalGeneration.from_pretrained(model_id)

    def transcribe_file(self, audio_path: str) -> TranscriptionResult:
        audio, sample_rate = sf.read(audio_path)
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        return self.transcribe_array(audio, sample_rate)

    def transcribe_array(self, audio: np.ndarray, sample_rate: int) -> TranscriptionResult:
        inputs = self.processor(audio, sampling_rate=sample_rate, return_tensors="pt")
        predicted_ids = self.model.generate(inputs["input_features"])
        text = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
        return TranscriptionResult(text=text.strip(), model_id=self.model_id, sample_rate=sample_rate)
