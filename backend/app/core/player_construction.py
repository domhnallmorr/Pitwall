from app.models.chassis import Chassis
from app.models.email import EmailCategory
from app.models.finance import TransactionCategory
from app.models.state import GameState, PlayerCarDevelopment, PlayerConstructionProject


class PlayerConstructionManager:
    SCOPES = {"current_year", "next_year"}
    CURRENT_YEAR_MIN_UPGRADE_COST = 20_000
    CURRENT_YEAR_MAX_UPGRADE_COST = 300_000
    CURRENT_YEAR_MIN_DESIGN_BLOCKS = 4
    CURRENT_YEAR_MAX_DESIGN_BLOCKS = 40
    NEXT_YEAR_CHASSIS_UNIT_COST = 500_000
    CURRENT_YEAR_PROGRESS_REQUIRED = 10
    NEXT_YEAR_PROGRESS_REQUIRED = 24
    NEXT_YEAR_RACE_READY_CHASSIS_REQUIRED = 2
    MINOR_UPGRADE_FAST_WEEKS = 2.0
    MINOR_UPGRADE_SLOW_WEEKS = 4.0
    MAJOR_UPGRADE_FAST_WEEKS = 4.0
    MAJOR_UPGRADE_SLOW_WEEKS = 8.0

    def _normalize_scope(self, scope: str | None) -> str:
        normalized = (scope or "current_year").strip().lower()
        if normalized not in self.SCOPES:
            raise ValueError("Invalid construction scope")
        return normalized

    def _engineering_capacity_for_team(self, state: GameState) -> int:
        team = state.player_team
        if not team:
            return 0
        engineering_staff = int(getattr(team, "engineering_staff", 0) or 0)
        if engineering_staff > 0:
            return engineering_staff
        return int(getattr(team, "workforce", 0) or 0)

    def _active_projects(self, state: GameState) -> list[PlayerConstructionProject]:
        return [project for project in state.player_construction_projects if project.active and not project.completed]

    def _allocated_percent_except(self, state: GameState, project: PlayerConstructionProject) -> int:
        return sum(
            int(item.allocation_percent or 0)
            for item in self._active_projects(state)
            if item is not project
        )

    def _refresh_project_staffing(self, state: GameState, project: PlayerConstructionProject) -> None:
        capacity = self._engineering_capacity_for_team(state)
        project.allocation_percent = max(0, min(100, int(project.allocation_percent or 0)))
        project.assigned_engineers = round(capacity * project.allocation_percent / 100)

    def _raw_progress_per_week(self, state: GameState, project: PlayerConstructionProject) -> float:
        estimated_weeks = self._estimated_weeks(state, project)
        if estimated_weeks is None or estimated_weeks <= 0:
            return 0.0
        return max(0.0, project.progress_required / estimated_weeks)

    def _resource_score(self, state: GameState) -> float:
        team = state.player_team
        if not team:
            return 0.0
        engineering_staff = max(0, min(80, int(getattr(team, "engineering_staff", 0) or 0)))
        factory_size = max(1, min(5, int(getattr(team, "factory_size", 1) or 1)))
        facilities = max(0, min(100, int(getattr(team, "facilities", 0) or 0)))
        staff_score = engineering_staff / 80
        factory_score = (factory_size - 1) / 4
        facilities_score = facilities / 100
        return max(0.0, min(1.0, (staff_score * 0.45) + (factory_score * 0.30) + (facilities_score * 0.25)))

    def _design_block_score(self, project: PlayerConstructionProject) -> float:
        design_blocks = max(self.CURRENT_YEAR_MIN_DESIGN_BLOCKS, min(self.CURRENT_YEAR_MAX_DESIGN_BLOCKS, int(project.design_blocks or 0)))
        return (
            (design_blocks - self.CURRENT_YEAR_MIN_DESIGN_BLOCKS)
            / (self.CURRENT_YEAR_MAX_DESIGN_BLOCKS - self.CURRENT_YEAR_MIN_DESIGN_BLOCKS)
        )

    def _target_week_range(self, project: PlayerConstructionProject) -> tuple[float, float]:
        if project.scope == "next_year":
            return self.MAJOR_UPGRADE_FAST_WEEKS, self.MAJOR_UPGRADE_SLOW_WEEKS
        scale = self._design_block_score(project)
        fast = self.MINOR_UPGRADE_FAST_WEEKS + ((self.MAJOR_UPGRADE_FAST_WEEKS - self.MINOR_UPGRADE_FAST_WEEKS) * scale)
        slow = self.MINOR_UPGRADE_SLOW_WEEKS + ((self.MAJOR_UPGRADE_SLOW_WEEKS - self.MINOR_UPGRADE_SLOW_WEEKS) * scale)
        return fast, slow

    def _estimated_weeks(self, state: GameState, project: PlayerConstructionProject) -> float | None:
        allocation = max(0, min(100, int(project.allocation_percent or 0)))
        if allocation <= 0 or int(project.assigned_engineers or 0) <= 0:
            return None
        fast_weeks, slow_weeks = self._target_week_range(project)
        resource_score = self._resource_score(state)
        base_weeks = slow_weeks - ((slow_weeks - fast_weeks) * resource_score)
        return max(1.0, base_weeks * (100 / allocation))

    def _build_cost_for_scope(self, scope: str, design: PlayerCarDevelopment | None = None) -> int:
        if scope == "next_year":
            return self.NEXT_YEAR_CHASSIS_UNIT_COST
        if design is None:
            return self.CURRENT_YEAR_MIN_UPGRADE_COST
        design_blocks = sum(max(0, min(10, int(stage.progress or 0))) for stage in design.stages)
        bounded_blocks = max(self.CURRENT_YEAR_MIN_DESIGN_BLOCKS, min(self.CURRENT_YEAR_MAX_DESIGN_BLOCKS, design_blocks))
        scale = (
            (bounded_blocks - self.CURRENT_YEAR_MIN_DESIGN_BLOCKS)
            / (self.CURRENT_YEAR_MAX_DESIGN_BLOCKS - self.CURRENT_YEAR_MIN_DESIGN_BLOCKS)
        )
        return round(self.CURRENT_YEAR_MIN_UPGRADE_COST + ((self.CURRENT_YEAR_MAX_UPGRADE_COST - self.CURRENT_YEAR_MIN_UPGRADE_COST) * scale))

    def _progress_required_for_scope(self, scope: str) -> int:
        return self.NEXT_YEAR_PROGRESS_REQUIRED if scope == "next_year" else self.CURRENT_YEAR_PROGRESS_REQUIRED

    def _units_required_for_scope(self, scope: str) -> int:
        return 1

    def create_from_design(self, state: GameState, design: PlayerCarDevelopment) -> PlayerConstructionProject:
        scope = self._normalize_scope(design.scope)
        if any(project.scope == scope and not project.completed for project in state.player_construction_projects):
            raise ValueError("A construction project for this chassis is already queued")
        project = PlayerConstructionProject(
            active=False,
            scope=scope,
            name=design.name,
            year=design.year,
            allocation_percent=0,
            progress_required=self._progress_required_for_scope(scope),
            total_cost=self._build_cost_for_scope(scope, design),
            speed_delta=int(design.speed_delta or 0),
            quality_score=int(design.quality_score or 0),
            risk=design.risk,
            units_required=self._units_required_for_scope(scope),
            design_blocks=sum(max(0, min(10, int(stage.progress or 0))) for stage in design.stages),
        )
        self._refresh_project_staffing(state, project)
        state.player_construction_projects.append(project)
        state.add_email(
            sender="Chief Engineer",
            subject=f"Construction Package Ready: {project.name}",
            body=(
                f"The completed design package is ready to start construction.\n\n"
                f"Project: {project.name}\n"
                f"Build cost estimate: ${project.total_cost:,}\n"
                f"Required build work: {project.progress_required} blocks"
            ),
            category=EmailCategory.GENERAL,
        )
        return project

    def start_project(self, state: GameState, scope: str | None) -> PlayerConstructionProject:
        normalized_scope = self._normalize_scope(scope)
        project = next(
            (
                item
                for item in state.player_construction_projects
                if item.scope == normalized_scope and not item.active and not item.completed
            ),
            None,
        )
        if project is None and normalized_scope == "next_year":
            project = self._create_additional_next_year_chassis_project(state)
        if not project:
            raise ValueError("No construction package is ready for this chassis")
        if any(item.scope == normalized_scope and item.active for item in state.player_construction_projects):
            raise ValueError("A construction project for this chassis is already active")
        remaining_allocation = max(0, 100 - sum(int(item.allocation_percent or 0) for item in self._active_projects(state)))
        project.active = True
        project.allocation_percent = remaining_allocation
        self._refresh_project_staffing(state, project)
        state.add_email(
            sender="Chief Engineer",
            subject=f"Construction Started: {project.name}",
            body=(
                f"Engineering has started construction.\n\n"
                f"Project: {project.name}\n"
                f"Engineering allocation: {project.allocation_percent}% ({project.assigned_engineers} engineers)\n"
                f"Build cost estimate: ${project.total_cost:,}"
            ),
            category=EmailCategory.GENERAL,
        )
        return project

    def _create_additional_next_year_chassis_project(self, state: GameState) -> PlayerConstructionProject | None:
        previous = next(
            (
                item
                for item in reversed(state.player_construction_projects)
                if item.scope == "next_year" and item.completed and not item.applied
            ),
            None,
        )
        if previous is None:
            return None
        built_so_far = self._next_year_chassis_built_count(state, int(previous.year or state.year + 1))
        base_name = str(previous.name or "Next Year Chassis").split(" #", 1)[0]
        project = PlayerConstructionProject(
            active=False,
            scope="next_year",
            name=f"{base_name} #{built_so_far + 1}",
            year=previous.year,
            allocation_percent=0,
            progress_required=self.NEXT_YEAR_PROGRESS_REQUIRED,
            total_cost=self.NEXT_YEAR_CHASSIS_UNIT_COST,
            speed_delta=int(previous.speed_delta or 0),
            quality_score=int(previous.quality_score or 0),
            risk=previous.risk,
            units_required=1,
            design_blocks=int(previous.design_blocks or 0),
        )
        self._refresh_project_staffing(state, project)
        state.player_construction_projects.append(project)
        return project

    def set_allocation(self, state: GameState, scope: str | None, allocation_percent: int | None) -> PlayerConstructionProject:
        normalized_scope = self._normalize_scope(scope)
        project = next((item for item in self._active_projects(state) if item.scope == normalized_scope), None)
        if not project:
            raise ValueError("No active construction project")
        if allocation_percent is None:
            raise ValueError("allocation_percent is required")
        requested = max(0, min(100, int(allocation_percent)))
        other_allocated = self._allocated_percent_except(state, project)
        if requested + other_allocated > 100:
            raise ValueError(f"Engineering allocation exceeds 100%; {100 - other_allocated}% is available")
        project.allocation_percent = requested
        self._refresh_project_staffing(state, project)
        return project

    def get_payload(self, state: GameState) -> dict:
        engineering_capacity = self._engineering_capacity_for_team(state)
        projects = {}
        for scope in sorted(self.SCOPES):
            project = next((item for item in state.player_construction_projects if item.scope == scope and item.active), None)
            if project is None:
                project = next(
                    (
                        item
                        for item in reversed(state.player_construction_projects)
                        if item.scope == scope and not item.completed
                    ),
                    None,
                )
            if project is None:
                project = next(
                    (
                        item
                        for item in reversed(state.player_construction_projects)
                        if item.scope == scope and item.completed
                    ),
                    None,
                )
            projects[scope] = self._project_payload(state, project, scope) if project else self._empty_project_payload(state, scope)
        return {
            "engineering_staff_available": engineering_capacity,
            "allocated_percent": sum(int(project.allocation_percent or 0) for project in self._active_projects(state)),
            "projects": projects,
        }

    def _empty_project_payload(self, state: GameState, scope: str) -> dict:
        return {
            "active": False,
            "scope": scope,
            "name": None,
            "year": state.year + 1 if scope == "next_year" else state.year,
            "allocation_percent": 0,
            "assigned_engineers": 0,
            "available_allocation_percent": 100 - sum(int(project.allocation_percent or 0) for project in self._active_projects(state)),
            "progress": 0,
            "progress_required": self._progress_required_for_scope(scope),
            "total_cost": self._build_cost_for_scope(scope),
            "paid": 0,
            "completed": False,
            "applied": False,
            "can_start": False,
            "speed_delta": 0,
            "quality_score": 0,
            "risk": "None",
            "units_required": self._units_required_for_scope(scope),
            "units_built": 0,
            "race_ready_required": self.NEXT_YEAR_RACE_READY_CHASSIS_REQUIRED if scope == "next_year" else 1,
            "race_ready_built": self._next_year_chassis_built_count(state, state.year + 1) if scope == "next_year" else 0,
            "estimated_weeks": None,
            "target_week_range": self._target_week_range(PlayerConstructionProject(scope=scope)),
        }

    def _project_payload(self, state: GameState, project: PlayerConstructionProject, scope: str) -> dict:
        self._refresh_project_staffing(state, project)
        race_ready_built = self._next_year_chassis_built_count(state, int(project.year or state.year + 1)) if scope == "next_year" else project.units_built
        can_start = not project.active and not project.completed
        if scope == "next_year" and project.completed and not project.applied:
            can_start = True
        return {
            "active": project.active,
            "scope": project.scope,
            "name": project.name,
            "year": project.year,
            "allocation_percent": project.allocation_percent,
            "assigned_engineers": project.assigned_engineers,
            "available_allocation_percent": max(0, 100 - self._allocated_percent_except(state, project)),
            "progress": project.progress,
            "progress_required": project.progress_required,
            "total_cost": project.total_cost,
            "paid": project.paid,
            "completed": project.completed,
            "applied": project.applied,
            "can_start": can_start,
            "speed_delta": project.speed_delta,
            "quality_score": project.quality_score,
            "risk": project.risk,
            "units_required": project.units_required,
            "units_built": project.units_built,
            "race_ready_required": self.NEXT_YEAR_RACE_READY_CHASSIS_REQUIRED if scope == "next_year" else 1,
            "race_ready_built": race_ready_built,
            "estimated_weeks": self._estimated_weeks(state, project),
            "target_week_range": self._target_week_range(project),
        }

    def process_week(self, state: GameState) -> dict | None:
        results = []
        for project in self._active_projects(state):
            result = self._process_project_week(state, project)
            if result:
                results.append(result)
        if not results:
            return None
        return {"status": "processed", "projects": results}

    def _process_project_week(self, state: GameState, project: PlayerConstructionProject) -> dict | None:
        self._refresh_project_staffing(state, project)
        raw_progress = self._raw_progress_per_week(state, project)
        project.progress_carry = max(0.0, float(project.progress_carry or 0.0)) + raw_progress
        progress_added = min(6, int(project.progress_carry))
        project.progress_carry -= progress_added
        if progress_added <= 0:
            return {
                "status": "blocked",
                "project": project.name,
                "scope": project.scope,
                "raw_progress": raw_progress,
                "progress_carry": project.progress_carry,
            }
        progress_before = int(project.progress or 0)
        project.progress = min(project.progress_required, progress_before + progress_added)
        actual_added = project.progress - progress_before
        cost = self._charge_progress_cost(state, project, actual_added)
        if project.progress >= project.progress_required:
            self._complete_project(state, project)
        return {
            "status": "completed" if project.completed else "in_progress",
            "project": project.name,
            "scope": project.scope,
            "progress_before": progress_before,
            "progress_after": project.progress,
            "progress_added": actual_added,
            "cost": cost,
            "raw_progress": raw_progress,
            "progress_carry": project.progress_carry,
        }

    def _charge_progress_cost(self, state: GameState, project: PlayerConstructionProject, progress_added: int) -> int:
        if progress_added <= 0 or project.total_cost <= 0 or project.progress_required <= 0:
            return 0
        remaining_cost = max(0, int(project.total_cost or 0) - int(project.paid or 0))
        cost = min(remaining_cost, round(project.total_cost * (progress_added / project.progress_required)))
        if cost <= 0:
            return 0
        project.paid += cost
        state.finance.add_transaction(
            week=state.calendar.current_week,
            year=state.year,
            amount=-cost,
            category=TransactionCategory.CONSTRUCTION,
            description=f"{project.name} construction ({project.progress}/{project.progress_required})",
        )
        return cost

    def _complete_project(self, state: GameState, project: PlayerConstructionProject) -> None:
        project.active = False
        project.completed = True
        project.units_built = int(project.units_required or 1)
        if project.scope == "current_year":
            self._apply_current_year_upgrade(state, project)
            return
        state.add_email(
            sender="Chief Engineer",
            subject=f"Next Year's Chassis Built: {project.name}",
            body=(
                f"Construction of {project.name} is complete.\n\n"
                f"Chassis built: {self._next_year_chassis_built_count(state, int(project.year or state.year + 1))} / {self.NEXT_YEAR_RACE_READY_CHASSIS_REQUIRED} required for Race 1\n"
                f"Projected performance gain: +{project.speed_delta}\n"
                f"Construction spend: ${project.paid:,}"
            ),
            category=EmailCategory.GENERAL,
        )

    def _apply_current_year_upgrade(self, state: GameState, project: PlayerConstructionProject) -> None:
        team = state.player_team
        if not team:
            return
        old_speed = team.car_speed
        team.car_speed = max(1, old_speed + int(project.speed_delta or 0))
        project.applied = True
        state.add_email(
            sender="Chief Engineer",
            subject=f"Chassis Upgrade Built and Fitted: +{project.speed_delta}",
            body=(
                f"{project.name} has been constructed and fitted to the current car.\n\n"
                f"Car rating: {old_speed} -> {team.car_speed}\n"
                f"Construction spend: ${project.paid:,}\n"
                f"Design quality: {project.quality_score}\n"
                f"Risk: {project.risk}"
            ),
            category=EmailCategory.GENERAL,
        )

    def apply_next_year_for_rollover(self, state: GameState) -> dict | None:
        projects = self._completed_next_year_projects(state, state.year)
        team = state.player_team
        if not team:
            return None
        if self._sum_units_built(projects) < self.NEXT_YEAR_RACE_READY_CHASSIS_REQUIRED:
            return {"status": "not_ready", "reason": "next_year_chassis_not_built"}
        return self._apply_next_year_projects(state, projects)

    def validate_first_race_chassis_ready(self, state: GameState) -> dict | None:
        current_event = state.calendar.current_event
        if current_event is None:
            return None
        race_events = [event for event in state.calendar.events if event.type.value == "RACE"]
        first_race_week = min((event.week for event in race_events), default=None)
        if first_race_week is None or current_event.week != first_race_week:
            return None
        team = state.player_team
        if not team:
            return None
        projects = self._completed_next_year_projects(state, state.year)
        chassis_year = getattr(state, "player_chassis_year", None)
        if chassis_year is None and state.year <= 1998:
            return {"status": "ready", "chassis_built": len(state.player_chassis)}
        if (
            chassis_year == state.year
            and len(state.player_chassis) >= self.NEXT_YEAR_RACE_READY_CHASSIS_REQUIRED
        ):
            return {"status": "ready", "chassis_built": len(state.player_chassis)}
        if self._sum_units_built(projects) >= self.NEXT_YEAR_RACE_READY_CHASSIS_REQUIRED:
            return self._apply_next_year_projects(state, projects)
        state.game_over = True
        state.game_over_reason = "next_year_chassis_not_built"
        state.add_email(
            sender="Board of Directors",
            subject="Game Over: No Race-Ready Chassis",
            body=(
                f"The team has failed scrutineering for {state.year} Race 1.\n\n"
                "At least two race-ready chassis must be built before the first race of the new season."
            ),
            category=EmailCategory.SEASON,
        )
        return {"status": "game_over", "reason": state.game_over_reason, "message": "At least two race-ready chassis must be built before Race 1."}

    def _completed_next_year_projects(self, state: GameState, year: int) -> list[PlayerConstructionProject]:
        return [
            item
            for item in state.player_construction_projects
            if item.scope == "next_year" and item.year == year and item.completed
        ]

    def _sum_units_built(self, projects: list[PlayerConstructionProject]) -> int:
        return sum(max(0, int(project.units_built or 0)) for project in projects)

    def _next_year_chassis_built_count(self, state: GameState, year: int) -> int:
        return self._sum_units_built(self._completed_next_year_projects(state, year))

    def _apply_next_year_projects(self, state: GameState, projects: list[PlayerConstructionProject]) -> dict:
        team = state.player_team
        if not team:
            return {"status": "not_ready", "reason": "no_player_team"}
        built_count = self._sum_units_built(projects)
        if all(project.applied for project in projects) and len(state.player_chassis) >= self.NEXT_YEAR_RACE_READY_CHASSIS_REQUIRED:
            return {"status": "ready", "chassis_built": len(state.player_chassis)}
        project = projects[0]
        old_speed = team.car_speed
        team.car_speed = max(1, old_speed + int(project.speed_delta or 0))
        for item in projects:
            item.applied = True
        state.player_chassis = self._create_next_year_chassis(state, team.id, built_count)
        state.player_chassis_year = state.year
        state.player_test_chassis_id = state.player_chassis[0].id if state.player_chassis else None
        state.player_race_chassis_assignments = {}
        state.add_email(
            sender="Chief Engineer",
            subject=f"New Chassis Introduced: {project.name}",
            body=(
                f"The completed {project.name} has been introduced for {state.year}.\n\n"
                f"Car rating: {old_speed} -> {team.car_speed}\n"
                f"Race-ready chassis: {built_count}\n"
                f"Construction spend: ${sum(int(item.paid or 0) for item in projects):,}"
            ),
            category=EmailCategory.SEASON,
        )
        return {
            "status": "applied",
            "project": project.name,
            "old_speed": old_speed,
            "new_speed": team.car_speed,
            "speed_delta": project.speed_delta,
            "quality_score": project.quality_score,
            "chassis_built": built_count,
        }

    def _create_next_year_chassis(self, state: GameState, team_id: int, count: int) -> list[Chassis]:
        return [
            Chassis(id=index, team_id=team_id, name=f"{state.year} Chassis {index}", wear=0)
            for index in range(1, max(0, int(count or 0)) + 1)
        ]

    def reset_completed_for_new_season(self, state: GameState) -> None:
        state.player_construction_projects = [
            project
            for project in state.player_construction_projects
            if project.scope == "next_year" and project.year == state.year and not project.applied
        ]
