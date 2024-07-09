=================================================================
=========================== HEV OS ==============================
=================================================================

This program closely replicates the audible response mechanics of the
HEV Suit in Half-Life (1998) by Valve.

Inputs:
	- hit 		- User recieves physical damage ranging from 1 - 50 hit points (HP).
	- hazard 	- User recieves energy damage ranging from 1 - 40 HP.
	- heal		- Heals the user's health by 15 (HP).
	- repair	- Repairs the suit's armor by 15 armor points (AP).
	- armor		- The suit's voice reads out the current armor value.
	- quit		- Exits the program.

========================   Health & Armor   ========================

- Health (health) and Armor (armor) have their own pools. Both range from 0 - 100.
  
- armor negates how much health gets subtracted from a physical hit. The original
  formula is as follows:
  (hit * 0.80 / 2)

- To explain this, armor will absorb 80% of the hit, divide it by 2 and deduct from the
  current armor value, up until the point of where the user is depleted of it,
  at which point 100% of the hit is commited to health instead.
  Regardless, whenever there is armor, health will take the remaining 20% of the hit.
  Even if the user has 100% armor, health is still affected when taking physical damage.

- Upon a hazard, damage goes straight to armor and health is totally unaffected. If there
  is 0 armor, hazard damage is applied to health instead.

********   Health Alerts   ********

- When health is at certain thresholds, there is a chance for 3 different voice lines to
  play:
	- if health > 30 and <= 50:
		play seek_medic.wav
	- elif health > 6 and <= 30:
		play health_critical.wav
	- elif health > 1 and <= 6:
		play near_death.wav

- By default, all 3 have a chance to play that can be configured in the top config:
	- seek_medic_chance - 50% chance
	- health_critical_chance - 65% chance
	- near_death_chance - 90% chance

- When health drops to 0, a death sound will play.

********   Armor Alerts   ********

- A small audible armor alarm will play if either a physical or energy hit greater than
  or equal to a value of 30 is rolled.

- If armor drops to 0, there is a 50% chance (default) that a voice line will play
  stating armor compromised.

========================   Hit - Physical Damage   ========================

- Upon a hit, the user will take damage ranging from 1 - 50.

- There are several different physical hit sounds, distinguished by either a major hit
   or a minor hit. One of them will randomly play.

- If the value of hit was greater than or equal to 25, a major hit sound
  will play. Otherwise a minor hit sound will play.

- There is a 40% chance (default) that a follow up voice line will play, alerting the
  user that either a major or minior hit has been detected.

- Additionally, there is a 44% chance (default) that if the aforementioned major hit
  detected line has played, the suit will play a voice line that administers a morphine
  shot.

- For example:
	if hit >= 25:
		play random major_hit.wav
		40% chance to play major_hit_detected.wav
		if major_detected.wav has played:
			44% chance to play morphine_shot.wav
	
	else:
		play random minor_hit.wav
		40% chance to play minor_hit_detected.wav

========================   Hazard - Energy Damage   ========================

- Upon a hazard, the suit will damage ranging from 1 - 40. Health is unaffected if there
  is armor.

- hazard damage gets applied to health only when there is 0 armor.

- Randomly, 1 of 6 hazard sounds will play. The hazards themeselves do not currently
  have a sound effect, so a voice line will play detecting the random hazard.

- Current hazard types are [heat, shock, bio hazard, blood toxins, chemical, radiation]

- If either of [bio hazard, blood toxins, chemical, radiation] voice lines play, there is
  a 50% chance (default) that an additional voice line will play, stating that vital signs
  are dropping.

========================   Healing and Repairing   ========================

- There are 2 commands to replenish health and armor. They are:
	- heal
	- repair

- Both items heal/repair by 15, individually.

- Both items play their respective sounds as found in the game.

- Both also play a different sound if trying to heal/repair when that value is at max (100).

- When repairing armor and after the armor repair sound has played, the suit will dynamically
  play a voice line stating the armor value once repaired. This is read out in increments of 5,
  which is rounded to the nearest multiple of 5, this is a similar behaviour to how it works
  in the original.

========================   Armor Readout   ========================

- Upon armor readouts, the suit will play a couple of boop varying noises and play a dynamic
  voice line that reads the exact current armor value.

- If armor is 0, another sound will play to signal that there is no armor currently left.