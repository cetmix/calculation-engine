import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-cetmix-calculation-engine",
    description="Meta package for cetmix-calculation-engine Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-cetmix_calculation>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
