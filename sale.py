# -*- coding: utf-8 -*-
"""
    sale.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import math
from decimal import Decimal

from trytond.model import fields
from trytond.pool import PoolMeta, Pool

__all__ = ['SaleLine', 'Sale']
__metaclass__ = PoolMeta


class Sale:
    "Sale"
    __name__ = 'sale.sale'

    package_weight = fields.Function(
        fields.Float("Package weight", digits=(16,  2)),
        'get_package_weight'
    )

    def get_package_weight(self, name):
        """
        Returns sum of weight associated with each line
        """
        return sum(
            map(lambda line: line.get_weight(), self.lines)
        )


class SaleLine:
    'Sale Line'
    __name__ = 'sale.line'

    @classmethod
    def __setup__(cls):
        super(SaleLine, cls).__setup__()
        cls._error_messages.update({
            'weight_required': 'Weight is missing on the product %s',
        })

    def get_weight(self, weight_uom):
        """
        Returns weight as required for carriers

        :param weight_uom: Weight uom used by carriers
        """
        ProductUom = Pool().get('product.uom')

        if not self.product or self.quantity <= 0 or \
                self.product.type == 'service':
            return Decimal('0')

        if not self.product.template.weight:
            self.raise_user_error(
                'weight_required',
                error_args=(self.product.name,)
            )

        # Find the quantity in the default uom of the product as the weight
        # is for per unit in that uom
        if self.unit != self.product.default_uom:
            quantity = ProductUom.compute_qty(
                self.unit,
                self.quantity,
                self.product.default_uom
            )
        else:
            quantity = self.quantity

        weight = float(self.product.weight) * quantity

        # Compare product weight uom with the weight uom used by carrier
        # and calculate weight if botth are not same
        if self.product.weight_uom.symbol != weight_uom.symbol:
            weight = ProductUom.compute_qty(
                self.product.weight_uom,
                weight,
                weight_uom,
            )
        return math.ceil(weight)
