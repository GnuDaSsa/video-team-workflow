import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import model_routing as m


class ExistingOwnerHandoffTests(unittest.TestCase):
    def args(self):
        return dict(manager_id='00000000-0000-0000-0000-000000000001',
                    owner_id='00000000-0000-0000-0000-000000000002',
                    owner_status='idle', phase='production', action='Verify accepted jobs; do not resubmit.')

    def test_recipient_is_executor_not_manager(self):
        a = self.args(); r = m.existing_owner_handoff(**a)
        self.assertEqual(r['threadId'], a['owner_id'])
        self.assertIn('재전송하거나', r['prompt'])
        self.assertIn('이 작업의 final', r['prompt'])
        self.assertEqual(r['model'], m.LUNA_MODEL)

    def test_authoring_uses_actual_native_model_argument(self):
        a = self.args(); a['phase'] = 'prompting'
        r = m.existing_owner_handoff(**a)
        self.assertEqual((r['model'], r['thinking']), ('gpt-6-astra', 'xhigh'))

    def test_same_recipient_rejected(self):
        a = self.args(); a['owner_id'] = a['manager_id']
        with self.assertRaises(ValueError): m.existing_owner_handoff(**a)

    def test_active_or_unknown_not_dispatchable(self):
        for state in ['active', 'notLoaded', 'unknown', '']:
            a = self.args(); a['owner_status'] = state
            with self.assertRaises(ValueError): m.existing_owner_handoff(**a)

    def test_invalid_identity_phase_or_empty_action(self):
        for key, value in [('owner_id','bad'), ('phase','monitor'), ('action','  ')]:
            a = self.args(); a[key] = value
            with self.assertRaises(ValueError): m.existing_owner_handoff(**a)

    def test_echo_is_not_execution(self):
        self.assertTrue(m.is_instruction_echo('실제 확인 요청', '실제\n확인 요청'))
        self.assertTrue(m.is_instruction_echo('실제 확인 요청', '전달 완료: 실제 확인 요청'))
        self.assertFalse(m.is_instruction_echo('', ''))
        self.assertFalse(m.is_instruction_echo('실제 확인 요청', '새 결과 없음'))
