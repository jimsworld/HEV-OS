### HEV OS v6.02 ###

#---- Imports
import random
import math
import os
import time
import pygame
pygame.init()

#---- Import Tkinter for GUI
import tkinter as tk

#---- Global Variables
armor = 100
health = 100
energy_types = ['heat', 'shock', 'bio', 'blood toxins', 'chemical', 'radiation']

#---- Instructions
show_instructions = True

#---- Additional Voiceline Chances:
# Hit Detected
major_detected_chance = 1.0  # 40% chance
minor_detected_chance = 1.0  # 40% chance

# Hazard Sound Follow Up 
health_dropping_chance = 1.0  # 50% chance

# Armor Compromised
compromised_chance = 1.0  # 50% chance

# Health Alerts
near_death_chance = 1.0  # 90% chance
health_critical_chance = 1.0  # 65% chance
seek_medic_chance = 1.0  # 50% chance

# Morphine Shot
morphine_chance = 1.0  # 44% chance

#---- Redundant Variables
# hazard_turn = 15
# hazard_turn_counter = 0
########################################################################

############ Loads Sounds ############

def load_sounds(directory):
    sounds = {}
    for root, dirs, files in os.walk(directory):  # Path from root to current directory
        path_parts = root.split(os.sep)
        
        temp_dict = sounds  # Initialize a temporary dictionary based on path_parts
        for part in path_parts[1:]:  # Skip the first part, as it's the main directory
            temp_dict = temp_dict.setdefault(part, {})

        for file in files:  # Load each .wav file in the current directory
            if file.endswith('.wav'):  # Form the key from the file name without its extension
                key = file[:-4]
                # Load the sound and assign it to the correct place in the nested dictionary
                sound_path = os.path.join(root, file)
                temp_dict[key] = pygame.mixer.Sound(sound_path)
    return sounds

hev_common = load_sounds('HEVcommon')
# Example usage:
# hev_common['subfolder']['another_subfolder']['sound_key'].play()


########################################################################

############ Sound Manager ############

class SoundManager:
    def __init__(self):
        self.sound_queue = []
        self.channels = {
            'hit': pygame.mixer.Channel(0),
            'hit_detected': pygame.mixer.Channel(1),
            'hazard': pygame.mixer.Channel(2),
            'armor_alerts': pygame.mixer.Channel(3),
            'health_alerts': pygame.mixer.Channel(4),
            'medical_administer': pygame.mixer.Channel(5),
            'hazard_administer': pygame.mixer.Channel(6),
            'number_playback': pygame.mixer.Channel(7)
        }
        self.hev_common = load_sounds('HEVcommon')
        self.disable_input_during_sound = False  # Enable/disable input while sound is playing

    def is_sound_playing(self):
        if self.disable_input_during_sound and pygame.mixer.get_busy():
            return True
        return False
    
    def add_to_queue(self, sound_path, channel_name='armor_alerts'):
        self.sound_queue.append((sound_path, channel_name))
        self.play_next_in_queue()
    
    def play_next_in_queue(self):
        if self.sound_queue:
            sound_path, channel_name = self.sound_queue.pop(0)
            while self.channels[channel_name].get_busy():
                pygame.time.wait(100)
            self.play_sound(sound_path, channel_name)
    
    def play_sound(self, sound_path, channel_name='hit'):
        try:
            current_dict = self.hev_common  # Start with the base dictionary.
            for key in sound_path:  # Iterate through the parts of the path to navigate the nested dictionaries.
                current_dict = current_dict[key]
            self.channels[channel_name].play(current_dict)  # Play the sound at the final key.
        except KeyError:  # If the sound path is invalid, print a warning.
            print(f"Warning: The sound at path '{sound_path}' does not exist.")
        finally:
            self.play_next_in_queue()
    
    def play_sound_immediately(self, sound_path, channel_name='hit'):
        pygame.mixer.stop()
        self.play_sound(sound_path, channel_name)
    
    def play_sound_simultaneously(self, sound_path, channel_name='hit'):
        try:
            sound = self.hev_common
            for key in sound_path:
                sound = sound[key]
            self.channels[channel_name].play(sound)
        except KeyError:
            print(f"Warning: Sound not found for path {sound_path}.")
    
    def play_and_clear_queue(self, sound_path, channel_name):
        pygame.mixer.stop()  # Stop all sounds
        self.sound_queue.clear()  # Clear the sound queue
        self.play_sound(sound_path, channel_name)  # Play the specified sound

    def get_sound_length(self, sound_path):
        """Return the length of the sound at the specified path in seconds."""
        try:
            current_dict = self.hev_common  # Start with the base dictionary.
            for key in sound_path:  # Iterate through the parts of the path to navigate the nested dictionaries.
                current_dict = current_dict[key]
            return current_dict.get_length()  # Return the length of the sound at the final key.
        except KeyError:  # If the sound path is invalid, print a warning.
            print(f"Warning: The sound at path '{sound_path}' does not exist.")
            return 0
    
    def play_sound_for_duration(self, sound_files, channel_name, duration):
        """Play a sound on the specified channel for the specified duration."""
        start_time = time.time()
        while time.time() - start_time < duration:
            self.play_sound(sound_files, channel_name)
            time.sleep(self.get_sound_length(sound_files))
        self.stop_sound(channel_name)

    def stop_sound(self, channel_name='hit'):
        """Stop the sound that is currently playing on the specified channel."""
        self.channels[channel_name].stop()


########################################################################

############ Damage Calculations ############

def calculate_physical(armor, health, thud):
    if armor >= thud:
        armor -= math.floor(thud * 0.80 / 2)  # Applies 80% divided by 2 of thud to armor, if armor is enough.
        health -= math.floor(thud * 0.20)  # Applies 20% of thud to health, if armor is enough.
    else:
        excess_physical = thud - armor
        health -= excess_physical  # Only the excess of physical damage impacts health.
        armor = 0  # Armor is depleted.
    return armor, health

def calculate_energy(armor, health, hazard):
    if armor >= hazard:
        armor -= hazard
    else:
        excess_energy = hazard - armor
        health -= excess_energy
        armor = 0
    return armor, health


########################################################################

############ Enforce Non-Negative Values ############

def enforce_non_negative(armor, health):
    armor = max(armor, 0)
    health = max(health, 0)
    return armor, health


########################################################################

############ Damage Application and Healing Items ############

#---- Damage Application for Physical
def physical_hit(armor, health, thud):
    armor, health = calculate_physical(armor, health, thud)
    armor, health = enforce_non_negative(armor, health)
    return armor, health


#---- Damage Application for Energy
def energy_hit(armor, health, hazard):
    armor, health = calculate_energy(armor, health, hazard)
    armor, health = enforce_non_negative(armor, health)
    return armor, health


#---- Healing and Repair
def apply_restoration(current_value, amount, max_value):
    updated_value = current_value + amount
    if updated_value > max_value:
        updated_value = max_value
    return updated_value


########################################################################

############ Suit Functions ############

sound_manager = SoundManager()

#---- Hit Sounds and Hit Detected Sounds

major_detected_sound_played = False  # Flag to check if this has played, which will allow Morphine Shot to play.

def hit_sound(thud):
    global major_detected_sound_played
    if thud >= 25:
        major_detected_sound = {
            ('hit', 'pl_fallpain3'): ['medical', 'detected', 'physical', 'boopmid_old_major_fracture'],
            ('hit', 'hc_headbite'): ['medical', 'detected', 'physical', 'boopmid_old_major_lacerations'],
            ('hit', 'claw_strike1'): ['medical', 'detected', 'physical', 'boopmid_old_major_lacerations'],
            ('hit', 'claw_strike2'): ['medical', 'detected', 'physical', 'boopmid_old_major_lacerations']
        }

        major_hits = list(major_detected_sound.keys())  # Get the keys (major hit sounds) from the dictionary
        selected_major_hit = random.choice(major_hits)  # Chosen at random
        sound_manager.play_sound_simultaneously(selected_major_hit, 'hit')

        if random.random() < major_detected_chance:
            major_fracture_lacerations = major_detected_sound[selected_major_hit]  # Lookup the corresponding sound
            sound_manager.play_sound_simultaneously(major_fracture_lacerations, 'hit_detected')
        
            major_detected_sound_played = True

    else:
        minor_detected_sound = {
            ('hit', 'pl_pain2'): ['medical', 'detected', 'physical', 'boopmid_old_minor_fracture'],
            ('hit', 'pl_pain6'): ['medical', 'detected', 'physical', 'boopmid_old_minor_lacerations'],
            ('hit', 'hc_attack1'): ['medical', 'detected', 'physical', 'boopmid_old_minor_lacerations'],
            ('hit', 'claw_strike3'): ['medical', 'detected', 'physical', 'boopmid_old_minor_lacerations']
        }

        minor_hits = list(minor_detected_sound.keys())
        selected_minor_hit = random.choice(minor_hits)
        sound_manager.play_sound_simultaneously(selected_minor_hit, 'hit')

        if random.random() < minor_detected_chance:
            minor_fracture_lacerations = minor_detected_sound[selected_minor_hit]
            sound_manager.play_sound_simultaneously(minor_fracture_lacerations, 'hit_detected')
        
        major_detected_sound_played = False


#---- Hazard Sounds
def hazard_sound(energy_types):
    hazard_sounds = {
        'heat': ['medical', 'detected', 'energy', 'heat_damage_boophighdouble'],
        'shock': ['medical', 'detected', 'energy', 'shock_damage_boophighdouble'],
        'bio': ['medical', 'detected', 'energy', 'biohazard_detected_blipblipblip'],
        'blood toxins': ['medical', 'detected', 'energy', 'blood_toxins_boopmid_old'],
        'chemical': ['medical', 'detected', 'energy', 'chemical_detected_blipblipblip'],
        'radiation': ['medical', 'detected', 'energy', 'radiation_detected_blipblipblip']
    }

    health_dropping_sound = ['medical', 'health', 'boophighdouble_health_dropping2']

    if energy_types in hazard_sounds:
        sound_manager.play_sound(hazard_sounds[energy_types], 'hazard')
        if energy_types in ['bio', 'blood toxins', 'chemical', 'radiation']:
            if random.random() < health_dropping_chance:
                while pygame.mixer.get_busy():
                    pygame.time.wait(100)
                sound_manager.add_to_queue(health_dropping_sound, 'health_alerts')


#---- Armor Alarm
def armor_alarm(health, armor, thud=None, hazard=None):
    if health and armor > 0:
        if thud and thud >= 30:
            armor_buzz = ['misc', 'buzzdouble']
            sound_manager.play_sound_simultaneously(armor_buzz, 'armor_alerts')
        if hazard and hazard >= 30:
            armor_buzz = ['misc', 'buzzdouble']
            sound_manager.play_sound_simultaneously(armor_buzz, 'armor_alerts')


#---- Armor Compromised
armor_was_compromised = False

def armor_compromised(armor):
    if random.random() < compromised_chance:
        while pygame.mixer.get_busy():
            pygame.time.wait(100) # Wait for 100 milliseconds.
        sound_manager.add_to_queue(['armor', 'armor_compromised_complete'], 'armor_alerts')
        sound_manager.play_next_in_queue()


#---- Health Alerts
def health_alerts(health):
    def health_alert_helper(health, health_range, sound_queue, chance, seek_medic_chance=None):
        if health_range[0] <= health <= health_range[1] and random.random() < chance:
            while pygame.mixer.get_busy():
                pygame.time.wait(100)
            sound_manager.add_to_queue(sound_queue, 'health_alerts')
            if seek_medic_chance and random.random() < seek_medic_chance:
                sound_manager.add_to_queue(['medical', 'health', 'booplow_seek_medic'], 'health_alerts')
            sound_manager.play_next_in_queue()
    
    health_alert_helper(health, (1, 6), ['medical', 'health', 'boophigh_near_death'], near_death_chance, seek_medic_chance)
    health_alert_helper(health, (7, 30), ['medical', 'health', 'boophigh_health_critical'], health_critical_chance, seek_medic_chance)
    health_alert_helper(health, (31, 50), ['medical', 'health', 'booplow_seek_medic'], seek_medic_chance)


#---- Morphine Shot
def morphine_shot(thud):
    global major_detected_sound_played
    if thud >= 25 and major_detected_sound_played and random.random() < morphine_chance:
        while pygame.mixer.get_busy():
            pygame.time.wait(100)
        sound_manager.add_to_queue(['medical', 'administered', 'booplow_morphine_shot'], 'medical_administer')
        sound_manager.play_next_in_queue()


#---- Death Noise
is_dead = False  #  Flag to prevent death_noise from being called multiple times.

def death_noise(thud):
    if thud >= 25:
        major_hit_sound = {
            ('hit', 'pl_fallpain3'),
            ('hit', 'hc_headbite'),
            ('hit', 'claw_strike1'),
            ('hit', 'claw_strike2')
        }

        major_hits = list(major_hit_sound)  # Get the major hit sounds
        selected_major_hit = random.choice(major_hits)  # Chosen at random

    else:
        minor_hit_sound = {
            ('hit', 'pl_pain2'),
            ('hit', 'pl_pain6'),
            ('hit', 'hc_attack1'),
            ('hit', 'claw_strike3')
        }

        minor_hits = list(minor_hit_sound)
        selected_minor_hit = random.choice(minor_hits)

    death_sound = ['misc', 'flatline_main']

    if thud >= 25:
        sound_manager.play_and_clear_queue(selected_major_hit, 'hit')
        sound_manager.play_and_clear_queue(death_sound, 'hit_detected')
    else:
        sound_manager.play_and_clear_queue(selected_minor_hit, 'hit')
        sound_manager.play_and_clear_queue(death_sound, 'hit_detected')


#---- Play Number Sound
def play_number_sound(number, folder_path):
    number_to_word = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five',
                    6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten',
                    11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen', 15: 'fifteen',
                    16: 'sixteen', 17: 'seventeen', 18: 'eighteen', 19: 'nineteen', 20: 'twenty',
                    30: 'thirty', 40: 'fourty', 50: 'fifty', 60: 'sixty', 70: 'seventy', 80: 'eighty',
                    90: 'ninety', 100: 'onehundred'}

    if 1 <= number <= 19:  # For numbers 1-19, play the corresponding file directly
        sound_manager.add_to_queue([folder_path, number_to_word[number]], 'number_playback')
    elif 20 <= number <= 99:  # For numbers 20-99, break them down into tens and ones
        tens = number // 10 * 10  # Get the tens part
        ones = number % 10  # Get the ones part
        sound_manager.add_to_queue([folder_path, number_to_word[tens]], 'number_playback')  # Play the tens part
        if ones != 0:  # If there are ones left, play the ones part
            sound_manager.add_to_queue([folder_path, number_to_word[ones]], 'number_playback')
    elif 100 == number:  # For 100, play the corresponding file directly
        sound_manager.add_to_queue([folder_path, number_to_word[number]], 'number_playback')


#---- Play Number Sound In Incremements of 5
def play_number_sound_increments(armor, folder_path):
    increment = round(armor / 5) * 5  # Round to the nearest multiple of 5
    play_number_sound(increment, folder_path)


#---- Armor Readout
power_level_is_100_played = True  # Flag to prevent power_level_is_100 from being played multiple times when armor is 100.

def armor_readout(command, armor):
    global power_level_is_100_played

    fuzz_sounds = {
        ('misc', 'fuzzdouble'),
        ('misc', 'fuzzhighdouble')
    }
    fuzz_double_random = random.choice(list(fuzz_sounds))

    if 1 <= armor <= 100:
        sound_manager.play_sound_simultaneously(fuzz_double_random, 'number_playback')
        if armor == 100:
            sound_manager.add_to_queue(['armor', 'power_level_is'], 'number_playback')
            power_level_is_100_played = True
        else:
            sound_manager.add_to_queue(['armor', 'power'], 'number_playback')
        
        if command == 'repair':  # If the command is repair, play the armor value in increments of 5.
            play_number_sound_increments(armor, 'number')
        elif command == "armor":  # If the command is armor, plays the exact armor value.
            play_number_sound(armor, 'number')
        
        sound_manager.add_to_queue(['percent'], 'number_playback')
    
    else:  # If the armor value is 0, play a warning sound.
        sound_manager.add_to_queue(['misc', 'warning2'], 'number_playback')


#---- Healing Items
def healing_items(command):
    if command == 'heal':
        if health < 100:
            sound_manager.play_sound_simultaneously(['items', 'smallmedkit1'], 'medical_administer')
        else:
            sound_manager.play_sound_simultaneously(['items', 'medshotno1'], 'medical_administer')
        
    elif command == 'repair':
        if armor < 100:
            sound_manager.play_sound_simultaneously(['items', 'hl2', 'battery_pickup'], 'medical_administer')
        else:
            sound_manager.play_sound_simultaneously(['items', 'suitchargeno1'], 'medical_administer')


########################################################################

############ Heal and Repair over time ############

########################################################################

############ Tkinter GUI Loop ############

root = tk.Tk()
root.title("HEV Suit v6.02")

hit_button = tk.Button(root, text="Hit", command=lambda: sound_manager.play_sound(['hit', 'pl_fallpain3'], 'hit'))
hit_button.pack()

root.mainloop()

########################################################################

############ Main Loop ############

while True:

    if sound_manager.is_sound_playing():
        continue

    #-----Instructions
    if show_instructions:
        print("\nHEV Suit test ready. Available commands:"
            "\n'hit':     physical attack between 1 - 50"
            "\n'hazard':  energy hazard between 1 - 40"
            "\n'heal':    heals 15HP"
            "\n'repair':  repairs 15AP"
            "\n'armor':   checks current armor level"
            "\n'quit':    exits.")
        show_instructions = False  # Stops repetitive instructions

    # just_had_hit = False  # Flag to prevent armor_compromised playing twice after hit command when armor is 0
    # just_had_hazard = False  # Flag to prevent armor_compromised playing twice after hazard command when armor is 0

    #User Input
    user_input = input("\nEnter command: ")
    match user_input:

        #-----

        case 'hit':
            # just_had_hit = True
            # hazard_turn_counter += random.randint(1, 5)  # Increment the hazard counter
            thud = random.randint(1, 50)  # This randomises damage value for each hit
            
            armor_alarm(health, armor, thud=thud)

            armor, health = physical_hit(armor, health, thud)

            power_level_is_100_played = False

            if health <= 0 and not is_dead:
                death_noise(thud)
                is_dead = True
            
            if health > 0:  # If health is still above 0 after physical hit
                hit_sound(thud)

                if armor <= 0 and not armor_was_compromised:  # Only call armor_compromised if armor is not already compromised
                    armor_compromised(armor)  # Checks if armor is compromised after each hit
                    armor_was_compromised = True  # Set flag to prevent armor_compromised from being called twice

                health_alerts(health)
            
                morphine_shot(thud)

            print(f"---- {'MINOR' if thud < 25 else 'MAJOR'} Thud, -{thud} physical damage")

        #-----

        case 'hazard':
            # just_had_hazard = True
            hazard = random.randint(1, 40)

            armor_alarm(health, armor, hazard=hazard)

            armor, health = energy_hit(armor, health, hazard)

            power_level_is_100_played = False

            if health <= 0 and not is_dead:
                death_noise(hazard)
                is_dead = True
            
            if health > 0:
                energy_type = random.choice(energy_types)
                hazard_sound(energy_type)
                
                if armor <= 0 and not armor_was_compromised:
                    armor_compromised(armor)
                    armor_was_compromised = True

                health_alerts(health)
            
            print(f"---- {energy_type.title()} Hazard, -{hazard} energy damage")

        #-----

        case 'heal':
            healing_items(user_input)
            health = apply_restoration(health, 15, 100)
            is_dead = False  # Reset the flag to allow death_noise to be called again.
            print("---- Health has been restored!")

        #-----

        case 'repair':
            healing_items(user_input)
            armor = apply_restoration(armor, 15, 100)
            if not power_level_is_100_played:
                armor_readout(user_input, armor)
            armor_was_compromised = False  # Reset the flag to allow armor_compromised to be called again.
            print("---- Armor has been repaired!")

        #-----

        case 'armor':
            armor_readout(user_input, armor)

        #-----

        case 'quit':
            print("HEV Suit shutting down.")
            break

        #-----

        case _:
            print("Unknown command. Please enter:"
                  "\n'hit'"
                  "\n'hazard'"
                  "\n'heal'"
                  "\n'repair'"
                  "\n'armor'"
                  "\n'quit'")

    # #-----Random Hazard
    # if hazard_turn_counter >= hazard_turn:  # Triggers a random hazard when threshold is met
    #     hazard = random.randint(1, 40)  # This randomises energy value for each hazard
    #     energy_type = random.choice(energy_types)
    #     armor, health = energy_hit(armor, health, hazard)
    #     if health > 0:
    #     if armor <= 0 and not armor_was_compromised:
    #         armor_compromised(armor)
    #         armor_was_compromised = True
        
    #     print(f"---- {energy_type.title()} hazard, for {hazard} energy damage")

    #     hazard_turn_counter = 0
    #     just_had_hit = False  # Reset the flag
    #     just_had_hazard = False  # Reset the flag

    #-----Armor and Health Readouts
    print("==== Remaining armor: ", armor)
    print("==== Remaining health: ", health)


########################################################################