
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
from factory.fuzzy import FuzzyChoice

from service.models import Shopcart, Item


# pylint: disable=R0903
class ShopcartFactory(factory.Factory):
    """Creates fake Shopcarts"""

    class Meta:
        """ ShopcartFactory Meta """
        model = Shopcart

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")

    @factory.post_generation
    def items(self, create, extracted, **kwargs):   # pylint: disable=method-hidden, unused-argument
        """Creates the items list"""
        if not create:
            return

        if extracted:
            self.items = extracted


# pylint: disable=R0903
class ItemFactory(factory.Factory):
    """Creates fake Items"""

    class Meta:
        """ ItemFactory Meta """
        model = Item

    id = factory.Sequence(lambda n: n)
    shopcart_id = None
    name = FuzzyChoice(choices=["Air Pods", "iPhone SE", "Macbook Air"])
    quantity = 1
    price = factory.Faker("pyfloat", positive=True)
