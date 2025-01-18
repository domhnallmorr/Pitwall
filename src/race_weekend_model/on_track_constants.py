

DRIVER_SPEED_FACTOR = 2_0 # factor, 20 means a driver with 0 speed is 2s slower than one with 100 speed rating
CAR_SPEED_FACTOR = 5_0 # factor, 50 means a car with 0 speed is 5s slower than one with 100 speed rating

DIRTY_AIR_THRESHOLD = 1_500 # in ms, 1_500 means dirty air comes into affect when running 1.5s behind car in front
DIRTY_AIR_EFFECT = 500 # in ms, 500 means car loses 0.5s in pace when running in dirty air

RETIREMENT_CHANCE = 20 # % chance of retiring
LAP_TIME_VARIATION = 700 # in ms, 700 means variation of 0.7s possible for a given laps

PIT_STOP_LOSS_RANGE = (3_800, 6_000) # in ms, random time taken to perform pitstops

LAP1_TIME_LOSS = 6_000 # in ms, how much longer lap 1 takes compared to a normal lap
LAP1_TIME_LOSS_PER_POSITION = 1_000 # in ms, how much longer lap 1 takes, per position down the field

MAX_SPEED = 100 # the speed scale for car and driver is between 0 and 100, 100 defined here as the max value