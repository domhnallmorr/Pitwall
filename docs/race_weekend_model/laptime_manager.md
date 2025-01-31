# LapTimeManager Documentation

## Overview
The `LapTimeManager` class is responsible for calculating and managing lap times for each participant in the race. It takes into account various factors such as driver skill, driver consistency, car performance, car condition (fuel/tyres), and randomness to simulate real-world lap times.

Note, a participant is a combination of a specific car and driver.

## How Lap Times Are Calculated

### 1. Base Lap Time Calculation
The foundation of any lap time is the base lap time of the track. It essentially represents the fastest possible time a participant can achieve. It is dictatated by:
- **Driver speed**: A faster driver reduces lap time.
- **Car speed**: A more powerful car also lowers the lap time.

Formula:
```python
self.base_laptime = self.track_model.base_laptime
self.base_laptime += (MAX_SPEED - self.driver.speed) * DRIVER_SPEED_FACTOR
self.base_laptime += (MAX_SPEED - self.car_model.speed) * CAR_SPEED_FACTOR
```
- A driver with a **0 speed rating** is considered **2 seconds** slower than one with **100 speed**.
- A car with a **0 speed rating** is considered **5 seconds** slower than one with **100 speed**.

### 2. Lap Time Variation

Lap times are not constant due to natural driving inconsistencies. The variation is calculated as:

```python
additonal_laptime_variaton = int((1 - (self.driver.consistency / 100)) * LAP_TIME_VARIATION)
self.laptime_variation = LAP_TIME_VARIATION_BASE + additonal_laptime_variaton
```

- `LAP_TIME_VARIATION_BASE` is a fixed 300ms variation that applies to all drivers.
- `LAP_TIME_VARIATION` is an additional 400ms that applies depending on driver consistency.
- A driver with **100 consistency** has **0ms additional variation**, while a driver with **0 consistency** has the full **400ms additional variation**.

Below shows a laptime comparison of a driver with a consistency rating of 90 and 20.

![consistency](lap_time_consistency.png)

### 3. Calculating a Lap Time
Each lap time is determined using:

```python
random_time_loss = self.randomiser.random_laptime_loss()
self.laptime = self.base_laptime + random_time_loss + self.car_model.fuel_effect + self.car_model.tyre_wear + dirty_air_effect
```
Where:
- `random_time_loss` adds a realistic variation.
- `fuel_effect` accounts for added weight from fuel.
- `tyre_wear` increases the lap time as tires degrade.
- `dirty_air_effect` simulates aerodynamic disadvantage when following another car.

### 4. Pit Stop Time Adjustment
If a participant is **pitting**, the lap time is adjusted by adding:
```python
self.laptime += self.track_model.pit_stop_loss
self.laptime += self.participant.pitstop_times[-1]
```
This ensures pit stops have a realistic time penalty.

### 5. First Lap Time Calculation
The first lap is handled differently because cars start from a grid position and experience more traffic.
```python
random_time_loss = self.randomiser.random_lap1_time_loss()
self.laptime = self.track_model.base_laptime + LAP1_TIME_LOSS + (idx * LAP1_TIME_LOSS_PER_POSITION) + random_time_loss
```

Here, `idx` represents the car's position after turn 1, which increases lap time losses due to congestion. The intent of this calculation is to spread the field out after turn 1. No position changes after turn 1 can occur.

### 6. Adjusting Time When Overtaken
When a car is overtaken, its lap time is revised:
```python
self.laptime = revised_laptime
self.laptimes[-1] = revised_laptime
```

This ensures that the total time reflects the real-time loss from being passed.

## Summary of Factors Affecting Lap Times

| Factor                | Effect on Lap Time |
|-----------------------|-------------------|
| Track Base Lap Time  | Baseline for all calculations |
| Driver Speed        | Faster driver decreases lap time |
| Car Speed          | Faster car decreases lap time |
| Random Variation   | Introduces unpredictability |
| Fuel Load         | Higher fuel increases lap time |
| Tyre Wear         | More wear increases lap time |
| Dirty Air Effect  | Following cars experience increased lap times |
| Pit Stop          | Adds pit stop loss time |
| First Lap Position | Further back increases lap time |
| Being Overtaken   | Adjusts lap time to reflect time lost |

This class provides a realistic simulation of lap times based on multiple contributing factors.

