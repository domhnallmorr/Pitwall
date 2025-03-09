from __future__ import annotations
from typing import TYPE_CHECKING, Union

from pw_model.senior_staff.senior_staff import SeniorStaff
from pw_model.pw_model_enums import StaffRoles

if TYPE_CHECKING:
    from pw_model.pw_base_model import Model
    from pw_model.team.team_model import TeamModel

class TeamPrincipalModel(SeniorStaff): # type: ignore
    def __init__(self,
              model: Model,
              name: str,
              age: int,
              skill: int,
              contract_length: int):
        
        super().__init__(model, name, age, skill, 0, contract_length) # salary is not used
        self.role = StaffRoles.TEAM_PRINCIPAL

    def __repr__(self) -> str:
        return f"TeamPrincipalModel <{self.name}>"

    @property
    def team_model(self) -> Union[None, TeamModel]:
        current_team = None

        for team in self.model.teams:
            if self.name == team.team_principal:
                current_team = team
                break

        return current_team