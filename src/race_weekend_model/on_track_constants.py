

DRIVER_SPEED_FACTOR = 2_0 # factor, 20 means a driver with 0 speed is 2s slower than one with 100 speed rating
CAR_SPEED_FACTOR = 5_0 # factor, 50 means a car with 0 speed is 5s slower than one with 100 speed rating

DIRTY_AIR_THRESHOLD = 1_500 # in ms, 1_500 means dirty air comes into affect when running 1.5s behind car in front
DIRTY_AIR_EFFECT = 500 # in ms, 500 means car loses 0.5s in pace when running in dirty air

RETIREMENT_CHANCE = 27 # % chance of retiring due to mechanical failure
CRASH_CHANCE = 21 # % chance of crashing out

LAP_TIME_VARIATION_BASE = 300 # in ms, lap time variation for every driver, independant of consistency attribute
LAP_TIME_VARIATION = 400 # in ms, driver with 0 consistency has 0.4s add to laptime variation, driver with 100 consistency has 0.0s added

PIT_STOP_LOSS_RANGE = (3_800, 6_000) # in ms, random time taken to perform pitstops

LAP1_TIME_LOSS = 6_000 # in ms, how much longer lap 1 takes compared to a normal lap
LAP1_TIME_LOSS_PER_POSITION = 1_000 # in ms, how much longer lap 1 takes, per position down the field

MAX_SPEED = 100 # the speed scale for car and driver is between 0 and 100, 100 defined here as the max value

POWER_SENSITIVITY = 2_000 # 

QUALIFYING_EXCEPTIONAL_CHANCE_FACTOR = 0.05  # Base chance per qualifying point (5%)
QUALIFYING_EXCEPTIONAL_BOOST_MAX = 400  # Maximum boost for exceptional laps (500ms = 0.5s)

TYRE_GRIP_BOOST = 2_000 # in ms, means a tyre with 100 grip rating gives 2s boost to laptime
TYRE_WEAR_INCREASE = 50 # in ms, means a tyre with 0 wear rating gives 0.05s increase to wear
