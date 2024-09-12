from interactive import configuration
from interactive.configuration import Config, FIELD_NAME, FIELD_ROLE, FIELD_COORDINATOR


class TestNode:
    def test_config_is_returned(self) -> None:
        """
        Validates configuration defaults are loaded as well as the local overrides
        contained in config.py.
        """
        config = configuration.get_node_config()

        assert config is not None
        assert config.trigger_distance == 99999

        # These are just random configuration values from the config.
        assert configuration.TEST_VALUE == 123.456
        assert configuration.TEST_STRING == "Hello world!"

    def test_config_returns_only_desired_config(self, monkeypatch) -> None:
        """
        Validates the boolean options that control which configuration properties
        are loaded, works as expected. This will mess with state so will restore
        all values it finds.
        """
        monkeypatch.setattr(configuration, 'BUTTON_PIN', "button_pin")
        monkeypatch.setattr(configuration, 'BUZZER_PIN', "buzzer_pin")
        monkeypatch.setattr(configuration, 'BUZZER_VOLUME', "buzzer_volume")
        monkeypatch.setattr(configuration, 'AUDIO_PIN', "audio_pin")
        monkeypatch.setattr(configuration, 'ULTRASONIC_TRIGGER_PIN', "ultrasonic_trigger_pin")
        monkeypatch.setattr(configuration, 'ULTRASONIC_ECHO_PIN', "ultrasonic_echo_pin")
        monkeypatch.setattr(configuration, 'TRIGGER_DISTANCE', "trigger_distance")
        monkeypatch.setattr(configuration, 'TRIGGER_DURATION', "trigger_duration")

        defaults = Config()

        assert not defaults.network
        config = configuration.get_node_config(network=True)
        assert config.network

        config = configuration.get_node_config(button=False)
        assert config.button_pin == defaults.button_pin

        config = configuration.get_node_config(buzzer=False)
        assert config.buzzer_pin == defaults.buzzer_pin
        assert config.buzzer_volume == defaults.buzzer_volume

        config = configuration.get_node_config(audio=False)
        assert config.audio_pin == defaults.audio_pin

        config = configuration.get_node_config(ultrasonic=False)
        assert config.ultrasonic_trigger_pin == defaults.ultrasonic_trigger_pin
        assert config.ultrasonic_echo_pin == defaults.ultrasonic_echo_pin
        assert config.trigger_distance == defaults.trigger_distance
        assert config.trigger_duration == defaults.trigger_duration

    def test_details_returns_correct_values(self, monkeypatch) -> None:
        """
        Validates details returns the correct values. This will mess with state
        so will restore all values it finds.
        """
        monkeypatch.setattr(configuration, 'NODE_NAME', "JacKsoN")
        monkeypatch.setattr(configuration, 'NODE_ROLE', "RaNdOm")
        monkeypatch.setattr(configuration, 'NODE_COORDINATOR', "arbiter")

        details = configuration.details()
        assert len(details.keys()) == 3
        assert set(details.keys()) == {FIELD_NAME, FIELD_ROLE, FIELD_COORDINATOR}
        assert details[FIELD_NAME] == "JacKsoN"
        assert details[FIELD_ROLE] == "RaNdOm"
        assert details[FIELD_COORDINATOR] == "arbiter"
