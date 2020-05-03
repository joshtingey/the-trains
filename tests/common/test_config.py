import logging

import common.config


def check_base_attributes(config):
    attributes = ['MG_USER', 'MG_PASS', 'MAPBOX_TOKEN', 'CONN_ATTEMPTS',
                  'PPM_FEED', 'TD_FEED']
    types = [str, str, str, int, bool, bool]
    errors = []
    for i, attribute in enumerate(attributes):
        if not hasattr(config, attribute):
            errors.append("No {} attribute".format(attribute))
        if not type(getattr(config, attribute)) == types[i]:
            errors.append("Wrong type for {} attribute".format(attribute))

    assert not errors, "errors occured:\n{}".format("\n".join(errors))


def check_extra_attributes(config):
    attributes = ['MG_URI', 'NR_USER', 'NR_PASS']
    types = [str, str, str]
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


def test_local_attributes():
    local_config = common.config.LocalConfig()
    check_base_attributes(local_config)
    check_extra_attributes(local_config)


def test_docker_attributes():
    docker_config = common.config.DockerConfig()
    check_base_attributes(docker_config)
    check_extra_attributes(docker_config)


def test_prod_attributes():
    prod_config = common.config.ProdConfig()
    check_base_attributes(prod_config)
    check_extra_attributes(prod_config)


def test_logging_handlers():
    test_logger = logging.getLogger('test_logger')
    common.config.Config.init_logging(test_logger)
    assert len(test_logger.handlers) == 1


def test_logging_level():
    test_logger = logging.getLogger('test_logger')
    common.config.Config.init_logging(test_logger)
    assert test_logger.level in [logging.DEBUG, logging.INFO, logging.WARNING]
