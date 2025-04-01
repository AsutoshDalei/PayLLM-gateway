serviceDB = {
    'goa': {
        'electricity': ['ged'],
        'gas': ['iocl','hpcl','bpcl'],
        'water': ['pwd'],
        'mobile': ['airtel','bsnl','jio','vi']
    },
    'karnataka': {
        'electricity': ['bescom','mescom','hescom','gescom','cescom'],
        'gas': ['gail'],
        'water': ['bwssb'],
        'mobile': ['airtel','bsnl','jio','vi']
    },
    'telangana': {
        'electricity': ['tsspdcl','tsnpdcl'],
        'gas': ['bgl'],
        'water': ['hmwssb'],
        'mobile': ['airtel','bsnl','jio','vi']
    }
}

billDB = {
    # karnataka
    2037: {'customer name': 'rajesh shetty', 'service provider': 'bescom', 'unit': 48, 'amount': 710,
           'due date': '25/06/2025', 'status': 'paid', 'service': 'electricity'},
    2038: {'customer name': 'anjali rao', 'service provider': 'indane gas', 'amount': 1230, 'due date': '20/09/2025',
           'status': 'unpaid', 'service': 'gas'},
    2039: {'customer name': 'vivek patil', 'service provider': 'bangalore water supply', 'amount': 860,
           'due date': '15/11/2025', 'status': 'paid', 'service': 'water'},
    2040: {'customer name': 'sneha kulkarni', 'service provider': 'airtel', 'amount': 599, 'due date': '05/10/2026',
           'status': 'unpaid', 'service': 'mobile'},
    # goa
    2045: {'customer name': 'anil naik', 'service provider': 'goa electricity dept', 'unit': 48, 'amount': 690,
           'due date': '15/05/2025', 'status': 'paid', 'service': 'electricity'},
    2046: {'customer name': 'sneha gaonkar', 'service provider': 'hpcl', 'amount': 1100, 'due date': '20/07/2025',
           'status': 'unpaid', 'service': 'gas'},
    2047: {'customer name': 'rohan kamat', 'service provider': 'panjim water board', 'amount': 850,
           'due date': '25/10/2025', 'status': 'paid', 'service': 'water'},
    2048: {'customer name': 'vishal desai', 'service provider': 'jio', 'amount': 599, 'due date': '08/09/2026',
           'status': 'unpaid', 'service': 'mobile'},
}


providerDB = {'goa': 
       {
              'electricity': {'ged':1821},
              'gas':{'iocl':7812, 'hpcl':3388, 'bpcl':3455},
              'water':{'pwd':4280},
              'mobile':{'airtel':4730, 'bsnl':1566, 'jio':9615, 'vi':1290}
              },
       'karnataka': 
       {
              'electricity': {'bescom': 4823, 'mescom': 3591, 'hescom': 2456, 'gescom': 5647, 'cescom': 7632},
              'gas': {'gail': 5123},
              'water': {'bwssb': 6342},
              'mobile': {'airtel': 4730, 'bsnl': 1566, 'jio': 9615, 'vi': 1290}
              },
       'telangana': 
       {
              'electricity': {'tsspdcl': 8021, 'tsnpdcl': 9174},
              'gas': {'bgl': 3491},
              'water': {'hmwssb': 5283},
              'mobile': {'airtel': 4730, 'bsnl': 1566, 'jio': 9615, 'vi': 1290}
              },
       'odisha': 
       {
              'electricity': {'cesu': 7412, 'wesco': 3925, 'neco': 8123, 'sldc': 4598},
              'gas': {'indane': 2645},
              'water': {'owssb': 5339},
              'mobile': {'airtel': 4730, 'bsnl': 1566, 'jio': 9615, 'vi': 1290}
       }
       }


consumerDB = {
    '2037a': {
        'customer name': 'rajesh shetty',
        'state': 'odisha',
        'electricity': {'serviceCode':7412, 'service_provider': 'cesu', 'unit': 48, 'amount': 710, 'due date': '25/06/2025', 'status': 'paid'},
        'mobile': {'service': 4730, 'service_provider': 'airtel', 'amount': 599, 'due date': '15/08/2025', 'status': 'unpaid'}
    },
    '2045a': {
        'customer name': 'pradeep kumar',
        'state': 'karnataka',
        'electricity': {'service': 3591, 'service_provider': 'mescom', 'unit': 55, 'amount': 840, 'due date': '10/07/2025', 'status': 'unpaid'},
        'mobile': {'service': 4730, 'service_provider': 'airtel', 'amount': 710, 'due date': '30/09/2025', 'status': 'paid'},
        'gas': {'service': 5123, 'service_provider': 'gail', 'amount': 1200, 'due date': '05/07/2025', 'status': 'paid'}
    },
    '2052a': {
        'customer name': 'anita singh',
        'state': 'telangana',
        'electricity': {'service': 8021, 'service_provider': 'tsspdcl', 'unit': 65, 'amount': 950, 'due date': '20/07/2025', 'status': 'unpaid'},
        'mobile': {'service': 9651, 'service_provider': 'jio', 'amount': 850, 'due date': '25/08/2025', 'status': 'paid'},
        'gas': {'service': 5283, 'service_provider': 'hmwssb', 'amount': 350, 'due date': '28/06/2025', 'status': 'unpaid'}
    },
    '2061a': {
        'customer name': 'suresh rao',
        'state': 'odisha',
        'electricity': {'service': 7412, 'service_provider': 'cesu', 'unit': 72, 'amount': 1050, 'due date': '12/07/2025', 'status': 'paid'},
        'mobile': {'service': 9651, 'service_provider': 'jio', 'amount': 699, 'due date': '05/09/2025', 'status': 'unpaid'}
    }
}