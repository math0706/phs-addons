from dateutil.relativedelta import relativedelta

from odoo.tests.common import TransactionCase


class TestProductAutoTags(TransactionCase):
    """Tests tags on product"""

    def setUp(self):
        super(TestProductAutoTags, self).setUp()
        self.product_template = self.env["product.template"]
        self.product_categ_id = self.env["product.category"].search(
            [("name", "=", "All")]
        )
        self.tag_new = self.env.ref("phs_product_auto_tags.tag_new")

    def test_new_tag_product(self):
        """Test if when product is created, the tag 'new' is set on the product """
        vals = {
            "name": "test_product",
            "type": "consu",
            "categ_id": self.product_categ_id.id,
            "tag_ids": [],
        }
        new_product = self.product_template.create(vals)
        self.assertTrue(self.tag_new.id in new_product.tag_ids.ids)

    def test_untagged_new_on_product(self):
        """Test for check if the tag new is del after few days"""
        vals = {
            "name": "test_product",
            "type": "consu",
            "categ_id": self.product_categ_id.id,
            "tag_ids": [],
            # "create_date": datetime.now() - timedelta(days=14)
        }
        new_product = self.product_template.create(vals)
        new_product.create_date += relativedelta(days=-14)
        self.product_template.update_tag_new()
        self.assertFalse(self.tag_new.id in new_product.tag_ids.ids)
