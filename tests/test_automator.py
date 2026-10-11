#!/usr/bin/env python3
"""
Unit tests for AutonomousAutomator (src/automator.py).
Tests launchd plist generation with XML escaping and skill creation.
"""

import unittest
import tempfile
from pathlib import Path
from src.automator import AutonomousAutomator

class TestAutomator(unittest.TestCase):

    def test_launchd_plist_xml_escaping(self):
        with tempfile.TemporaryDirectory() as td:
            automator = AutonomousAutomator(Path(td) / "skills")
            
            # Injection characters in command
            malicious_cmd = 'echo "hello" && python3 script.py --param "<injection>&foo=\'bar\'"'
            plist = automator.generate_launchd_plist("test_job", malicious_cmd, 1800)

            self.assertIn("&quot;hello&quot;", plist)
            self.assertIn("&amp;&amp;", plist)
            self.assertIn("&lt;injection&gt;", plist)
            self.assertIn("&apos;bar&apos;", plist)
            # Ensure unescaped raw '<injection>' is not present
            self.assertNotIn('<injection>', plist)

if __name__ == "__main__":
    unittest.main()
