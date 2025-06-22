import logging
import sounddevice as sd
import numpy as np

class VoiceInterface:
    def __init__(self):
        self.logger = logging.getLogger("VoiceInterface")
        self.sample_rate = 16000
        self.logger.info("Voice interface initialized")

    def record_audio(self, duration=5):
        self.logger.info("Recording audio...")
        print("Listening...")
        recording = sd.rec(int(duration * self.sample_rate), 
                          samplerate=self.sample_rate, 
                          channels=1,
                          dtype='float32')
        sd.wait()
        return recording

    def transcribe(self, audio):
        # Simplified transcription
        self.logger.info("Transcribing audio...")
        return "This is a simulated transcription"

    def synthesize(self, text):
        # Simplified synthesis
        self.logger.info(f"Synthesizing: {text[:50]}...")
        return np.zeros(int(2 * self.sample_rate), dtype=np.float32)

    def play_audio(self, audio):
        self.logger.info("Playing audio...")
        sd.play(audio, self.sample_rate)
        sd.wait()

    def voice_loop(self, agent):
        print("Voice mode activated. Say 'exit' to quit.")
        while True:
            audio = self.record_audio()
            user_input = self.transcribe(audio)
            
            if "exit" in user_input.lower():
                self.synthesize("Goodbye!")
                break
                
            response = agent.process_request(user_input)
            self.synthesize(response)
            print(f"Kamil: {response}")
