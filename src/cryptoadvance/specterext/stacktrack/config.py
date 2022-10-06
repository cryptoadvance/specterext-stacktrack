"""
Here Configuration of your Extension takes place
"""


class BaseConfig:
    """ This is an extension-based Config which is used as Base """
    STACKTRACK_SOMEKEY = "some value"


class ProductionConfig(BaseConfig):
    """ This is an extension-based Config for Production """
    pass
