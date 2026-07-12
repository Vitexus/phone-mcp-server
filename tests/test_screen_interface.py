import json
import pytest
from unittest.mock import patch, AsyncMock

from phone_mcp.tools.screen_interface import get_screen_info, analyze_screen


EMPTY_UI_DUMP = json.dumps({"status": "success", "elements": []})
SCREEN_SIZE = json.dumps({"width": 1080, "height": 1920})
NO_CLICKABLES = json.dumps({"status": "success", "elements": []})


@pytest.mark.asyncio
class TestGetScreenInfoScreenshot:
    """Regression tests for include_screenshot=True.

    get_screen_info() used to call take_screenshot() and json.loads() its
    result, but take_screenshot() returns a plain human-readable status
    string rather than JSON, so this always raised JSONDecodeError and was
    swallowed into a generic "Failed to get screen information" error.
    """

    async def _mocks(self):
        return (
            patch(
                "phone_mcp.tools.screen_interface.dump_ui",
                new_callable=AsyncMock,
                return_value=EMPTY_UI_DUMP,
            ),
            patch(
                "phone_mcp.tools.screen_interface.get_screen_size",
                new_callable=AsyncMock,
                return_value=SCREEN_SIZE,
            ),
            patch(
                "phone_mcp.tools.screen_interface.find_clickable_elements",
                new_callable=AsyncMock,
                return_value=NO_CLICKABLES,
            ),
        )

    async def test_include_screenshot_true_returns_base64_png(self):
        dump_ui_p, size_p, clickable_p = await self._mocks()
        with dump_ui_p, size_p, clickable_p, patch(
            "phone_mcp.tools.screen_interface.run_command", new_callable=AsyncMock
        ) as run_command_mock:
            run_command_mock.return_value = (True, "iVBORw0KGgoAAAANSUhEUg==\n")

            result = json.loads(await get_screen_info(include_screenshot=True))

        assert result["status"] == "success"
        assert result["screenshot"] == "iVBORw0KGgoAAAANSUhEUg=="
        run_command_mock.assert_awaited_once_with("adb exec-out screencap -p | base64")

    async def test_include_screenshot_false_skips_capture(self):
        dump_ui_p, size_p, clickable_p = await self._mocks()
        with dump_ui_p, size_p, clickable_p, patch(
            "phone_mcp.tools.screen_interface.run_command", new_callable=AsyncMock
        ) as run_command_mock:
            result = json.loads(await get_screen_info(include_screenshot=False))

        assert result["status"] == "success"
        assert "screenshot" not in result
        run_command_mock.assert_not_awaited()

    async def test_include_screenshot_capture_failure_yields_empty_string(self):
        dump_ui_p, size_p, clickable_p = await self._mocks()
        with dump_ui_p, size_p, clickable_p, patch(
            "phone_mcp.tools.screen_interface.run_command", new_callable=AsyncMock
        ) as run_command_mock:
            run_command_mock.return_value = (False, "error: no devices/emulators found")

            result = json.loads(await get_screen_info(include_screenshot=True))

        assert result["status"] == "success"
        assert result["screenshot"] == ""

    async def test_analyze_screen_include_screenshot_true(self):
        dump_ui_p, size_p, clickable_p = await self._mocks()
        with dump_ui_p, size_p, clickable_p, patch(
            "phone_mcp.tools.screen_interface.run_command", new_callable=AsyncMock
        ) as run_command_mock:
            run_command_mock.return_value = (True, "iVBORw0KGgoAAAANSUhEUg==\n")

            result = json.loads(await analyze_screen(include_screenshot=True))

        assert result["status"] == "success"
        assert result["screenshot"] == "iVBORw0KGgoAAAANSUhEUg=="
