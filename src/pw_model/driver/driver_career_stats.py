from dataclasses import dataclass, field

@dataclass
class DriverCareerStats:
    starts: int = 0
    championships: int = 0
    wins: int = 0

    def update_after_race(self, position: int):
        """
        Call this method after each race to update the driver's statistics.
        For now, it only increments the 'starts' counter, but you can add more
        logic here if you want to track other stats in the future.
        """
        if position == 0:
            self.wins += 1

        self.starts += 1
        
    def update_after_season(self, position: int):
        """
        Call this method after each season to update the driver's statistics.
        For now, it only increments the 'championships' counter, but you can add more
        logic here if you want to track other stats in the future.
        """
        if position == 0:
            self.championships += 1