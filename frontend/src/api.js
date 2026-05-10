/**
 * API Module
 * Wrapper for Electron IPC calls.
 */

const API = {
	startCareer: (teamName) => window.electronAPI.sendToPython(
		teamName ? { type: 'start_career', team_name: teamName } : { type: 'start_career' }
	),
	loadGame: () => window.electronAPI.sendToPython({ type: 'load_game' }),
	checkSave: () => window.electronAPI.sendToPython({ type: 'check_save' }),
	getHome: () => window.electronAPI.sendToPython({ type: 'get_home' }),
	getGrid: (year) => window.electronAPI.sendToPython(
		year !== undefined ? { type: 'get_grid', year } : { type: 'get_grid' }
	),
	getCalendar: () => window.electronAPI.sendToPython({ type: 'get_calendar' }),
	getStandings: () => window.electronAPI.sendToPython({ type: 'get_standings' }),
	advanceWeek: () => window.electronAPI.sendToPython({ type: 'advance_week' }),
	skipEvent: () => window.electronAPI.sendToPython({ type: 'skip_event' }),
	attendTest: (kms) => window.electronAPI.sendToPython({ type: 'attend_test', kms }),
	getRaceWeekend: () => window.electronAPI.sendToPython({ type: 'get_race_weekend' }),
	setRaceStrategy: (strategies) => window.electronAPI.sendToPython({ type: 'set_race_strategy', strategies }),
	simulateQualifying: () => window.electronAPI.sendToPython({ type: 'simulate_qualifying' }),
	simulateRace: () => window.electronAPI.sendToPython({ type: 'simulate_race' }),
	getEmails: () => window.electronAPI.sendToPython({ type: 'get_emails' }),
	readEmail: (emailId) => window.electronAPI.sendToPython({ type: 'read_email', email_id: emailId }),
	getStaff: () => window.electronAPI.sendToPython({ type: 'get_staff' }),
	getReplacementCandidates: (driverId) => window.electronAPI.sendToPython({ type: 'get_replacement_candidates', driver_id: driverId }),
	getManagerReplacementCandidates: (managerId) => window.electronAPI.sendToPython({ type: 'get_manager_replacement_candidates', manager_id: managerId }),
	getTechnicalDirectorReplacementCandidates: (directorId) => window.electronAPI.sendToPython({ type: 'get_technical_director_replacement_candidates', director_id: directorId }),
	getTitleSponsorReplacementCandidates: (sponsorName) => window.electronAPI.sendToPython({ type: 'get_title_sponsor_replacement_candidates', sponsor_name: sponsorName }),
	getEngineSupplierReplacementCandidates: (supplierName) => window.electronAPI.sendToPython({ type: 'get_engine_supplier_replacement_candidates', supplier_name: supplierName }),
	getTyreSupplierReplacementCandidates: (supplierName) => window.electronAPI.sendToPython({ type: 'get_tyre_supplier_replacement_candidates', supplier_name: supplierName }),
	getTitleSponsorNegotiationMarket: () => window.electronAPI.sendToPython({ type: 'get_title_sponsor_negotiation_market' }),
	startTitleSponsorNegotiation: (sponsorId) => window.electronAPI.sendToPython({ type: 'start_title_sponsor_negotiation', sponsor_id: sponsorId }),
	updateTitleSponsorNegotiationStaff: (assignedStaff) => window.electronAPI.sendToPython({ type: 'update_title_sponsor_negotiation_staff', assigned_staff: assignedStaff }),
	signTitleSponsorNegotiatedDeal: () => window.electronAPI.sendToPython({ type: 'sign_title_sponsor_negotiated_deal' }),
	bookTitleSponsorHospitality: () => window.electronAPI.sendToPython({ type: 'book_title_sponsor_hospitality' }),
	getEngineNegotiationMarket: () => window.electronAPI.sendToPython({ type: 'get_engine_negotiation_market' }),
	startEngineNegotiation: (supplierId) => window.electronAPI.sendToPython({ type: 'start_engine_negotiation', supplier_id: supplierId }),
	updateEngineNegotiationStaff: (assignedStaff) => window.electronAPI.sendToPython({ type: 'update_engine_negotiation_staff', assigned_staff: assignedStaff }),
	signEngineNegotiatedDeal: (tier) => window.electronAPI.sendToPython({ type: 'sign_engine_negotiated_deal', tier }),
	bookEngineNegotiationHospitality: () => window.electronAPI.sendToPython({ type: 'book_engine_negotiation_hospitality' }),
	getTyreNegotiationMarket: () => window.electronAPI.sendToPython({ type: 'get_tyre_negotiation_market' }),
	startTyreNegotiation: (supplierId) => window.electronAPI.sendToPython({ type: 'start_tyre_negotiation', supplier_id: supplierId }),
	updateTyreNegotiationStaff: (assignedStaff) => window.electronAPI.sendToPython({ type: 'update_tyre_negotiation_staff', assigned_staff: assignedStaff }),
	signTyreNegotiatedDeal: (tier) => window.electronAPI.sendToPython({ type: 'sign_tyre_negotiated_deal', tier }),
	bookTyreNegotiationHospitality: () => window.electronAPI.sendToPython({ type: 'book_tyre_negotiation_hospitality' }),
	offerDriver: (driverId, incomingDriverId, salaryOffer, contractLength) => window.electronAPI.sendToPython({
		type: 'offer_driver',
		driver_id: driverId,
		incoming_driver_id: incomingDriverId,
		salary_offer: salaryOffer,
		contract_length: contractLength
	}),
	replaceDriver: (driverId, incomingDriverId) => window.electronAPI.sendToPython({
		type: 'replace_driver',
		driver_id: driverId,
		incoming_driver_id: incomingDriverId
	}),
	replaceCommercialManager: (managerId, incomingManagerId) => window.electronAPI.sendToPython({
		type: 'replace_commercial_manager',
		manager_id: managerId,
		incoming_manager_id: incomingManagerId
	}),
	replaceTechnicalDirector: (directorId, incomingDirectorId) => window.electronAPI.sendToPython({
		type: 'replace_technical_director',
		director_id: directorId,
		incoming_director_id: incomingDirectorId
	}),
	replaceTitleSponsor: (sponsorName, incomingSponsorId) => window.electronAPI.sendToPython({
		type: 'replace_title_sponsor',
		sponsor_name: sponsorName,
		incoming_sponsor_id: incomingSponsorId
	}),
	replaceEngineSupplier: (supplierName, incomingSupplierId) => window.electronAPI.sendToPython({
		type: 'replace_engine_supplier',
		supplier_name: supplierName,
		incoming_supplier_id: incomingSupplierId
	}),
	replaceTyreSupplier: (supplierName, incomingSupplierId) => window.electronAPI.sendToPython({
		type: 'replace_tyre_supplier',
		supplier_name: supplierName,
		incoming_supplier_id: incomingSupplierId
	}),
	getDriver: (name) => window.electronAPI.sendToPython({ type: 'get_driver', name }),
	getCar: () => window.electronAPI.sendToPython({ type: 'get_car' }),
	startCarDevelopment: (developmentType = 'current_year') => window.electronAPI.sendToPython({ type: 'start_car_development', development_type: developmentType }),
	finishCarDevelopmentStage: (scope = 'current_year') => window.electronAPI.sendToPython({ type: 'finish_car_development_stage', scope }),
	setCarDevelopmentAllocation: (scope = 'current_year', allocationPercent = 0) => window.electronAPI.sendToPython({
		type: 'set_car_development_allocation',
		scope,
		allocation_percent: allocationPercent
	}),
	setConstructionAllocation: (scope = 'current_year', allocationPercent = 0) => window.electronAPI.sendToPython({
		type: 'set_construction_allocation',
		scope,
		allocation_percent: allocationPercent
	}),
	startConstructionProject: (scope = 'current_year') => window.electronAPI.sendToPython({
		type: 'start_construction_project',
		scope
	}),
	setTestChassis: (chassisId) => window.electronAPI.sendToPython({ type: 'set_test_chassis', chassis_id: chassisId }),
	setRaceChassisAssignments: (driver1ChassisId, driver2ChassisId) => window.electronAPI.sendToPython({
		type: 'set_race_chassis_assignments',
		driver1_chassis_id: driver1ChassisId,
		driver2_chassis_id: driver2ChassisId
	}),
	repairChassisWear: (chassisId, wearPoints) => window.electronAPI.sendToPython({
		type: 'repair_chassis_wear',
		chassis_id: chassisId,
		wear_points: wearPoints
	}),
	buildSpareSet: () => window.electronAPI.sendToPython({ type: 'build_spare_set' }),
	getFinance: () => window.electronAPI.sendToPython({ type: 'get_finance' }),
	getFacilities: () => window.electronAPI.sendToPython({ type: 'get_facilities' }),
	previewFacilitiesUpgrade: (points, years) => window.electronAPI.sendToPython({ type: 'preview_facilities_upgrade', points, years }),
	startFacilitiesUpgrade: (points, years) => window.electronAPI.sendToPython({ type: 'start_facilities_upgrade', points, years }),
	ping: () => window.electronAPI.sendToPython({ type: 'ping' }),
	loadRoster: () => window.electronAPI.sendToPython({ type: 'load_roster' }),

	// Listener for incoming data
	onData: (callback) => window.electronAPI.onPythonData(callback)
};

export default API;
