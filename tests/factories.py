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