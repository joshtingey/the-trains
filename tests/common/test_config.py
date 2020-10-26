import logging

import common.config


def check_base_attributes(config):
    attributes = [
        "MONGO_USER",
        "MONGO_PASS",
        "MONGO_URI",
        "DASH_MAPBOX_TOKEN",
        "COLLECTOR_NR_USER",
        "COLLECTOR_NR_PASS",
        "COLLECTOR_ATTEMPTS",
        "COLLECTOR_PPM",
        "COLLECTOR_TD",
        "COLLECTOR_TM",
        "GENERATOR_RATE",
        "GENERATOR_K",
        "GENERATOR_ITER",
        "GENERATOR_CUT_D",
        "GENERATOR_SCALE",
        "GENERATOR_DELTA_B",
        "GENERATOR_DELTA_T",
    ]
    types = [
        str,
        str,
        str,
        str,
        str,
        str,
        int,
        bool,
        bool,
        bool,
        int,
        float,
        int,
        float,
        int,
        int,
        int,
    ]
    errors = []
    for i, attribute in enumerate(attributes):
        if not hasattr(config, attribute):
            errors.append("No {} attribute".format(attribute))
        if not type(getattr(config, attribute)) == types[i]:
            errors.append("Wrong type for {} attribute".format(attribute))

    assert not errors, "errors occured:\n{}".format("\n".join(errors))


def test_base_attributes():
    base_config = common.config.Config()
    check_base_attributes(base_config)


def test_logging_handlers():
    test_logger = logging.getLogger("test_logger")
    common.config.Config.init_logging(test_logger)
    assert len(test_logger.handlers) == 1


def test_logging_level():
    test_logger = logging.getLogger("test_logger")
    common.config.Config.init_logging(test_logger)
    assert test_logger.level in [logging.DEBUG, logging.INFO, logging.WARNING]
