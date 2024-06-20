from framework import environment


class TestEnvironment:
    def test_report(self):
        """
        Simply tests there is no error calling the report method.
        """
        environment.report()

    def test_controller_or_desktop(self):
        """
        Just a simple test to make sure we are not returning a microcontroller
        and desktop environment
        """
        assert environment.is_running_on_desktop() != environment.is_running_on_microcontroller()

    def test_is_running_in_ci(self):
        """
        Simple test for when running in CI.
        """
        if environment.is_running_in_ci():
            assert not environment.is_running_on_microcontroller()
            assert environment.is_running_on_desktop()
            assert not environment.are_pins_available()
