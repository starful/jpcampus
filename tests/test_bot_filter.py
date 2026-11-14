import unittest

from app.bot_filter import is_mobile_user_agent, is_suspected_bot

MOBILE_UAS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/17.0 Mobile/15E148 Safari/604.1",
]


class BotFilterMobileTests(unittest.TestCase):
    def test_mobile_browsers_are_detected_as_mobile(self):
        for ua in MOBILE_UAS:
            self.assertTrue(is_mobile_user_agent(ua), ua)

    def test_mobile_browsers_are_never_flagged_as_suspect_bots(self):
        for ua in MOBILE_UAS:
            self.assertFalse(is_suspected_bot(ua), ua)

    def test_desktop_browser_is_not_mobile(self):
        desktop_ua = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.assertFalse(is_mobile_user_agent(desktop_ua))


if __name__ == "__main__":
    unittest.main()
