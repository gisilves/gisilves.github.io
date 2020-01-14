window.FCAUsedConfig = {
	maps: {
		endpoint: 'https://maps.googleapis.com/maps/api/js?libraries=places&client=gme-fiat&language=it&region=it'
	},
	language: {
		id: 'it',
		endpoint: 'https://usedcars.fcagroup.com/:market/:language/_layouts/UsedCarsUtilityPages/JsonData.aspx?List=UsedCarsLabelList',
		numberGroupSeparator: '.',
		numberDecimalSeparator: ','
	},
	market: {
		code: 1000,
		id: 'it'
	},
	brand: {
		code: '000',
		id: 'fiat',
		name: 'Fiat',
		taggingName: 'fiat',
		headerSelector: '.header-top-fixed'
	},
 	search: {
		explicitMandate: true,
		distance: {
			min: 15,
			max: 200,
			default: 50,
			step: 10,
			unit: 'km'
		},
		brand: {
			default: {
				brandCode: '000',
				brandDescription: 'Fiat'
			}
		},
		price: {
			min: 0,
			max: 80000,
			step: 500,
			default: { min: 0, max: 80000 },
			unit: '€'
		},
		year: {
			min: (new Date()).getFullYear() - 10,
			max: (new Date()).getFullYear(),
			step: 1,
			default: {
				min: (new Date()).getFullYear() - 10,
				max: (new Date()).getFullYear()
			}
		},
		mileage: {
			steps: [0, 5000, 10000, 15000, 20000, 30000, 50000, 75000, 100000, 150000],
			default: 150000,
			unit: 'km'
		},
		premium: {
			default: false,
			warrantyCode: '20',
			taggingId: 'autoexpert'
		},
		power: {
			min: 50,
			max: 250,
			step: 1,
			unit: 'Cv'
		}
	},
	pagination: {
		sizes: [10, 20, 30],
		default: 10
	},
	order: {
		fields: [{
			label: 'order_by_distance',
			key: 'vehicle_position',
			direction: 'asc'
		}, {
			label: 'order_by_price',
			key: 'priceCurrent',
			direction: 'asc'
		}, {
			label: 'order_by_year',
			key: 'registrationYear',
			direction: 'desc'
		}, {
			label: 'order_by_km',
			key: 'km',
			direction: 'asc'
		}],
		default: {
			label: 'order_by_distance',
			key: 'vehicle_position',
			direction: 'asc'
		}
	},
	premium: {
		descriptionItems: 6,
		descriptionNotes: 2
	},
	uvl: {
		api: 'https://usedcars.fcagroup.com/uvl/uvl-rest/api',
		images: 'https://usedcars.fcagroup.com/uvl',
		additionalFilters: {
			simType: ['V']
		}
	},
	contactForm: {
		url: 'https://dpromo.fiat.com/LP=13660'
	},
	dealerLocator: {
		endpoint: 'https://dealerlocator.fiat.com/geocall/RestServlet',
		params: {
			serv: 'sales',
            wa: 1
		}
	},
	vehicleDetailFields: {
		enableDealerWebsite: false
	},
	mirafioriStripe: {
		selector: ".outlet"
	},
	queryStringParams: {
		defaultDistance: "defaultDistance",
		defaultModel: "defaultModel"
	},
	mkParams: {
		mktgCampaignID: "8750",
		offerIncentiveID: "",
		siteType: "web corporate",
		businessArea: "used",
		usedvehicleBrand: "Fiat",
		assetOwner: "brand"
	},
	impressum: {
		endpoint: 'https://usedcars.fcagroup.com/Resources/new-usedcars/impressum/:market/:language/:legalentity.html'
	},
	mynumber: {
		enabled: false,
		endpoint: "https://fcausatomynumber.azurewebsites.net/api/dealer/mynumber",
		masterKey: "Autoexpert - USATO",
		enableDealerLocatorFallback: true,
		removePrefix: /^\+39/
	},
	installmentsCalculator: {
      enabled: true, // Se false disabilita la calcolatrice
      iframe: { // Endpoint iframe
        domain: "https://fcabank.it",
        path: "/calculators/usedvehicle/it/expert/fiat/index.php"
      },
      api: "https://fcaused.calculator.fgacapital.it/calculator_it.asmx", // Endpoint API
    }
};
