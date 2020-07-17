import params


class Vehicle:
    """ Type
        1. Combustion: 'gas'
        2. Electric: 'green'

        CO2 emission reduction is the goal
        """
    def __init__(self, _type='gas',
                 production_cost=params.production_cost['gas'],
                 ee=params.energy_economy['gas'],
                 ec=params.energy_capacity['gas'],
                 ql=params.quality_level['gas'],
                 firm=None):
        # Type: 'combustion' or 'electric'
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

    def autonomy(self):
        return self.EE * self.EC

    def running_cost(self):
        return params.price_energy[self.type]/self.EE

    def emissions(self):
        return params.emission[self.type]/self.EE

    def calculate_price(self):
        self.sales_price = (1 + params.iva) * (1 + params.p_lambda) * self.production_cost - 1

    def criteria_selection(self, emotion):
        criteria = {'price_accessibility': 1/self.sales_price,
                    # TODO: Check that Det is really car.autonomy()
                    'use_accessibility': 1/self.autonomy(),
                    'stations': params.stations[self.type],
                    'market_share': max(self.firm.sold_cars[self.type] / self.firm.sim.num_cars[self.type],
                                        self.firm.sim.current_data['epsilon']),
                    'energy_capacity': self.EC,
                    'car_cleanness': 1/self.EC,
                    'quality': self.QL,
                    'emotion': emotion}

        criteria1, criteria2 = self.firm.sim.seed.choices(criteria, k=2)
        return criteria[criteria1] * criteria[criteria2]