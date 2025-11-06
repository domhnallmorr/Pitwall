from pw_model.staff_market import manager_transfers
from pw_model.pw_model_enums import StaffRoles
from tests import create_model


def test_salary_ranges():
    ''' 
    Test that salaries are within expected ranges when player hired someone
    '''

    model = create_model.create_model(auto_save=False)
    model.player_team = "Warrick"

    muller_model = model.entity_manager.get_driver_model("Jorn Maller")
    gene_model = model.entity_manager.get_driver_model("Marco Genoa")
    gene_model.speed = 99

    oatley_model = model.entity_manager.get_technical_director_model("Neil Oatley")
    gallagher_model = model.entity_manager.get_commercial_manager_model("Mark Gallagher")

    model.staff_market.complete_hiring("Marco Genoa", "Warrick", StaffRoles.DRIVER1, 3_200_000)
    model.staff_market.complete_hiring("Jorn Maller", "Warrick", StaffRoles.DRIVER2, 700_000)
    model.staff_market.complete_hiring("Neil Oatley", "Warrick", StaffRoles.TECHNICAL_DIRECTOR)
    model.staff_market.complete_hiring("Mark Gallagher", "Warrick", StaffRoles.COMMERCIAL_MANAGER)
    
    # Setup sponsor market before end_season
    model.sponsor_market.setup_dataframes()
    model.sponsor_market.compute_transfers()
    
    model.end_season()

    assert gene_model.contract.salary == 3_200_000
    assert muller_model.contract.salary == 700_000
    assert oatley_model.contract.salary >= 700_000 and oatley_model.contract.salary <= 1_200_000
    assert gallagher_model.contract.salary >= 180_000 and gallagher_model.contract.salary <= 220_000

