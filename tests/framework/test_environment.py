from framework import environment


class TestEnvironment():
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
        assert environment.is_running_on_desktop() != environment.__is_running_on_microcontroller
