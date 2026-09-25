import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]


class QmlSecurityTests(unittest.TestCase):
    def test_every_text_item_explicitly_uses_plain_text(self):
        for name in ("BarWidget.qml", "Panel.qml"):
            with self.subTest(name=name):
                source = (ROOT / name).read_text(encoding="utf-8")
                self.assertIsNone(
                    re.search(
                        r"\bText\s*\{(?!\s*textFormat\s*:\s*Text\.PlainText\s*;)",
                        source,
                    ),
                    f"{name} contains a Text item that defaults to Text.AutoText",
                )

    def test_global_demo_action_is_simulated_and_real_action_is_timed(self):
        source = (ROOT / "BarWidget.qml").read_text(encoding="utf-8")
        start = source.index("function runAction(action)")
        end = source.index("function retryJob(jobId)")
        action = source[start:end]
        self.assertIn('root.demoState !== ""', action)
        self.assertIn("demoActionTimer.restart()", action)
        self.assertIn("actionTimeout.restart()", action)

    def test_panel_close_hides_before_touching_bar(self):
        # A throwing bar call before hide() leaves the full-screen overlay grabbing all input.
        source = (ROOT / "Panel.qml").read_text(encoding="utf-8")
        close = re.search(r"function close\(\) \{([^}]*)\}", source).group(1)
        self.assertLess(close.index("controller.hide()"), close.index("setCenterHoverRevealSuppressed"))
        start = source.index("function setCenterHoverRevealSuppressed(value)")
        setter = source[start:source.index("function activeListHeight", start)]
        self.assertIn("bar.setCenterHoverRevealSuppressed(value)", setter)
        self.assertIn("try {", setter)


if __name__ == "__main__":
    unittest.main()
