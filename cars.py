import params


class Vehicle:
    """ Type
        1. Combustion: 'gas'
        2. Electric: 'green'

        CO2 emission reduction is the goal
        """
    def __init__(self, _type='gas',
                 production_cost=params.production_cost['gas'],
                 # Distance (km) a car can travel per unit of energy consumed
                 ee=params.energy_economy['gas'],
                 # Storage size
                 ec=params.energy_capacity['gas'],
                 # Performance measure ~= quality characteristics
                 ql=params.quality_level['gas'],
                 firm=None):
        # Type: 'combustion' or 'electric', 'gas' or 'green'
        self.type = _type
        # Price (production_cost)
        self.production_cost = production_cost
        # Energy: distance per unit of energy (engine power per km)
        self.EE = ee
        # Energy capacity: quantity of units able to carry
        self.EC = ec
        # Quality
        self.QL = ql
        self.firm = firm
        self.sales_price = None
        self.calculate_price()
        self.owed_taxes = 0
        self.policy_value_discount = 0

    def drive_range(self):
        # Driving range (DR)
        return self.EE * self.EC

    def emissions(self):
        return params.emission[self.type]/self.EE

    def calculate_price(self):
        policy_value, policy_tax = 0, 0
        e_parameter = params.discount_tax_table(self.firm.sim.e, self.emissions())
        if self.firm.sim.policy['policy'] == 'tax':
            # First part refers to 'low', 'high' [.1, .5], Second refers to Table 5 levels
            policy_tax = params.tax[self.firm.sim.policy['level']] * e_parameter
        elif self.firm.sim.policy['policy'] == 'discount':
            policy_value = params.discount[self.firm.sim.policy['level']] * e_parameter
        elif self.firm.sim.policy['policy'] == 'green_support':
            # Only for green cars that perform less than average benchmark
            if self.type == 'green' and self.emissions() < self.firm.sim.e:
                policy_value = params.green_support[self.firm.sim.policy['level']] * e_parameter
        # policy_value é DESCONTO. policy_tax é SOBRETAXA OU DESCONTO NA TAXA
        # TODO: política brasileira
        # Politica Brasileira: descontar do IVA  no minimo 3% quando a fabrica inicia desenvolvimento do carro eletrico
        self.sales_price = (1 + params.iva) * (1 + params.p_lambda) * \
                           (1 + policy_tax) * self.production_cost + policy_value
        # QUAL CUSTO O GOVERNO DEIXA DE RECEBER, QUAL DEIXA A FIRMA?
        self.owed_taxes = (policy_tax + params.iva) * self.production_cost
        self.policy_value_discount = policy_value
        return self.owed_taxes + self.policy_value_discount

    def criteria_selection(self, emotion, criteria1, criteria2):
        ms1 = self.firm.market_share[self.type][self.firm.sim.t]
        criteria = {'car_affordability': 1 / self.sales_price,
                    'use_affordability': 1 / params.price_energy[self.type],
                    'stations': params.stations['gas'] if self.type == 'gas'
                    else self.firm.sim.green_stations[self.firm.sim.t],
                    'market_share': max(ms1, params.epsilon),
                    'energy_capacity': self.EC,
                    'car_cleanness': 1 / self.emissions(),
                    'quality': self.QL,
                    'emotion': emotion}

        return criteria[criteria1] * criteria[criteria2]
