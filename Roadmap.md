# Roadmap

Objective for V2 is to flesh the game out, with a basic representation of the core game mechanics.

Off track, this will include car development, sponsorship deals and engine/tyre suppliers. A basic representation of contract negotiation for drivers and senior staff will be added.

On track, extra details in the races will be added, such as crashes and driver mistakes. A timing screen view will be added to view the sessions. 

The bottom of this page includes a high level overview of additions for V2. Below, a specific roadmap to V1.10 is provided.

## V1.10


## UI Improvements

Add country flags
Need page for each track (overtaking difficulty, engine sensitivity and any other track details)
Improve Email page
Improve team selection page
Add engine page

## Off Track Features

### Finance

Add projections for year
Race costs should vary by distance from Europe
Crash damage costs
Track profit/loss

### Car

Car should be split into engine and chassis
Track should have an attribute on how sensitive performance is to engine performance
Add engine class
	power
	hard code engine suppliers for each team
	random change each season

### Sponsors

Add title sponsors
	Dependent on commercial manager
Have "other sponsorship" attribute

### Drivers

Add consistency attribute
	feed into laptime calculation
Track driver statistics

### Contract Negotiations

Drivers take some time to respond to offers
		
### Other

Add team principal as staff member to AI teams
Replace real driver names with fake names
Add winner column to calendar page
Add track lengths

## On Track

Add overtake difficulty attribute to tracks
Add random driver crashes
Improve AI pit strategies
Proper base laptime for each track

## Refactoring

Add a custom widget for datatables
Reduce use of dictioaries to improve type hinting
Improve use of enums
Review and improve grand_prix_model
Improve use of randomisers


# V2 Overview

In season testing
Car development
Next years car development
Engine/tyre customer/partner/works deals
Title sponsors
Wet races (weather will be static)
Pay Drivers
Reliability of various components
Car wear
Additonal driver attributes
Additonal details in races
	Crashes
	Mistakes
	Punctures
	Overtaking difficulty per track
	broken front wing
Add practice session
Add timing screen page for on-track sessions
Save previous season results/stats
Improve existing code base
Images of drivers/staff
Pay off facility upgrades over time
Split workforce into commercial, mechanics, design
Basic contract negotiation for drivers/staff
