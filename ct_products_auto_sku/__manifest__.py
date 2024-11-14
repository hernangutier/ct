

{
    "name": "Autogenerar SKU por Categoria de Productos",
    "version": "13.0.2.0.3",
    "author": "H.G.L. SISTEMAS, F.P.",
    "website": "https://hgl.com",
    "license": "AGPL-3",
    "category": "Product",
    "depends": ["product"],
    "data": [
        "data/product_sequence.xml",
        "views/product_category.xml",
        "views/res_config_settings_views.xml",
        "wizard/wizard.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "installable": True,
}
