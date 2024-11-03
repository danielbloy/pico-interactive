from collections.abc import Callable, Awaitable

import pytest

from interactive.button import ButtonController
from interactive.polyfills.button import Button
from interactive.runner import Runner


class MockButton(Button):
    def __init__(self):
        super().__init__(None)
        self.short_count_pattern = [0]
        self.short_count_index = 0

        self.long_press_pattern = [False]
        self.long_press_index = 0

        self.update_count = 0

    def update(self) -> None:
        self.update_count += 1

    @property
    def short_count(self) -> int:
        if len(self.short_count_pattern) == 0:
            return 0

        if self.short_count_index >= len(self.short_count_pattern):
            self.short_count_index = 0

        result = self.short_count_pattern[self.short_count_index]
        self.short_count_index += 1

        return result

    @property
    def long_press(self) -> bool:
        if len(self.long_press_pattern) == 0:
            return False

        if self.long_press_index >= len(self.long_press_pattern):
            self.long_press_index = 0

        result = self.long_press_pattern[self.long_press_index]
        self.long_press_index += 1

        return result


class TestButtonController:

    def test_creating_with_none_button_errors(self) -> None:
        """
        Validates that a ButtonController cannot be constructed with
        a None value.
        """
        with pytest.raises(ValueError):
            # noinspection PyTypeChecker
            ButtonController(None)

    def test_creating_with_string_errors(self) -> None:
        """
        Validates that a ButtonController cannot be constructed with
        a value that is not a Button.
        """
        with pytest.raises(ValueError):
            # noinspection PyTypeChecker
            ButtonController("")

    def test_adding_single_click_handler(self) -> None:
        """
        Straightforward validation that a handler can be added
        as well as removed without raising an error.
        """
        button = MockButton()
        controller = ButtonController(button)

        # This should be fine.
        controller.add_single_press_handler(None)

        async def handler():
            pass

        # This will also be fine.
        controller.add_single_press_handler(handler)

        # This will also be fine.
        controller.add_single_press_handler(None)

    def test_adding_multi_click_handler(self) -> None:
        """
        Straightforward validation that a handler can be added
        as well as removed without raising an error.
        """
        button = MockButton()
        controller = ButtonController(button)

        # This should be fine.
        controller.add_multi_press_handler(None)

        async def handler():
            pass

        # This will also be fine.
        controller.add_multi_press_handler(handler)

        # This will also be fine.
        controller.add_multi_press_handler(None)

    def test_adding_long_press_handler(self) -> None:
        """
        Straightforward validation that a handler can be added
        as well as removed without raising an error.
        """
        button = MockButton()
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
            def add_loop_task(self, task: Callable[[], Awaitable[None]]) -> None:
                nonlocal add_task_count
                add_task_count += 1

        runner = TestRunner()
        button = MockButton()
        controller = ButtonController(button)
        assert add_task_count == 0
        controller.register(runner)
        assert add_task_count == 1

    def test_running_with_no_handler(self) -> None:
        """
        Validates that running with no handlers does not error even
        though the button is generating events.
        """
        called_count: int = 0

        async def callback():
            nonlocal called_count
            called_count += 1
            runner.cancel = called_count >= 10

        runner = Runner()
        button = MockButton()
        button.short_count_pattern = [0, 1, 2]
        button.long_press_pattern = [True, False]
        controller = ButtonController(button)
        controller.register(runner)
        runner.run(callback)

        assert called_count == 10
        assert button.update_count > 10

    def test_running_with_only_single_click_handler(self) -> None:
        """
        Validates that running with just the single-press handler only
        raises single-ress events.
        """
        called_count: int = 0

        async def callback():
            nonlocal called_count
            called_count += 1
            runner.cancel = called_count >= 10

        single_click_count: int = 0

        async def single_click():
            nonlocal single_click_count
            single_click_count += 1

        runner = Runner()
        button = MockButton()
        controller = ButtonController(button)
        controller.add_single_press_handler(single_click)
        controller.register(runner)

        # First we run generating all events except single-press
        button.short_count_pattern = [0, 2, 3]
        button.long_press_pattern = [True, False]
        runner.run(callback)

        assert called_count == 10
        assert button.update_count > 10
        assert single_click_count == 0

        # Now we run generating all events
        called_count = 0
        button.update_count = 0
        button.short_count_pattern = [0, 1, 2, 3]
        runner.run(callback)

        assert called_count == 10
        assert button.update_count > 10
        assert single_click_count > 0

    def test_running_with_only_multi_click_handler(self) -> None:
        """
        Validates that running with just the multi-press handler only
        raises multi-press events.
        """
        called_count: int = 0

        async def callback():
            nonlocal called_count
            called_count += 1
            runner.cancel = called_count >= 10

        multi_click_count: int = 0

        async def multi_click():
            nonlocal multi_click_count
            multi_click_count += 1

        runner = Runner()
        button = MockButton()
        controller = ButtonController(button)
        controller.add_multi_press_handler(multi_click)
        controller.register(runner)

        # First we run generating all events except multi-press
        button.short_count_pattern = [0, 1]
        button.long_press_pattern = [True, False]
        runner.run(callback)

        assert called_count == 10
        assert button.update_count > 10
        assert multi_click_count == 0

        # Now we run generating all events
        called_count = 0
        button.update_count = 0
        button.short_count_pattern = [0, 1, 2, 3]
        runner.run(callback)

        assert called_count == 10
        assert button.update_count > 10
        assert multi_click_count > 0

    def test_running_with_only_long_press_handler(self) -> None:
        """
        Validates that running with just the long-press handler only
        raises long-press events.
        """
        called_count: int = 0

        async def callback():
            nonlocal called_count
            called_count += 1
            runner.cancel = called_count >= 10

        long_press_count: int = 0

        async def long_press():
            nonlocal long_press_count
            long_press_count += 1

        runner = Runner()
        button = MockButton()
        controller = ButtonController(button)
        controller.add_long_press_handler(long_press)
        controller.register(runner)

        # First we run generating all events except long-presses
        button.short_count_pattern = [0, 1, 2, 3]
        button.long_press_pattern = [False]
        runner.run(callback)

        assert called_count == 10
        assert button.update_count > 10
        assert long_press_count == 0

        # Now we run generating all events
        called_count = 0
        button.update_count = 0
        button.long_press_pattern = [True, False]
        runner.run(callback)

        assert called_count == 10
        assert button.update_count > 10
        assert long_press_count > 0

    def test_running_with_all_handlers(self) -> None:
        """
        Validates running with all handlers and only the correct ones
        are triggered.
        """
        called_count: int = 0

        async def callback():
            nonlocal called_count
            called_count += 1
            runner.cancel = called_count >= 10

        single_click_count: int = 0

        async def single_click():
            nonlocal single_click_count
            single_click_count += 1

        multi_click_count: int = 0

        async def multi_click():
            nonlocal multi_click_count
            multi_click_count += 1

        long_press_count: int = 0

        async def long_press():
            nonlocal long_press_count
            long_press_count += 1

        runner = Runner()
        button = MockButton()
        controller = ButtonController(button)
        controller.add_single_press_handler(single_click)
        controller.add_multi_press_handler(multi_click)
        controller.add_long_press_handler(long_press)
        controller.register(runner)

        # First we run generating no events.
        button.short_count_pattern = [0]
        button.long_press_pattern = [False]
        runner.run(callback)

        assert called_count == 10
        assert button.update_count > 10
        assert single_click_count == 0
        assert multi_click_count == 0
        assert long_press_count == 0

        # Now we run generating just single-press events
        called_count = 0
        button.update_count = 0
        button.short_count_pattern = [0, 1]
        single_click_count = 0
        multi_click_count = 0
        long_press_count = 0
        runner.run(callback)

        assert called_count == 10
        assert button.update_count > 10
        assert single_click_count > 0
        assert multi_click_count == 0
        assert long_press_count == 0

        # Now we run generating just multi-press events
        called_count = 0
        button.update_count = 0
        button.short_count_pattern = [0, 2, 3]
        single_click_count = 0
        multi_click_count = 0
        long_press_count = 0
        runner.run(callback)

        assert called_count == 10
        assert button.update_count > 10
        assert single_click_count == 0
        assert multi_click_count > 0
        assert long_press_count == 0

        # Now we run generating just long-press events
        called_count = 0
        button.update_count = 0
        button.short_count_pattern = [0]
        button.long_press_pattern = [False, True]
        single_click_count = 0
        multi_click_count = 0
        long_press_count = 0
        runner.run(callback)

        assert called_count == 10
        assert button.update_count > 10
        assert single_click_count == 0
        assert multi_click_count == 0
        assert long_press_count > 0

        # Now we run generating all events
        called_count = 0
        button.update_count = 0
        button.short_count_pattern = [0, 1, 2, 3]
        button.long_press_pattern = [False, True]
        single_click_count = 0
        multi_click_count = 0
        long_press_count = 0
        runner.run(callback)

        assert called_count == 10
        assert button.update_count > 10
        assert single_click_count > 0
        assert multi_click_count > 0
        assert long_press_count > 0
