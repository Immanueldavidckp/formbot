import whisper
import pyaudio
import wave
import numpy as np
import time

class VoiceController:
    def __init__(self, motor_controller):
        self.motors = motor_controller
        self.model = whisper.load_model("tiny")
        self.commands = {
            'go straight': self.motors.forward,
            'move forward': self.motors.forward,
            'go back': lambda: self.motors.backward(0.5),
            'move backward': lambda: self.motors.backward(0.5),
            'stop': self.motors.emergency_stop,
            'halt': self.motors.emergency_stop,
            'left': lambda: self._turn_left(0.5),
            'right': lambda: self._turn_right(0.5),
        }
        
        # Audio config
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.SILENCE_THRESHOLD = 500
        
    def _turn_left(self, speed):
        # Implement left turn logic based on your motor setup
        GPIO.output(self.motors.pins['left_fwd'], GPIO.LOW)
        GPIO.output(self.motors.pins['right_fwd'], GPIO.HIGH)
        
    def _turn_right(self, speed):
        # Implement right turn logic based on your motor setup
        GPIO.output(self.motors.pins['left_fwd'], GPIO.HIGH)
        GPIO.output(self.motors.pins['right_fwd'], GPIO.LOW)

    def listen(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)
        
        print("\nListening for command... (speak now)")
        frames = []
        silent_frames = 0
        
        for _ in range(0, int(self.RATE / self.CHUNK * 3)):  # Max 3 seconds
            data = stream.read(self.CHUNK, exception_on_overflow=False)
            frames.append(data)
            
            # Simple silence detection
            audio_data = np.frombuffer(data, dtype=np.int16)
            if np.abs(audio_data).mean() < self.SILENCE_THRESHOLD:
                silent_frames += 1
                if silent_frames > 10:  # 10 silent chunks = ~1s silence
                    break
            else:
                silent_frames = 0
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Save and transcribe
        with wave.open("temp.wav", 'wb') as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(p.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))
        
        result = self.model.transcribe("temp.wav")
        return result["text"].strip().lower()
    
    def process_command(self, text):
        for cmd, action in self.commands.items():
            if cmd in text:
                print(f"Executing voice command: {cmd}")
                action()
                return True
        return False
