from app.models.email import EmailCategory
from app.models.finance import TransactionCategory
from app.models.state import ChassisDesignStage, GameState, PlayerCarDevelopment


class PlayerCarDevelopmentManager:
    STAGES = [
        ("design", "Design"),
        ("cfd", "CFD Simulation"),
        ("model", "Model Design"),
        ("wind_tunnel", "Wind Tunnel"),
    ]
    DESIGN_STAFF_BASELINE = 60
    DESIGNER_WEEKLY_PROJECT_COST = 400
    SCOPES = {"current_year", "next_year"}

    def _design_capacity_for_team(self, team) -> int:
        design_staff = getattr(team, "design_staff", None)
        engineering_staff = getattr(team, "engineering_staff", None)
        mechanics_staff = getattr(team, "mechanics_staff", None)
        if any(int(value or 0) > 0 for value in (design_staff, engineering_staff, mechanics_staff)):
            return int(design_staff or 0)
        return int(getattr(team, "workforce", 0) or 0)

    def _get_td_skill(self, state: GameState, team_id: int) -> int:
        director = next((td for td in state.technical_directors if td.team_id == team_id), None)
        return max(0, min(100, int(getattr(director, "skill", 50) if director else 50)))

    def _raw_stage_progress_per_week(self, state: GameState, project: PlayerCarDevelopment) -> float:
        team = state.player_team
        if not team:
            return 0.0
        assigned_designers = max(0, int(project.assigned_designers or 0))
        if assigned_designers <= 0:
            return 0.0
        facilities = max(0, min(100, int(getattr(team, "facilities", 0) or 0)))
        td_skill = self._get_td_skill(state, team.id)
        facilities_multiplier = 0.35 + (0.65 * (facilities / 100))
        td_multiplier = 0.75 + (0.50 * (td_skill / 100))
        return (assigned_designers / 40) * facilities_multiplier * td_multiplier

    def _stage_progress_per_week(self, assigned_designers: int) -> int:
        bounded = max(0, int(assigned_designers or 0))
        if bounded <= 0:
            return 0
        return max(0, min(2, round(bounded / 40)))

    def _weekly_cost(self, assigned_designers: int) -> int:
        return max(0, int(assigned_designers or 0)) * self.DESIGNER_WEEKLY_PROJECT_COST

    def _normalize_scope(self, scope: str | None) -> str:
        normalized = (scope or "current_year").strip().lower()
        if normalized not in self.SCOPES:
            raise ValueError("Invalid chassis design scope")
        return normalized

    def _get_project(self, state: GameState, scope: str | None) -> PlayerCarDevelopment | None:
        normalized_scope = self._normalize_scope(scope)
        if normalized_scope == "next_year":
            return state.player_next_year_car_development
        return state.player_car_development

    def _set_project(self, state: GameState, project: PlayerCarDevelopment) -> None:
        if project.scope == "next_year":
            state.player_next_year_car_development = project
        else:
            state.player_car_development = project

    def _clear_project(self, state: GameState, scope: str) -> None:
        if scope == "next_year":
            state.player_next_year_car_development = None
        else:
            state.player_car_development = None

    def _active_projects(self, state: GameState) -> list[PlayerCarDevelopment]:
        return [
            project
            for project in [
                self._normalize_project(state, "current_year"),
                self._normalize_project(state, "next_year"),
            ]
            if project and project.active and not project.completed
        ]

    def _fresh_stages(self) -> list[ChassisDesignStage]:
        return [
            ChassisDesignStage(key=key, label=label)
            for key, label in self.STAGES
        ]

    def _normalize_project(self, state: GameState, scope: str | None = "current_year") -> PlayerCarDevelopment | None:
        project = self._get_project(state, scope)
        if project is None:
            return None
        normalized_scope = self._normalize_scope(scope)
        if project.completed and normalized_scope == "current_year":
            self._clear_project(state, normalized_scope)
            return None
        if not project.stages:
            project.stages = self._fresh_stages()
            project.current_stage_index = 0
            project.name = project.name or "Current Chassis Upgrade"
            project.scope = project.scope or "current_year"
        if not getattr(project, "allocation_percent", 0) and getattr(project, "assigned_designers", 0):
            team = state.player_team
            capacity = self._design_capacity_for_team(team) if team else 0
            project.allocation_percent = min(100, round((project.assigned_designers / capacity) * 100)) if capacity else 0
        project.current_stage_index = max(0, min(project.current_stage_index, len(project.stages) - 1))
        return project

    def _refresh_project_staffing(self, state: GameState, project: PlayerCarDevelopment) -> None:
        team = state.player_team
        capacity = self._design_capacity_for_team(team) if team else 0
        project.allocation_percent = max(0, min(100, int(project.allocation_percent or 0)))
        project.assigned_designers = round(capacity * project.allocation_percent / 100)
        project.weekly_cost = self._weekly_cost(project.assigned_designers)

    def _allocated_percent_except(self, state: GameState, scope: str) -> int:
        return sum(
            int(project.allocation_percent or 0)
            for project in self._active_projects(state)
            if project.scope != scope
        )

    def _quality_score(self, state: GameState, project: PlayerCarDevelopment) -> int:
        team = state.player_team
        if not team:
            return 0
        raw_progress = sum(max(0, min(10, int(stage.progress or 0))) for stage in project.stages)
        progress_score = raw_progress * 2
        td_bonus = round((self._get_td_skill(state, team.id) - 50) / 5)
        facility_bonus = round((max(0, min(100, int(team.facilities or 0))) - 50) / 10)
        return max(1, min(100, progress_score + td_bonus + facility_bonus))

    def _speed_delta_for_quality(self, quality_score: int) -> int:
        if quality_score >= 85:
            return 7
        if quality_score >= 70:
            return 5
        if quality_score >= 50:
            return 3
        if quality_score >= 25:
            return 2
        return 1

    def _risk_for_quality(self, quality_score: int) -> str:
        if quality_score >= 70:
            return "Low"
        if quality_score >= 40:
            return "Medium"
        return "High"

    def _payload(self, state: GameState, project: PlayerCarDevelopment) -> dict:
        self._refresh_project_staffing(state, project)
        quality_score = self._quality_score(state, project)
        current_stage = project.stages[project.current_stage_index] if project.stages else None
        is_final_stage = project.current_stage_index >= len(project.stages) - 1
        can_finish_stage = bool(
            project.active
            and current_stage is not None
            and int(current_stage.progress or 0) > 0
        )
        return {
            "active": project.active,
            "scope": project.scope,
            "name": project.name,
            "year": project.year,
            "current_stage_index": project.current_stage_index,
            "current_stage_key": current_stage.key if current_stage else None,
            "current_stage_label": current_stage.label if current_stage else None,
            "stages": [stage.model_dump() for stage in project.stages],
            "assigned_designers": project.assigned_designers,
            "allocation_percent": project.allocation_percent,
            "progress_carry": project.progress_carry,
            "available_allocation_percent": max(0, 100 - self._allocated_percent_except(state, project.scope)),
            "weekly_cost": project.weekly_cost,
            "paid": project.paid,
            "completed": project.completed,
            "quality_score": quality_score,
            "projected_speed_delta": self._speed_delta_for_quality(quality_score),
            "risk": self._risk_for_quality(quality_score),
            "can_finish_stage": can_finish_stage,
            "finish_action_label": "Complete Upgrade" if is_final_stage else "Finish Stage",
        }

    def get_empty_project_payload(self, state: GameState | None = None, scope: str | None = "current_year") -> dict:
        normalized_scope = self._normalize_scope(scope)
        design_capacity = 0
        if state and state.player_team:
            design_capacity = self._design_capacity_for_team(state.player_team)
        return {
            "active": False,
            "scope": normalized_scope,
            "name": None,
            "year": (getattr(state, "year", None) + 1) if state and normalized_scope == "next_year" else (getattr(state, "year", None) if state else None),
            "current_stage_index": 0,
            "current_stage_key": None,
            "current_stage_label": None,
            "stages": [stage.model_dump() for stage in self._fresh_stages()],
            "assigned_designers": 0,
            "allocation_percent": 0,
            "progress_carry": 0.0,
            "available_allocation_percent": max(0, 100 - sum(int(project.allocation_percent or 0) for project in self._active_projects(state))) if state else 100,
            "designers_available": design_capacity,
            "weekly_cost": 0,
            "paid": 0,
            "completed": False,
            "quality_score": 0,
            "projected_speed_delta": 0,
            "risk": "None",
            "can_finish_stage": False,
            "finish_action_label": "Finish Stage",
        }

    def get_payload(self, state: GameState) -> dict:
        design_capacity = self._design_capacity_for_team(state.player_team) if state.player_team else 0
        current_project = self._normalize_project(state, "current_year")
        next_project = self._normalize_project(state, "next_year")
        current_payload = self._payload(state, current_project) if current_project else self.get_empty_project_payload(state, "current_year")
        next_payload = self._payload(state, next_project) if next_project else self.get_empty_project_payload(state, "next_year")
        payload = {
            "active": bool(current_payload.get("active") or next_payload.get("active")),
            "designers_available": design_capacity,
            "allocated_percent": sum(int(project.allocation_percent or 0) for project in self._active_projects(state)),
            "projects": {
                "current_year": current_payload,
                "next_year": next_payload,
            },
        }
        # Backward-compatible current-year fields for older renderer/tests.
        payload.update(current_payload)
        payload["designers_available"] = design_capacity
        return payload

    def start(self, state: GameState, scope: str | None = None) -> PlayerCarDevelopment:
        normalized_scope = self._normalize_scope(scope)
        existing = self._normalize_project(state, normalized_scope)
        if existing:
            if existing.active:
                raise ValueError("A chassis design project is already active")
            if existing.completed:
                self._clear_project(state, normalized_scope)

        team = state.player_team
        if not team:
            raise ValueError("No player team assigned")

        remaining_allocation = max(0, 100 - self._allocated_percent_except(state, normalized_scope))
        project = PlayerCarDevelopment(
            active=True,
            scope=normalized_scope,
            name="Current Chassis Upgrade" if normalized_scope == "current_year" else f"{state.year + 1} Chassis",
            year=state.year if normalized_scope == "current_year" else state.year + 1,
            current_stage_index=0,
            stages=self._fresh_stages(),
            allocation_percent=remaining_allocation,
        )
        self._refresh_project_staffing(state, project)
        self._set_project(state, project)
        state.add_email(
            sender="Technical Department",
            subject=f"Chassis Design Started: {project.name}",
            body=(
                f"Design work has started.\n\n"
                f"Project: {project.name}\n"
                f"Designer allocation: {project.allocation_percent}% ({project.assigned_designers} designers)\n"
                f"Current stage: {project.stages[0].label}\n"
                "Each stage can be finished after at least one progress block, but more progress improves the final design."
            ),
            category=EmailCategory.GENERAL,
        )
        return project

    def set_allocation(self, state: GameState, scope: str | None, allocation_percent: int | None) -> PlayerCarDevelopment:
        normalized_scope = self._normalize_scope(scope)
        project = self._normalize_project(state, normalized_scope)
        if not project or not project.active:
            raise ValueError("No active chassis design project")
        if allocation_percent is None:
            raise ValueError("allocation_percent is required")
        requested = max(0, min(100, int(allocation_percent)))
        other_allocated = self._allocated_percent_except(state, normalized_scope)
        if requested + other_allocated > 100:
            raise ValueError(f"Designer allocation exceeds 100%; {100 - other_allocated}% is available")
        project.allocation_percent = requested
        self._refresh_project_staffing(state, project)
        return project

    def finish_current_stage(self, state: GameState, scope: str | None = "current_year") -> PlayerCarDevelopment:
        normalized_scope = self._normalize_scope(scope)
        project = self._normalize_project(state, normalized_scope)
        if not project or not project.active:
            raise ValueError("No active chassis design project")
        if not project.stages:
            raise ValueError("Chassis design project has no stages")

        stage = project.stages[project.current_stage_index]
        if int(stage.progress or 0) <= 0:
            raise ValueError("Current design stage needs at least one progress block before it can be finished")

        stage.completed = True
        if project.current_stage_index < len(project.stages) - 1:
            project.current_stage_index += 1
            return project

        team = state.player_team
        if not team:
            raise ValueError("No player team assigned")
        quality_score = self._quality_score(state, project)
        speed_delta = self._speed_delta_for_quality(quality_score)
        project.active = False
        project.completed = True
        project.quality_score = quality_score
        project.speed_delta = speed_delta
        project.risk = self._risk_for_quality(quality_score)
        if project.scope == "next_year":
            state.add_email(
                sender="Technical Department",
                subject=f"Next Year's Chassis Design Complete: +{speed_delta}",
                body=(
                    f"{project.name} design work has been completed.\n\n"
                    f"Quality score: {quality_score}\n"
                    f"Projected next-season gain: +{speed_delta}\n"
                    f"Risk: {project.risk}\n"
                    f"Total project spend: ${project.paid:,}"
                ),
                category=EmailCategory.GENERAL,
            )
            return project

        old_speed = team.car_speed
        team.car_speed = max(1, old_speed + speed_delta)
        state.add_email(
            sender="Technical Department",
            subject=f"Chassis Upgrade Complete: +{speed_delta}",
            body=(
                f"{project.name} has been completed and fitted to the current car.\n\n"
                f"Quality score: {quality_score}\n"
                f"Risk: {project.risk}\n"
                f"Car rating: {old_speed} -> {team.car_speed}\n"
                f"Total project spend: ${project.paid:,}"
            ),
            category=EmailCategory.GENERAL,
        )
        return project

    def _finish_full_stages(self, state: GameState, project: PlayerCarDevelopment) -> list[dict]:
        completed: list[dict] = []
        while project.active and project.stages:
            stage = project.stages[project.current_stage_index]
            if int(stage.progress or 0) < 10:
                break
            completed.append(
                {
                    "stage": stage.label,
                    "scope": project.scope,
                    "project": project.name,
                }
            )
            self.finish_current_stage(state, project.scope)
        return completed

    def process_week(self, state: GameState) -> dict | None:
        results = []
        for project in self._active_projects(state):
            result = self._process_project_week(state, project)
            if result:
                results.append(result)
        if not results:
            return None
        return {"status": "processed", "projects": results}

    def _process_project_week(self, state: GameState, project: PlayerCarDevelopment) -> dict | None:
        self._refresh_project_staffing(state, project)
        if not project or not project.active or project.completed:
            return None
        if not project.stages:
            return None

        stage = project.stages[project.current_stage_index]
        raw_progress = self._raw_stage_progress_per_week(state, project)
        project.progress_carry = max(0.0, float(project.progress_carry or 0.0)) + raw_progress
        progress_added = min(2, int(project.progress_carry))
        project.progress_carry -= progress_added
        if progress_added <= 0:
            return {
                "status": "blocked",
                "project": project.name,
                "scope": project.scope,
                "stage": stage.label,
                "progress": stage.progress,
                "raw_progress": raw_progress,
                "progress_carry": project.progress_carry,
            }

        old_progress = max(0, int(stage.progress or 0))
        stage.progress = min(10, old_progress + progress_added)
        charge = max(0, int(project.weekly_cost or 0))
        if charge:
            state.finance.add_transaction(
                week=state.calendar.current_week,
                year=state.year,
                amount=-charge,
                category=TransactionCategory.DEVELOPMENT,
                description=f"Chassis design ({project.name}) weekly payment",
                event_name=None,
                event_type=None,
                circuit_country=None,
            )
            project.paid += charge

        completed_stages = self._finish_full_stages(state, project)
        return {
            "status": "in_progress",
            "project": project.name,
            "scope": project.scope,
            "stage": stage.label,
            "progress_before": old_progress,
            "progress_after": stage.progress,
            "progress_added": stage.progress - old_progress,
            "raw_progress": raw_progress,
            "progress_carry": project.progress_carry,
            "completed_stages": completed_stages,
            "project_completed": project.completed,
            "paid": project.paid,
        }

    def apply_next_year_project_for_rollover(self, state: GameState) -> dict | None:
        project = self._normalize_project(state, "next_year")
        if not project or not project.completed:
            return None
        if project.year != state.year:
            return None
        team = state.player_team
        if not team:
            return None
        old_speed = team.car_speed
        team.car_speed = max(1, old_speed + int(project.speed_delta or 0))
        state.add_email(
            sender="Technical Department",
            subject=f"New Chassis Introduced: {project.name}",
            body=(
                f"The completed {project.name} has been introduced for {state.year}.\n\n"
                f"Car rating: {old_speed} -> {team.car_speed}\n"
                f"Design quality: {project.quality_score}\n"
                f"Risk: {project.risk}"
            ),
            category=EmailCategory.SEASON,
        )
        return {
            "project": project.name,
            "old_speed": old_speed,
            "new_speed": team.car_speed,
            "speed_delta": project.speed_delta,
            "quality_score": project.quality_score,
        }

    def reset_for_new_season(self, state: GameState) -> None:
        state.player_car_development = None
        state.player_next_year_car_development = None
