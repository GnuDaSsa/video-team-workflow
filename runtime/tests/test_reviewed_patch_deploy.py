import pathlib
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / 'tools'))
from deploy_reviewed_patch import merge_bytes, deploy

class ReviewedPatchTests(unittest.TestCase):
    def test_preserves_unrelated_live_change(self):
        base = b'first\nKorean default\nlast\n'
        source = b'first\nEnglish default\nlast\n'
        before = base + b'new unrelated guard\n'
        after = merge_bytes(before, base, source)
        self.assertEqual(after, source + b'new unrelated guard\n')
        self.assertEqual(merge_bytes(after, source, base), before)

    def test_conflicting_context_is_not_overwritten(self):
        with self.assertRaisesRegex(ValueError, 'PATCH_CONTEXT_CONFLICT'):
            merge_bytes(b'first\nconflicting rule\nlast\n',
                        b'first\nKorean default\nlast\n',
                        b'first\nEnglish default\nlast\n')

    def test_explicit_unique_paths_required(self):
        with self.assertRaisesRegex(ValueError, 'EXPLICIT_UNIQUE_SOURCE_LIST_REQUIRED'):
            deploy(pathlib.Path('.'), pathlib.Path('.'), [])
