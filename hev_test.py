### version 5.94 ###

import random
import math
import os
import pygame
pygame.init()

armor = 100
health = 100
energy_types = ['heat', 'shock', 'bio', 'chemical', 'radiation']

hazard_turn = 15
hazard_turn_counter = 0

show_instructions = True


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
            'health_threshold_alerts': pygame.mixer.Channel(4),
            'medical_administer': pygame.mixer.Channel(5),
            'hazard_administer': pygame.mixer.Channel(6),
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


########################################################################

############ Damage Calculations ############

def calculate_physical(armor, health, thud):
    if armor >= thud:
        armor -= thud
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

############ Damage Application and Healing ############

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

############ Sound Engine ############

sound_manager = SoundManager()

#---- Hit Sounds and Hit Detected Sounds
def hit_sound(thud):
    if thud >= 25:
        major_followup_sound = {
            ('hit', 'pl_fallpain3'): ['medical', 'detected', 'physical', 'boopmid_old_major_fracture'],
            ('hit', 'hc_headbite'): ['medical', 'detected', 'physical', 'boopmid_old_major_lacerations'],
            ('hit', 'claw_strike1'): ['medical', 'detected', 'physical', 'boopmid_old_major_lacerations'],
            ('hit', 'claw_strike2'): ['medical', 'detected', 'physical', 'boopmid_old_major_lacerations']
        }

        heavy_hits = list(major_followup_sound.keys())  # Get the keys (heavy hit sounds) from the dictionary
        selected_heavy_hit = random.choice(heavy_hits)  # Chosen at random
        sound_manager.play_sound_simultaneously(selected_heavy_hit, 'hit')

        major_detected_chance = 1.0  # 40% chance
        if random.random() < major_detected_chance:
            major_fracture_lacerations = major_followup_sound[selected_heavy_hit]  # Lookup the corresponding sound
            sound_manager.play_sound_simultaneously(major_fracture_lacerations, 'hit_detected')

    else:
        minor_followup_sound = {
            ('hit', 'pl_pain2'): ['medical', 'detected', 'physical', 'boopmid_old_minor_fracture'],
            ('hit', 'pl_pain6'): ['medical', 'detected', 'physical', 'boopmid_old_minor_lacerations'],
            ('hit', 'hc_attack1'): ['medical', 'detected', 'physical', 'boopmid_old_minor_lacerations'],
            ('hit', 'claw_strike3'): ['medical', 'detected', 'physical', 'boopmid_old_minor_lacerations']
        }

        light_hits = list(minor_followup_sound.keys())
        selected_light_hit = random.choice(light_hits)
        sound_manager.play_sound_simultaneously(selected_light_hit, 'hit')

        minor_detected_chance = 1.0  # 40% chance
        if random.random() < minor_detected_chance:
            minor_fracture_lacerations = minor_followup_sound[selected_light_hit]
            sound_manager.play_sound_simultaneously(minor_fracture_lacerations, 'hit_detected')


#---- Armor Compromised
armor_was_compromised = False

def armor_compromised(armor):
    compromised_chance = 1.0  # 50% chance
    if random.random() < compromised_chance:
        while pygame.mixer.get_busy():
            pygame.time.wait(100) # Wait for 100 milliseconds.
        sound_manager.add_to_queue(['armor', 'armor_compromised_complete'], 'armor_alerts')
        sound_manager.play_next_in_queue()


#---- Health Threshold Alerts
def health_threshold_alerts(health):

    near_death_chance = 1.0  # 100% chance
    health_critical_chance = 1.0  # 100% chance
    seek_medic_chance = 1.0  # 100% chance

    if 1 <= health <= 6 and random.random() < near_death_chance:
        while pygame.mixer.get_busy():
            pygame.time.wait(100)
        sound_manager.add_to_queue(['medical', 'health', 'boophigh_near_death'], 'health_threshold_alerts')
        if random.random() < seek_medic_chance:
            sound_manager.add_to_queue(['medical', 'health', 'booplow_seek_medic'], 'health_threshold_alerts')
        sound_manager.play_next_in_queue()

    if 7 <= health <= 30 and random.random() < health_critical_chance:
        while pygame.mixer.get_busy():
            pygame.time.wait(100)
        sound_manager.add_to_queue(['medical', 'health', 'boophigh_health_critical'], 'health_threshold_alerts')
        if random.random() < seek_medic_chance:
            sound_manager.add_to_queue(['medical', 'health', 'booplow_seek_medic'], 'health_threshold_alerts')
        sound_manager.play_next_in_queue()

    if 31 <= health <= 50 and random.random() < seek_medic_chance:
        while pygame.mixer.get_busy():
            pygame.time.wait(100)
        sound_manager.add_to_queue(['medical', 'health', 'booplow_seek_medic'], 'health_threshold_alerts')
        sound_manager.play_next_in_queue()
        

# 	# if:
# 	# 	health <= 50 - play seek_medic.wav after "medical\detected\physical" voiceline.
# 	# elif:
# 	# 	health <= 30 - play health_critical.wav after "medical\detected\physical" voiceline.
# 	# elif:
# 	# 	health <= 6 - play near_death.wav after "medical\detected\physical" voiceline.


#---- Morphine Shot
def morphine_shot(thud):
    morphine_chance = 1.0  # 30% chance
    if random.random() < morphine_chance:
        while pygame.mixer.get_busy():
            pygame.time.wait(100)
        sound_manager.add_to_queue(['medical', 'administered', 'booplow_morphine_shot'], 'medical_administer')
        sound_manager.play_next_in_queue()


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
            "\n'heal':    heals 25HP"
            "\n'repair':  repairs 25AP"
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
            
            armor, health = physical_hit(armor, health, thud)

            if health > 0:  #  Calls hit_sound as long as health is above 0
                hit_sound(thud)

            if health > 0:  # If health is still above 0 after physical hit
                if armor <= 0 and not armor_was_compromised:  # Only call armor_compromised if armor is not already compromised
                    armor_compromised(armor)  # Checks if armor is compromised after each hit
                    armor_was_compromised = True  # Set flag to prevent armor_compromised from being called twice

                if health > 0:
                    health_threshold_alerts(health)
            
                if thud >= 25:  # Only call morphine_shot if thud is 25 or higher
                    morphine_shot(thud)

            print(f"---- {'LIGHT' if thud < 25 else 'HEAVY'} Thud, -{thud} physical damage")

        #-----

        case 'hazard':
            # just_had_hazard = True
            hazard = random.randint(1, 40)
            energy_type = random.choice(energy_types)

            armor, health = energy_hit(armor, health, hazard)

            if health > 0:
                if armor <= 0 and not armor_was_compromised:
                    armor_compromised(armor)
                    armor_was_compromised = True 
            
            print(f"---- {energy_type.title()} hazard, -{hazard} energy damage")

        #-----

        case 'heal':
            health = apply_restoration(health, 25, 100)
            print("---- Health has been restored!")

        #-----

        case 'repair':
            armor = apply_restoration(armor, 25, 100)
            armor_was_compromised = False  # Reset the flag to allow armor_compromised to be called again.
            print("---- Armor has been repaired!")

        #-----

        case 'quit':
            print("HEV Suit shutting down.")
            break

        #-----

        case _:
            print("Unknown command. Please enter 'hit', 'heal', 'repair' or 'quit'.")

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

# Make a list of all the SFX that'll be used for Combat Mode.
#(Probably unecessary now since there is a function that dynamically creates a dictionary related to the HEVcommon directory.)

# "Boops & Fuzz": Functions could handle playing the correct sound corresponding to the health level.
# "Suit Advise": Functions could handle the suit advice logic, triggering the appropriate advice based on the current health level.
# "Suit Aid": Functionality could handle scenarios involving heavy hits.
# "Timed Alerts - For Energy Damage": You could implement functionality for the energy damage inflicted at fixed time intervals.
# Focus on one of these areas at a time, preferably one that has dependencies on others.
# Note this whole program will need to be written in Arduino

# Need a Sound Manager that allows me to specify what sounds can play immediately and at the same time.
# And also it should be able to queue up sounds that can play after the current sound.
## The Sound Manager's queue system should be set up so that it can release multiple sounds in a row
## after the current sound has finished playing from play_sound_immediately.
# It also needs to respect the current system of loading sounds, withn the load_sound function.

# Redo hit_sounds function to work inline with new Sound Manager.
# It needs to perform the same way it does currently,
# with a 40% chance of playing a follow-up sound after a heavy or light hit.

# Redo armor_compromised function to work inline with new Sound Manager.
# It needs to be queued up to play after the current sound.

# Same principle applies to hazard sounds, whenever a hazard is triggered, it should be queued up to play after the current sound.

# If either armor_compromised sound or hazard sound is playing, NO sound should be able to play until they are finished.