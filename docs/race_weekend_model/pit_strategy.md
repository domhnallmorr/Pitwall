# PitStrategy Documentation

## Overview  
The `PitStrategy` class determines the optimal pit stop strategy for a race by calculating the number of stops and the specific laps on which they occur. The pit stop strategy is crucial in balancing fuel load, tire wear, and race pace to ensure an efficient race plan.

## How Pit Strategy is Determined  

### 1. Initializing Pit Strategy  
Upon initialization, the `PitStrategy` class determines:  
- **The total number of laps in the race**  
- **The number of planned pit stops (randomly chosen between 1, 2, or 3 stops)**  
- **The laps on which the stops occur**  

```python
class PitStrategy:
    def __init__(self, number_of_laps: int):
        self.number_of_laps = number_of_laps
        self.determine_number_of_stops()
        self.calculate_pitstop_laps()
```

- The `number_of_laps` parameter is provided when creating an instance of `PitStrategy`.  
- The method `determine_number_of_stops()` assigns a random value between **1 and 3** for the number of pit stops.  
- The method `calculate_pitstop_laps()` then determines the specific laps for each pit stop.  

### 2. Determining the Number of Pit Stops  
The number of planned pit stops is determined randomly using:  

```python
def determine_number_of_stops(self) -> None:
    self.planned_stops = random.choice([1, 2, 3])
```

This randomization ensures variability in race strategies.  

### 3. Calculating Pit Stop Laps  
The exact laps for pit stops depend on the total race distance and the number of planned stops.  

```python
def calculate_pitstop_laps(self) -> None:
    half_distance = self.number_of_laps // 2
    third_distance = self.number_of_laps // 3
    quarter_distance = self.number_of_laps // 4

    self.pit1_lap = None
    self.pit2_lap = None
    self.pit3_lap = None

    if self.planned_stops == 1:
        self.pit1_lap = random.randint(half_distance - 5, half_distance + 5)

    elif self.planned_stops == 2:
        self.pit1_lap = random.randint(third_distance - 3, third_distance + 3)
        self.pit2_lap = random.randint((third_distance * 2) - 3, (third_distance * 2) + 3)

    elif self.planned_stops == 3:
        self.pit1_lap = random.randint(quarter_distance - 2, quarter_distance + 2)
        self.pit2_lap = random.randint(half_distance - 2, half_distance + 2)
        self.pit3_lap = random.randint((quarter_distance * 3) - 2, (quarter_distance * 3) + 2)
```

- **1-Stop Strategy:** The pit stop is placed near the halfway mark.  
- **2-Stop Strategy:** The pit stops are spread across **one-third and two-thirds** of the race distance.  
- **3-Stop Strategy:** The stops are placed at **one-quarter, one-half, and three-quarters** of the race distance.  
- A **random variance** of a few laps is introduced to simulate different strategies.  

### 4. Retrieving Pit Stop Data  
The `PitStrategy` class provides properties to retrieve pit stop lap numbers.  

#### Retrieving Pit Stop Laps  
```python
@property
def pit_laps(self) -> list[Optional[int]]:
    return [self.pit1_lap, self.pit2_lap, self.pit3_lap]
```

This returns a list of the laps when pit stops occur. If a stop is not needed (e.g., in a **1-stop race**, `pit2_lap` and `pit3_lap` will be `None`).  

#### Retrieving Lap Ranges  
```python
@property
def lap_ranges(self) -> list[Optional[int]]:
    laps = self.pit_laps
    laps.append(self.number_of_laps)
    return laps
```

This returns a list of lap numbers, including the final lap of the race, which can be useful in planning fuel loads and tire stints.  

## Summary of Pit Stop Strategy Logic  

| Pit Strategy | Pit Stops Placement |
|-------------|---------------------|
| 1-Stop Strategy | One stop near the halfway mark (±5 laps) |
| 2-Stop Strategy | Stops near 1/3 and 2/3 of the race (±3 laps) |
| 3-Stop Strategy | Stops near 1/4, 1/2, and 3/4 of the race (±2 laps) |

This pit strategy system allows for variability and realism in race strategy planning.  
