import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import author_handoff as h
import model_routing as m

class AuthorHandoffTests(unittest.TestCase):
    def test_session_model_not_pinned(self):
        for lane in ('director','music','image_qc','seedance_qc','editor','package'):
            self.assertIsNone(m.resolve(lane)['model'])
        self.assertEqual(m.resolve('planner')['model'], 'gpt-6-astra')
        for lane in ('image_creator_01','image_creator_02'):
            self.assertIsNone(m.resolve(lane,'production')['model'])
            self.assertEqual(m.resolve(lane,'prompting')['model'], 'gpt-6-astra')

    def test_payload_and_approval(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td); (p/'brief.md').write_text('brief')
            args=(td,'A','video',['brief.md'],'lanes/seedance/prompts')
            with self.assertRaises(ValueError): h.request(*args,'')
            r=h.request(*args,'astra-author:video:A')
            self.assertEqual(r['model'],'gpt-6-astra')
            self.assertEqual(r['fork_turns'],'none')
            self.assertIn('Do not use browser', r['message'])
            self.assertIn('not alone',r['message'])
            with self.assertRaises(ValueError): h.request(td,'A','video',['brief.md'],'../escape','astra-author:video:A')

    def test_immutable_block_and_every_input(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            for name in ('prompt','settings','pack','ref'):(p/name).write_text(name)
            row=lambda name:dict(path=name,sha256=h.digest(p/name))
            r=dict(block_id='A',status='READY_FOR_EXECUTION',prompt=row('prompt'),settings=row('settings'),pack=row('pack'),references=[row('ref')])
            self.assertTrue(h.verify(td,r,'A')['ok'])
            self.assertFalse(h.verify(td,r,'A')['author_identity_verified'])
            with self.assertRaises(ValueError):h.verify(td,r,'ALT')
            for name in ('prompt','settings','pack','ref'):
                (p/name).write_text('drift')
                with self.assertRaises(ValueError):h.verify(td,r,'A')
                (p/name).write_text(name)
