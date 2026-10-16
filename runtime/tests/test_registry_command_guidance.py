import sys
from pathlib import Path
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import media_registry as registry

class GuidanceTests(unittest.TestCase):
 def test_character_promote_fails_with_safe_recovery(self):
  with patch.object(registry,'get_asset',return_value={'kind':'character'}):
   with self.assertRaisesRegex(ValueError,'set-state.*does not authorize approval'):
    registry.promote(Path('/tmp/fixture'),'fixture')
