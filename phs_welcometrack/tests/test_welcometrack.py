from odoo.tests.common import TransactionCase


class TestWelcomeTrack(TransactionCase):
    """Tests for welcometrack implementation"""

    def setUp(self):
        super(TestWelcomeTrack, self).setUp()

        self.so = self.env.ref("sale.portal_sale_order_1")
        self.so.partner_id.street = "84 rue d'Hauteville"
        self.so.partner_id.street2 = ""
        self.so.partner_id.zip = "75010"
        self.so.partner_id.city = "Paris"
        self.so.partner_id.country_id = self.env.ref("base.fr")

        self.carrier_wt = self.env.ref("phs_welcometrack.welcometrack_carrier_1")
        self.so.carrier_id = self.carrier_wt.id
        self.so.action_confirm()

        self.ref_payload_address = {
            "Address_City": self.so.partner_id.city,
            "Address_Line1": self.so.partner_id.street,
            "Address_Line2": self.so.partner_id.street2 or "",
            "Address_ZipCode": self.so.partner_id.zip,
            "Country_Code": self.so.partner_id.country_id.code,
            "Recipient_Code": self.so.picking_ids.partner_id.id,
            "Recipient_Email": self.so.partner_id.email or "",
            "Recipient_FirstName": self.so.partner_id.name,
            "Recipient_LastName": "",
            "Recipient_Mobile": self.so.partner_id.mobile or "",
        }
        self.ref_payload_order = {
            "Order_Amount": self.so.amount_total,
            "Order_Channel": self.so.sale_channel_id.id or "",
            "Order_DeliveryFees": 0,
            "Order_Reference": self.so.name,
            "Order_Store": "????",
        }
        self.ref_payload_carrier_login = {
            "carrierid": "3",
            "ProviderService_Code": "01",
            "carrier_login": "19869502",
            "carrier_password": "255562",
            "CustomerProvider_Account": "19869502",
        }
        self.ref_payload_sender = {
            "Sender_City": self.carrier_wt.sender_id.city,
            "Sender_Line1": self.carrier_wt.sender_id.street,
            "Sender_Line2": self.carrier_wt.sender_id.street2 or "",
            "Sender_ZipCode": self.carrier_wt.sender_id.zip,
            "Sender_Company": "Pharmasimple",
            "Sender_CountryCode": self.carrier_wt.sender_id.country_id.code,
            "Warehouse_Code": "Defaut",
            "PhoneNumber": "",
        }

        self.ref_payload_label_info = {
            "Label_Format": "PDF",
            "labelcheck": "0",
            "labeloutput": "binary",
        }

        self.ref_payload_package = {
            "Package_Weight": "1",
            "weightunit": "1",
        }

    def test_payload_address(self):
        payload_address = self.so.picking_ids._generate_payload_dest_address()

        self.assertEqual(payload_address, self.ref_payload_address)

    def test_payload_order(self):
        payload_order = self.so.picking_ids._generate_payload_order()

        self.assertEqual(payload_order, self.ref_payload_order)

    def test_payload_carrier_login(self):
        carrier_login = self.so.picking_ids._generate_payload_carrier_login()

        self.assertEqual(carrier_login, self.ref_payload_carrier_login)

    def test_payload_label_info(self):
        label_info = self.so.picking_ids._generate_payload_label_info()

        self.assertEqual(label_info, self.ref_payload_label_info)

    def test_payload_sender(self):
        sender = self.so.picking_ids._generate_payload_sender()

        self.assertEqual(sender, self.ref_payload_sender)

    def test_payload_package(self):
        package = self.so.picking_ids._generate_payload_package()

        self.assertEqual(package, self.ref_payload_package)

    def test_send_to_shipper(self):
        label = self.so.picking_ids.send_to_shipper()

        self.assertEqual(label, [])
