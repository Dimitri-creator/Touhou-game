import pygame

SOUND_EFFECTS = {}
sfx_volume = 1.0  # Default volume

def init_mixer():
    """
    Initializes Pygame's mixer with specific settings.
    Should be called once, typically at the start of the game.
    """
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        print("Pygame mixer initialized successfully.")
    except pygame.error as e:
        print(f"Error initializing Pygame mixer: {e}")

def load_sound(name, path):
    """
    Loads a sound effect and stores it in the SOUND_EFFECTS dictionary.
    :param name: The key name to store the sound under.
    :param path: The file path to the sound effect.
    """
    try:
        sound = pygame.mixer.Sound(path)
        SOUND_EFFECTS[name] = sound
        print(f"Sound loaded successfully: {name} from {path}")
    except pygame.error as e:
        print(f"Failed to load sound: {name} from {path} - {e}")
    except FileNotFoundError:
        print(f"Sound file not found: {name} at {path}")


def play_sound(name, loops=0):
    """
    Plays a loaded sound effect.
    :param name: The name of the sound effect to play (key in SOUND_EFFECTS).
    :param loops: Number of times to loop the sound (0 means play once).
    """
    if name in SOUND_EFFECTS:
        sound = SOUND_EFFECTS[name]
        sound.set_volume(sfx_volume)  # Apply current global SFX volume
        sound.play(loops=loops)
    else:
        print(f"Sound '{name}' not found or not loaded.")

def set_sfx_volume(volume_level):
    """
    Sets the global volume for sound effects.
    :param volume_level: A float between 0.0 (mute) and 1.0 (full volume).
    """
    global sfx_volume
    sfx_volume = max(0.0, min(1.0, float(volume_level)))
    print(f"SFX Volume set to: {sfx_volume}")

def get_sfx_volume():
    """
    Returns the current global SFX volume.
    :return: Float representing the current SFX volume (0.0 to 1.0).
    """
    return sfx_volume

if __name__ == '__main__':
    # Example Usage / Test
    pygame.init()  # Pygame needs to be initialized for sound
    init_mixer()   # Initialize the mixer

    # Create dummy sound files for testing if they don't exist
    # This is a simplified approach. For real .wav, you'd need a proper library or tool.
    import os
    os.makedirs("assets/sfx", exist_ok=True) # Ensure dir exists
    
    dummy_sounds_to_create = {
        "test_click": "assets/sfx/test_click.wav",
        "test_beep": "assets/sfx/test_beep.wav"
    }

    # Basic WAV file generation (very simple, might not work on all systems/players)
    # For robust WAV creation, a library like 'wave' would be needed.
    # This creates minimal valid (but silent or near-silent) WAV files.
    def create_minimal_wav(path, duration_ms=100, freq=440, sample_rate=44100):
        import wave, struct, math
        if os.path.exists(path):
            return # Don't overwrite
        try:
            num_channels = 1
            sampwidth = 2 # 16-bit
            num_frames = int(sample_rate * (duration_ms / 1000.0))
            
            with wave.open(path, 'w') as wf:
                wf.setnchannels(num_channels)
                wf.setsampwidth(sampwidth)
                wf.setframerate(sample_rate)
                
                max_amplitude = 32767 # For 16-bit
                
                for i in range(num_frames):
                    # Simple sine wave, or just silence (0)
                    # value = int(max_amplitude * math.sin(2 * math.pi * freq * (i / sample_rate)))
                    value = 0 # Silent is easier and safer for a placeholder
                    data = struct.pack('<h', value)
                    wf.writeframesraw(data)
            print(f"Created minimal WAV: {path}")
        except Exception as e:
            print(f"Could not create dummy WAV {path}: {e}. Manual creation might be needed.")


    for name, sound_path in dummy_sounds_to_create.items():
        create_minimal_wav(sound_path) # Attempt to create if not exists
        load_sound(name, sound_path)

    print("\nTesting sound playback...")
    set_sfx_volume(0.5) # Test volume setting
    
    if "test_click" in SOUND_EFFECTS:
        print("Playing 'test_click' (should be audible if sound system works and file is valid)")
        play_sound("test_click")
        pygame.time.wait(500) # Wait for sound to play
    else:
        print("'test_click' not loaded.")

    if "test_beep" in SOUND_EFFECTS:
        print("Playing 'test_beep' at full volume temporarily")
        SOUND_EFFECTS["test_beep"].set_volume(1.0) # Test individual volume setting if needed
        play_sound("test_beep")
        pygame.time.wait(500)
    else:
        print("'test_beep' not loaded.")

    print("\nAttempting to play a non-existent sound:")
    play_sound("non_existent_sound")
    
    print("\nSound manager test finished.")
    pygame.quit()
