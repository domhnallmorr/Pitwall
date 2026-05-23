"""Compatibility exports for staff/market command handlers.

New code should import from the domain-specific command modules directly.
"""

from app.commands.driver_market_commands import (
    handle_get_replacement_candidates,
    handle_offer_driver,
    handle_replace_driver,
)
from app.commands.management_market_commands import (
    handle_get_manager_replacement_candidates,
    handle_get_technical_director_replacement_candidates,
    handle_offer_technical_director,
    handle_replace_commercial_manager,
    handle_replace_technical_director,
)
from app.commands.sponsor_market_commands import (
    handle_book_title_sponsor_hospitality,
    handle_get_title_sponsor_negotiation_market,
    handle_get_title_sponsor_replacement_candidates,
    handle_replace_title_sponsor,
    handle_sign_title_sponsor_negotiated_deal,
    handle_start_title_sponsor_negotiation,
    handle_update_title_sponsor_negotiation_staff,
)
from app.commands.supplier_market_commands import (
    handle_book_engine_negotiation_hospitality,
    handle_book_tyre_negotiation_hospitality,
    handle_get_engine_negotiation_market,
    handle_get_engine_supplier_replacement_candidates,
    handle_get_tyre_negotiation_market,
    handle_get_tyre_supplier_replacement_candidates,
    handle_replace_engine_supplier,
    handle_replace_tyre_supplier,
    handle_sign_engine_negotiated_deal,
    handle_sign_tyre_negotiated_deal,
    handle_start_engine_negotiation,
    handle_start_tyre_negotiation,
    handle_update_engine_negotiation_staff,
    handle_update_tyre_negotiation_staff,
)
