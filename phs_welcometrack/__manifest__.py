{
    "name": "PHS WelcomeTrack connector",
    "summary": """
        Pharmasimple WelcomeTrack connector""",
    "license": "AGPL-3",
    "author": "Michael Michot",
    "website": "https://github.com/akretion/phs-addons",
    "category": "specific_industry_applications",
    "version": "14.0.1.0.0",
    # any module necessary for this one to work correctly
    "depends": ["base", "base_delivery_carrier_label", "sale_channel"],
    # always loaded
    "data": [
        "data/cron.xml",
        "security/ir.model.access.csv",
        "views/carrier.xml",
        "views/stock_picking.xml",
        "wizard/debug_delivery_label_view.xml",
    ],
    # only loaded in demonstration mode
    "demo": ["demo/demo_welcometrack.xml"],
}
