import pygame
import math
import struct

# Sintetizador Chiptune retro con melodía musical de fondo y efectos sonoros
def generate_sound(freq_start, freq_end, duration, wave_type="square", volume=0.25):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = bytearray()
    
    for i in range(n_samples):
        t = i / sample_rate
        progress = i / n_samples
        freq = freq_start + (freq_end - freq_start) * progress
        env = (1.0 - progress) * volume
        
        if wave_type == "square":
            phase = (t * freq) % 1.0
            val = 1.0 if phase < 0.5 else -1.0
        elif wave_type == "sine":
            val = math.sin(2 * math.pi * freq * t)
        else: # triangle
            phase = (t * freq) % 1.0
            val = (phase * 4.0 - 1.0) if phase < 0.5 else (3.0 - phase * 4.0)

        sample = int(val * env * 32767)
        buf.extend(struct.pack("<h", max(-32768, min(32767, sample))))
        
    return pygame.mixer.Sound(buffer=bytes(buf))


def generate_kawaii_bgm():
    """Genera una melodía alegre en loop estilo Chiptune/Music Box de Mario Pastel"""
    sample_rate = 22050
    # Notas en Hz: C5, D5, E5, G5, A5, C6
    notes = {
        'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46,
        'G5': 783.99, 'A5': 880.00, 'B5': 987.77, 'C6': 1046.50,
        'R': 0
    }
    
    melody = [
        ('E5', 0.16), ('E5', 0.16), ('R', 0.16), ('E5', 0.16),
        ('R', 0.16),  ('C5', 0.16), ('E5', 0.16), ('R', 0.16),
        ('G5', 0.32), ('R', 0.32),  ('C5', 0.32), ('R', 0.32),
        ('A5', 0.20), ('G5', 0.20), ('E5', 0.20), ('D5', 0.20),
        ('C5', 0.24), ('D5', 0.24), ('E5', 0.24), ('C5', 0.24),
        ('G5', 0.20), ('A5', 0.20), ('C6', 0.28), ('R', 0.20)
    ]
    
    total_samples = int(sum(dur for _, dur in melody) * sample_rate)
    buf = bytearray()
    
    for note, dur in melody:
        freq = notes.get(note, 0)
        n_note_samples = int(dur * sample_rate)
        for i in range(n_note_samples):
            t = i / sample_rate
            env = math.exp(-3.5 * (i / n_note_samples)) * 0.15 # Sonido dulce tipo campana/music box
            if freq > 0:
                val = math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(4 * math.pi * freq * t)
            else:
                val = 0.0
            sample = int(val * env * 32767)
            buf.extend(struct.pack("<h", max(-32768, min(32767, sample))))
            
    return pygame.mixer.Sound(buffer=bytes(buf))


class SoundManager:
    def __init__(self):
        self.muted = False
        try:
            self.snd_jump = generate_sound(220, 560, 0.16, "triangle", 0.22)
            self.snd_coin = generate_sound(987, 1318, 0.28, "sine", 0.32)
            self.snd_bump = generate_sound(160, 80, 0.14, "triangle", 0.25)
            self.bgm = generate_kawaii_bgm()
            self.bgm_channel = pygame.mixer.Channel(0)
        except Exception:
            self.snd_jump = None
            self.snd_coin = None
            self.snd_bump = None
            self.bgm = None
            self.bgm_channel = None

    def start_music(self):
        if self.bgm and self.bgm_channel and not self.muted:
            try:
                self.bgm_channel.play(self.bgm, loops=-1)
            except Exception:
                pass

    def toggle_mute(self):
        self.muted = not self.muted
        if self.bgm_channel:
            if self.muted:
                self.bgm_channel.pause()
            else:
                self.bgm_channel.unpause()
        return self.muted

    def play_jump(self):
        if self.snd_jump and not self.muted:
            try:
                self.snd_jump.play()
            except Exception:
                pass

    def play_coin(self):
        if self.snd_coin and not self.muted:
            try:
                self.snd_coin.play()
            except Exception:
                pass

    def play_bump(self):
        if self.snd_bump and not self.muted:
            try:
                self.snd_bump.play()
            except Exception:
                pass

sound_manager = SoundManager()
