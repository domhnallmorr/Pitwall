from dataclasses import dataclass, field

@dataclass
class DriverCareerStats:
    starts: int = 0

    def update_after_race(self):
        """
        Call this method after each race to update the driver's statistics.
        For now, it only increments the 'starts' counter, but you can add more
        logic here if you want to track other stats in the future.
        """
        self.starts += 1