import unittest
from unittest.mock import patch

from scripts.utils.window_layout import get_bottom_margin, get_interface_scale


class InterfaceScaleTests(unittest.TestCase):
    def test_scale_fits_both_dimensions(self):
        for width, height in ((1920, 1080), (1280, 720), (1024, 640), (3840, 2160)):
            scale = get_interface_scale(width, height, 1920, 1080)
            self.assertLessEqual(1920 * scale, width)
            self.assertLessEqual(1080 * scale, height)
            self.assertLessEqual(scale, 1)
            self.assertGreater(scale, 0)

    def test_invalid_dimensions_are_reported(self):
        with self.assertRaises(ValueError):
            get_interface_scale(0, 720, 1920, 1080)


class BottomMarginTests(unittest.TestCase):
    def test_default_for_wsl(self):
        with patch.dict("os.environ", {"WSL_DISTRO_NAME": "Ubuntu"}, clear=True):
            self.assertEqual(get_bottom_margin(), 64)

    def test_wsl_kernel_without_environment_variable(self):
        with patch.dict("os.environ", {}, clear=True):
            with patch("platform.release", return_value="6.18-microsoft-standard-WSL2"):
                self.assertEqual(get_bottom_margin(), 64)

    def test_default_for_other_desktops(self):
        with patch.dict("os.environ", {}, clear=True):
            with patch("platform.release", return_value="6.18-generic"):
                self.assertEqual(get_bottom_margin(), 0)

    def test_configured_margin(self):
        for value in (0, 48, 96):
            with self.subTest(value=value):
                with patch.dict("os.environ", {"SMARTYPER_BOTTOM_MARGIN": str(value)}, clear=True):
                    self.assertEqual(get_bottom_margin(), value)

    def test_invalid_margin_is_reported(self):
        for value in ("-1", "abc", "48.5", ""):
            with self.subTest(value=value):
                with patch.dict("os.environ", {"SMARTYPER_BOTTOM_MARGIN": value}, clear=True):
                    with self.assertRaisesRegex(ValueError, "non-negative integer"):
                        get_bottom_margin()
