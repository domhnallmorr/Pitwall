import random

from app.models.state import GameState
from app.models.tyre_compound import TyreCompound
from app.models.tyre_supplier import TyreSupplier


class TyreCompoundManager:
    _QUALITY_CENTER = 72

    _GRIP_INNOVATION_WEIGHT = {
        "Hard": 0.55,
        "Medium": 0.8,
        "Soft": 1.0,
    }

    _WEAR_RELIABILITY_WEIGHT = {
        "Hard": 1.0,
        "Medium": 0.85,
        "Soft": 0.7,
    }

    _POSITIVE_EXECUTION_SPREAD = 10
    _NEGATIVE_EXECUTION_SPREAD = 18

    def generate_for_new_career(self, state: GameState, rng: random.Random | None = None) -> None:
        roller = rng or random.Random()
        state.season_tyre_compounds = {
            supplier.name: self._generate_supplier_compounds(supplier, state.year, roller)
            for supplier in state.tyre_suppliers
        }

    def _generate_supplier_compounds(
        self,
        supplier: TyreSupplier,
        year: int,
        rng: random.Random,
    ) -> list[TyreCompound]:
        quality = (supplier.resources - 50) / 50.0
        innovation = (supplier.innovation - 50) / 50.0
        reliability = (supplier.reliability - 50) / 50.0

        compounds: list[TyreCompound] = []
        for compound_name in ("Hard", "Medium", "Soft"):
            grip_execution = rng.randint(-self._NEGATIVE_EXECUTION_SPREAD, self._POSITIVE_EXECUTION_SPREAD)
            wear_execution = rng.randint(-self._NEGATIVE_EXECUTION_SPREAD, self._POSITIVE_EXECUTION_SPREAD)
            stiffness_execution = rng.randint(-self._NEGATIVE_EXECUTION_SPREAD, self._POSITIVE_EXECUTION_SPREAD)
            grip = self._clamp_rating(
                self._QUALITY_CENTER
                + round((quality * 4.0) + (innovation * 16.0 * self._GRIP_INNOVATION_WEIGHT[compound_name]))
                + grip_execution
            )
            wear = self._clamp_rating(
                self._QUALITY_CENTER
                + round((quality * 6.0) + (reliability * 10.0 * self._WEAR_RELIABILITY_WEIGHT[compound_name]))
                + wear_execution
            )
            stiffness = self._clamp_rating(
                self._QUALITY_CENTER
                + round((quality * 5.0) + (reliability * 6.0) - (innovation * 3.0))
                + stiffness_execution
            )
            compounds.append(
                TyreCompound(
                    supplier_name=supplier.name,
                    name=compound_name,
                    grip=grip,
                    wear=wear,
                    stiffness=stiffness,
                    year=year,
                )
            )
        return compounds

    @staticmethod
    def _clamp_rating(value: int) -> int:
        return max(1, min(100, value))
