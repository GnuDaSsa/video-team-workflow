from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
GLOBAL = ROOT / 'GLOBAL_AGENTS.md'
SKILL = ROOT / 'codex-skills/videodirector/SKILL.md'
REFS = SKILL.parent / 'references'


class GlobalVideoLazyLoadTests(unittest.TestCase):
    def test_global_startup_is_bounded_but_safety_remains(self):
        text = GLOBAL.read_text(encoding='utf-8')
        self.assertLess(len(text), 20000)
        for marker in (
            'Video craft memory — load only the matching phase',
            'Subagent / lane spawn approval gate',
            'Codex Harness Auto Workflow',
            'Public contest upload/submission safety',
            'ChatGPT web send-button safety',
            'Kim Gu contest submission email',
            'Video-team authority order',
            'Gongnyang image-prompt compiler default',
        ):
            self.assertIn(marker, text)

    def test_removed_guidance_has_a_single_deferred_home(self):
        global_text = GLOBAL.read_text(encoding='utf-8')
        skill_text = SKILL.read_text(encoding='utf-8')
        groups = {
            'mode-calibrations.md': ('Video Agent Memory Routing',),
            'mv-production-calibrations.md': ('Music Video Production Team Standing Rules',),
            'character-identity-calibrations.md': ('Three-panel character identity standard',),
            'typography-calibrations.md': (
                'Typography and transition QC standing rule',
                'CapCut Korean caption shadow/legibility rule',
                'CapCut-first typography revision rule',
                'CapCut font limitation / baked typography exception',
                'MV typography/editing lesson',
                'CapCut editable text visual alignment lesson',
            ),
        }
        for name, markers in groups.items():
            self.assertIn(name, global_text)
            self.assertIn(name, skill_text)
            ref_text = (REFS / name).read_text(encoding='utf-8')
            for marker in markers:
                self.assertIn(marker, ref_text)
                self.assertNotIn('## ' + marker, global_text)


if __name__ == '__main__':
    unittest.main()
