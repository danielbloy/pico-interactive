from collections.abc import Callable, Awaitable

import pytest

from framework.button import ButtonController
from framework.polyfills.button import Button
from framework.runner import Runner


class TestButton(Button):
    def __init__(self):
        super().__init__(None)


class TestButtonController:

    def test_creating_with_none_button_errors(self) -> None:
        """
        Validates that a ButtonController cannot be constructed with
        a None value.
        """
        with pytest.raises(ValueError):
            ButtonController(None)

    def test_creating_with_string_errors(self) -> None:
        """
        Validates that a ButtonController cannot be constructed with
        a value that is not a Button.
        """
        with pytest.raises(ValueError):
            ButtonController("")

    def test_adding_single_click_handler(self) -> None:
        """
        Straightforward validation that a handler can be added
        as well as removed without raising an error.
        """
        button = TestButton()
        controller = ButtonController(button)

        # This should be fine.
        controller.add_single_click_handler(None)

        async def handler():
            pass

        # This will also be fine.
        controller.add_single_click_handler(handler)

        # This will also be fine.
        controller.add_single_click_handler(None)

    def test_adding_multi_click_handler(self) -> None:
        """
        Straightforward validation that a handler can be added
        as well as removed without raising an error.
        """
        button = TestButton()
        controller = ButtonController(button)

        # This should be fine.
        controller.add_multi_click_handler(None)

        async def handler():
            pass

        # This will also be fine.
        controller.add_multi_click_handler(handler)

        # This will also be fine.
        controller.add_multi_click_handler(None)

    def test_adding_long_press_handler(self) -> None:
        """
        Straightforward validation that a handler can be added
        as well as removed without raising an error.
        """
        button = TestButton()
        controller = ButtonController(button)

        # This should be fine.
        controller.add_long_press_handler(None)

        async def handler():
            pass

        # This will also be fine.
        controller.add_long_press_handler(handler)

        # This will also be fine.
        controller.add_long_press_handler(None)

    def test_registering_with_runner(self) -> None:
        """
        Validates the ButtonController registers with the Runner.
        """
        add_task_count: int = 0

        class TestRunner(Runner):
            def add_task(self, task: Callable[[], Awaitable[None]]) -> None:
                nonlocal add_task_count
                add_task_count += 1

        runner = TestRunner()
        button = TestButton()
        controller = ButtonController(button)
        assert add_task_count == 0
        controller.register(runner)
        assert add_task_count == 1

    # TODO: Test running with non handlers.
    # TODO: Test running with one handler with many event types
    # TODO: Test running with multi handlers with many event types.
