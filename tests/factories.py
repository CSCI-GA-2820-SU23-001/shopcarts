<<<<<<< HEAD
import factory
from datetime import date
from factory.fuzzy import FuzzyChoice, FuzzyDate
from service.models import Shopcart, Item
import random

class ShopcartFactory(factory.Factory):
    """Persistent class"""
    class Meta:
        model = Shopcart

    customer_id = 1#factory.Sequence(lambda n: n)
    ## name = factory.Faker("name")
    #date = FuzzyDate(date(2023, 1, 1))
    #total = round(random.uniform(1.00, 1000.00), 2)
    #email = factory.Faker("email")

    @factory.post_generation
    def items(self, create, extracted, **kwargs):   # pylint: disable=method-hidden, unused-argument
        """Creates the items list"""
        if not create:
            return

        if extracted:
            self.items = extracted

class ItemFactory(factory.Factory):
    """Creates fake Items"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""
        model = Item

    item_id = 1#factory.Sequence(lambda n: n)
    #quantity = factory.Faker('random_int', min=1, max=10)
    #total = round(random.uniform(1.00, 100.00), 2)
    customer_id = None
    #shopcart = factory.SubFactory(ShopcartFactory)
=======
# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Shopcart, Item

class ShopcartFactory(factory.Factory):
    """Creates fake Shopcarts"""

    class Meta:
        model = Shopcart

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")

    @factory.post_generation
    def items(self, create, extracted, **kwargs):
        if not create:
            return
        
        if extracted:
            self.addresses = extracted

class ItemFactory(factory.Factory):
    """Creates fake Items"""
    
    class Meta:
        model = Item
    
    id = factory.Faker("pyint")
    shopcart_id = None
    name = factory.Faker("job")
    quantity = factory.Faker("pyint")
    price = factory.Faker("pyfloat")
>>>>>>> master
