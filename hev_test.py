### version 5.3 ###
import random
import math
armor = 100
health = 100


def calculate_physical(armor, health, thud):
    if armor >= thud:
        armor -= thud
        # Applies 20% of thud to health if armor is enough.
        health -= math.floor(thud * 0.20)
    else:
        # When thud exceeds armor, armor absorbs as much as it can (its current value),
        # and the excess physical damage goes to health.
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


def enforce_non_negative(armor, health):
    armor = max(armor, 0)
    health = max(health, 0)
    return armor, health


def physical_hit(armor, health, thud):
    armor, health = calculate_physical(armor, health, thud)
    armor, health = enforce_non_negative(armor, health)
    return armor, health


def energy_hit(armor, health, hazard):
    armor, health = calculate_energy(armor, health, hazard)
    armor, health = enforce_non_negative(armor, health)
    return armor, health


def apply_restoration(current_value, amount, max_value):
    updated_value = current_value + amount
    if updated_value > max_value:
        updated_value = max_value
    return updated_value


while True:
    print("\nHEV Suit test ready. Enter:"
          "\n'hit':     physical attack between 1 - 50"
          "\n'hazard':  energy hazard between 1 - 40"
          "\n'heal':    heals 25HP"
          "\n'repair':  repairs 25AP"
          "\n'quit':    exits.")
    user_input = input()
    match user_input:
        case 'hit':
            thud = random.randint(1, 50)  # This updates thud value for each hit
            armor, health = physical_hit(armor, health, thud)
            print(f"---- {'Light' if thud < 25 else 'Heavy'} Thud, for {thud} physical damage")
        case 'hazard':
            hazard = random.randint(1, 40)  # This updates thud value for each hazard
            armor, health = energy_hit(armor, health, hazard)
            print(f"---- Hazard, for {hazard} energy damage")
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
    print("==== Remaining armor: ", armor)
    print("==== Remaining health: ", health)


# make a list of all the SFX that'll be used for Combat Mode

# Next steps could include:
# Creating functions for the health and armor regeneration actions.

# "Health & Armor": You've already implemented the basic functionality for this area, such as healing and damage.
# "Hit Detection - For Physical Damage": You'll need functions to handle light and heavy hits. You've already laid the groundwork for this! Adding some randomness to the physical damage can make it more dynamic.
# "Boops & Fuzz": Functions could handle playing the correct sound corresponding to the health level.
# "Suit Advise": Functions could handle the suit advice logic, triggering the appropriate advice based on the current health level.
# "Suit Aid": Functionality could handle scenarios involving heavy hits.
# "Timed Alerts - For Energy Damage": You could implement functionality for the energy damage inflicted at fixed time intervals.
# I suggest focusing on one of these areas at a time, preferably one that has dependencies on others. Which area are you eager to dive into? And do you perceive any function that you would require assistance with?
