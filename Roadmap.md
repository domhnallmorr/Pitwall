# Roadmap

Objective for V2 is to flesh the game out, with a basic representation of the core game mechanics. Primary aim is to get features that affect the finanical aspect of the game.

Off track, this will include car development, sponsorship deals and engine/tyre suppliers. A basic representation of contract negotiation for drivers and senior staff will be added.

On track, extra details in the races will be added, such as crashes and driver mistakes. 

The bottom of this page includes a high level overview of additions for V2. Below, a specific roadmap to V1.20 is provided.

## V1.20


## UI Improvements

- [ ] Improve driver negotiation page
- [ ] Turn improve facility page into a modal


## Off Track Features

### Finance

- [ ] Add cost for engines (depened on works, supplier, customer deal)
- [ ] Add cost for tyres (depened on works, supplier, customer deal)
- [ ] Testing costs

### Car

- [ ] Add engine model, engine suppliers to be static, performance changes year by year
- [ ] Add tyre model, tyre suppliers to be static, performance changes year by year

### Sponsors

- [ ] Flesh out title sponsors in roster
- [ ] Title sponsors "retire" from the sport
- [ ] Commercial manager responsible for title sponsor
- [ ] AI teams change title sponsor


### Drivers

- [ ] Add qualifying attribute

### Contract Negotiations

- [ ] Top drivers refuse to sign for poorly ranked player team
- [ ] Add salary negotiation
		
### Other

- [ ] Flesh out team principals in roster
- [ ] Team principals retire
- [ ] AI change team principals
- [ ] Add test sesssions, player chooses testing to be done, car performance can improve


## On Track

- [ ] Tracks should have a engine power attribute
- [ ] Implement tyre grip/wear from tyre model
- [ ] Add commentary to Grand Prix model. Commentary to be displayed in Results window
- [ ] Add lap 1, turn 1 incidents, limited to spins for now


## Refactoring

- [ ] Reduce use of dictionaries to improve type hinting
- [ ] Improve use of enums
- [ ] Review and improve grand_prix_model
- [ ] Improve use of randomisers
- [ ] Improve load_roster function


# V2 Overview

- Car development
- Next years car development
- Engine/tyre suppliers
- Title sponsors
- Pay Drivers
- Reliability of car
- Car wear
- Additonal driver attributes
- Additonal details in races
	- Crashes
	- Mistakes
	- Overtaking difficulty per track
	- 1st turn incidents
- Save previous season results/stats
- Improve existing code base
- Improve pit strategies
- Pay off facility upgrades over time
- Split workforce into commercial, mechanics, design
- Basic contract negotiation for drivers/staff
- Track driver statistics
