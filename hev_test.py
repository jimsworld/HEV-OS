### version 5.8 ###

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


####################################

############ Loads HEVcommon ############

def load_sounds(directory):
    sounds = {}
    for root, dirs, files in os.walk(directory):
        # Path from root to current directory
        path_parts = root.split(os.sep)
        
        # Initialize a temporary dictionary based on path_parts
        temp_dict = sounds
        for part in path_parts[1:]:  # Skip the first part, as it's the main directory
            temp_dict = temp_dict.setdefault(part, {})
        
        # Load each .wav file in the current directory
        for file in files:
            if file.endswith('.wav'):
                # Form the key from the file name without its extension
                key = file[:-4]
                # Load the sound and assign it to the correct place in the nested dictionary
                temp_dict[key] = pygame.mixer.Sound(os.path.join(root, file))
    return sounds


all_sounds = load_sounds('HEVcommon')
# Example usage:
# all_sounds['subfolder']['another_subfolder']['sound_key'].play()


####################################

############ Plays HEVcommon ############

def play_sound(sound_path):
    try:
        # Start with the base dictionary.
        current_dict = all_sounds
        # Iterate through the parts of the path to navigate the nested dictionaries.
        for key in sound_path:
            current_dict = current_dict[key]
        # Play the sound at the end of the path.
        current_dict.play()
    except KeyError:
        # Handle the case where any part of the path is incorrect.
        print(f"Warning: The sound at path '{sound_path}' does not exist.")


####################################

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


####################################

############ Enforce Non-Negative Values ############

def enforce_non_negative(armor, health):
    armor = max(armor, 0)
    health = max(health, 0)
    return armor, health


####################################

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


####################################

############ Sound Engine ############

#---- Hit Sounds
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
        play_sound(selected_heavy_hit)

        chance_to_play = 1.0  # 40% chance
        if random.random() < chance_to_play:
            major_fracture_lacerations = major_followup_sound[selected_heavy_hit]  # Lookup the corresponding sound
            play_sound(major_fracture_lacerations)

    else:
        minor_followup_sound = {
            ('hit', 'pl_pain2'): ['medical', 'detected', 'physical', 'boopmid_old_minor_fracture'],
            ('hit', 'pl_pain6'): ['medical', 'detected', 'physical', 'boopmid_old_minor_lacerations'],
            ('hit', 'hc_attack1'): ['medical', 'detected', 'physical', 'boopmid_old_minor_lacerations'],
            ('hit', 'claw_strike3'): ['medical', 'detected', 'physical', 'boopmid_old_minor_lacerations']
        }

        light_hits = list(minor_followup_sound.keys())
        selected_light_hit = random.choice(light_hits)
        play_sound(selected_light_hit)

        chance_to_play = 1.0
        if random.random() < chance_to_play:
            minor_fracture_lacerations = minor_followup_sound[selected_light_hit]
            play_sound(minor_fracture_lacerations)


#---- HEV Compromised Complete
armor_compromised_played = False

def armor_compromised(armor):
    global armor_compromised_played
    chance_to_play = 1.0  # 50% chance
    if armor <= 0 and random.random() < chance_to_play and not armor_compromised_played:
        while pygame.mixer.get_busy():
            pygame.time.wait(100) # Wait for 100 milliseconds.
        play_sound(['armor', 'armor_compromised_complete'])
        armor_compromised_played = True

####################################

############ Command Input and Console Output ############

while True:

    #Instructions
    if show_instructions:
        print("\nHEV Suit test ready. Available commands:"
            "\n'hit':     physical attack between 1 - 50"
            "\n'hazard':  energy hazard between 1 - 40"
            "\n'heal':    heals 25HP"
            "\n'repair':  repairs 25AP"
            "\n'quit':    exits.")
        show_instructions = False  # Stops repetitive instructions

    #User Input
    user_input = input("\nEnter command: ")
    match user_input:

        case 'hit':
            hazard_turn_counter += random.randint(1, 5)  # Increment the hazard counter
            thud = random.randint(1, 50)  # This randomises damage value for each hit
            if health > 0:  # Adds Hit Sound as long as health is above 0
                hit_sound(thud)
            armor, health = physical_hit(armor, health, thud)
            print(f"---- {'LIGHT' if thud < 25 else 'HEAVY'} Thud, -{thud} physical damage")

        case 'hazard':
            hazard = random.randint(1, 40)  # This randomises energy value for each hazard
            energy_type = random.choice(energy_types)
            armor, health = energy_hit(armor, health, hazard)
            print(f"---- {energy_type.title()} hazard, -{hazard} energy damage")

        case 'heal':
            health = apply_restoration(health, 25, 100)
            print("---- Health has been restored!")

        case 'repair':
            armor = apply_restoration(armor, 25, 100)
            print("---- Armor has been repaired!")

        case 'quit':
            print("HEV Suit shutting down.")
            break

        case _:
            print("Unknown command. Please enter 'hit', 'heal', 'repair' or 'quit'.")

    #Random Hazard
    if hazard_turn_counter >= hazard_turn:  # Triggers a random hazard when threshold is met
        hazard = random.randint(1, 40)  # This randomises energy value for each hazard
        energy_type = random.choice(energy_types)
        armor, health = energy_hit(armor, health, hazard)
        print(f"---- {energy_type.title()} hazard, for {hazard} energy damage")
        hazard_turn_counter = 0

    #Armor and Health Readouts
    print("==== Remaining armor: ", armor)
    print("==== Remaining health: ", health)

    #-Sound Playback-
    #-HEV Compromised Complete-
    armor_compromised(armor)
    if armor > 0:
        armor_compromised_played = False


####################################

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

# Redo hit_sounds function to work inline with new Sound Manager.
# It needs to perform the same way it does currently,
# with a 40% chance of playing a follow-up sound after a heavy or light hit.

# Redo armor_compromised function to work inline with new Sound Manager.
# It needs to be queued up to play after the current sound.

# Same principle applies to hazard sounds, whenever a hazard is triggered, it should be queued up to play after the current sound.

# If either armor_compromised sound or hazard sound is playing, NO sound should be able to play until it's finished.