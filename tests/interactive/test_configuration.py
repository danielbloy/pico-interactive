from interactive import configuration


class TestNode:
    def test_config_is_returned(self) -> None:
        """
        Tests that configuration defaults are loaded as well as the local overrides
        contained in config.py.
        """
        config = configuration.get_node_config()

        assert config is not None
        assert config.trigger_distance == 99999

        # These are just random configuration values from the config.
        assert configuration.TEST_VALUE == 123.456
        assert configuration.TEST_STRING == "Hello world!"
