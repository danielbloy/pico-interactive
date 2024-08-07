from interactive import configuration
from interactive.configuration import Config


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

    def test_config_returns_only_desired_config(self) -> None:
        """
        Validates the boolean options that control which configuration properties
        are loaded, works as expected. This will mess with state so will restore
        all values it finds.
        """
        # Copy original configuration state.
        original_config = configuration.get_node_config()

        configuration.BUTTON_PIN = "button_pin"
        configuration.BUZZER_PIN = "buzzer_pin"
        configuration.BUZZER_VOLUME = "buzzer_volume"
        configuration.AUDIO_PIN = "audio_pin"
        configuration.ULTRASONIC_TRIGGER_PIN = "ultrasonic_trigger_pin"
        configuration.ULTRASONIC_ECHO_PIN = "ultrasonic_echo_pin"
        configuration.TRIGGER_DISTANCE = "trigger_distance"
        configuration.TRIGGER_DURATION = "trigger_duration"

        try:
            defaults = Config()

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

        finally:
            # Restore original configuration state.
            configuration.BUTTON_PIN = original_config.button_pin
            configuration.BUZZER_PIN = original_config.buzzer_pin
            configuration.BUZZER_VOLUME = original_config.buzzer_volume
            configuration.AUDIO_PIN = original_config.audio_pin
            configuration.ULTRASONIC_TRIGGER_PIN = original_config.ultrasonic_trigger_pin
            configuration.ULTRASONIC_ECHO_PIN = original_config.ultrasonic_echo_pin
            configuration.TRIGGER_DISTANCE = original_config.trigger_distance
            configuration.TRIGGER_DURATION = original_config.trigger_duration
