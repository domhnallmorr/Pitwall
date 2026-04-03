from app.core.management_transfers import (
    CommercialManagerTransferManager,
    EngineSupplierTransferManager,
    TechnicalDirectorTransferManager,
    TitleSponsorTransferManager,
    TyreSupplierTransferManager,
)
from app.core.player_car_development import PlayerCarDevelopmentManager
from app.core.transfers import TransferManager
from app.commands.staff_market_commands import (
    handle_get_engine_supplier_replacement_candidates,
    handle_get_manager_replacement_candidates,
    handle_get_replacement_candidates,
    handle_get_technical_director_replacement_candidates,
    handle_get_title_sponsor_replacement_candidates,
    handle_get_tyre_supplier_replacement_candidates,
    handle_replace_commercial_manager,
    handle_replace_driver,
    handle_replace_engine_supplier,
    handle_replace_technical_director,
    handle_replace_title_sponsor,
    handle_replace_tyre_supplier,
)
from app.commands.staff_team_commands import (
    handle_repair_car_wear,
    handle_start_car_development,
    handle_update_workforce,
)
