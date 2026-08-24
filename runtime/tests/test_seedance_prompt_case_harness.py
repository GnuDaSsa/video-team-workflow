from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest


SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))

import seedance_prompt_case_harness as harness  # noqa: E402
import prompt_packet_utils  # noqa: E402


class SeedancePromptCaseHarnessTests(unittest.TestCase):
    def base_pack(self) -> dict:
        return {
            'duration_sec': 12,
            'shot_grammar': 'SINGLE_CONTINUOUS_SHOT',
            'prompt': (
                '@Image1의 여성 검객 얼굴, 머리, 검은 갓, 검은 도포와 검을 '
                '정체성 기준으로 사용하고 시트 배경과 레이아웃은 가져오지 않는다. '
                '12초 단일 원테이크에서 카메라는 후방 오른쪽을 유지한다.'
            ),
            'reference_role_map': [
                {'reference': '@Image1', 'role': 'CHAR_SWORDSWOMAN identity'},
            ],
            'prompt_rules_used': [],
            'semantic_contract': {},
        }

    def add_reference_cast_contract(self, pack: dict) -> None:
        pack['prompt_rules_used'].append(harness.REFERENCE_CAST_LEDGER_RULE)
        pack['semantic_contract'].update({
            'visible_entity_count_total': 1,
            'entities': [{
                'entity_id': 'CHAR_SWORDSWOMAN',
                'count': 1,
                'aliases': ['여성 검객', '검객'],
                'reference_tokens': ['@Image1'],
            }],
            'reference_bindings': [{
                'token': '@Image1',
                'role': 'identity',
                'entity_id': 'CHAR_SWORDSWOMAN',
                'use': ['face', 'hair', 'hat', 'wardrobe', 'sword'],
                'exclude': ['sheet background', 'layout', 'text'],
            }],
        })

    def add_timed_one_take_effect_contract(self, pack: dict) -> None:
        pack['prompt_rules_used'].extend([
            harness.TIMED_PERFORMANCE_RULE,
            harness.ONE_TAKE_AXIS_RULE,
            harness.PHYSICAL_EFFECT_RULE,
            harness.CONSTRAINT_CONSISTENCY_RULE,
        ])
        pack['semantic_contract'].update({
            'timed_beats': [
                {'start_sec': 0, 'end_sec': 3, 'action': '직립 정지 뒤 조용히 발도',
                 'camera': '후방 오른쪽 느린 푸시인'},
                {'start_sec': 3, 'end_sec': 8, 'action': '절제된 초고속 연속 베기',
                 'camera': '후방 오른쪽 원호 추적'},
                {'start_sec': 8, 'end_sec': 10, 'action': '칼끝을 고정한 잔심',
                 'camera': '같은 축에서 천천히 풀아웃'},
                {'start_sec': 10, 'end_sec': 12, 'action': '무너지는 산을 보며 납도',
                 'camera': '후방 오른쪽 상승'},
            ],
            'continuity': {
                'take_structure': 'single_take',
                'camera_axis': {
                    'side': 'subject rear-right',
                    'subject_placement': 'left third off-center',
                    'lead_room': 'toward mountain',
                },
            },
            'effects': [{
                'effect_id': 'wind_pressure_slash',
                'cause': 'steel blade acceleration',
                'material_mechanism': 'transparent air refraction and pressure',
                'nearby_reactions': ['grass flattens radially', 'cloth and ice scatter outward'],
                'travel': 'pressure groove crosses valley snow',
                'impact': 'one varied frost seam forms per slash',
                'aftermath': 'gravity-driven split, avalanche, and ice dust',
            }],
            'constraints': {
                'required': ['wind_pressure_refraction'],
                'forbidden': ['glowing_blade', 'laser', 'explosion'],
            },
        })

    def test_corrected_single_take_action_contract_passes(self) -> None:
        pack = self.base_pack()
        self.add_reference_cast_contract(pack)
        self.add_timed_one_take_effect_contract(pack)

        self.assertEqual(harness.validate_case_contract(pack), [])

    def test_corrected_multi_character_timed_dialogue_contract_passes(self) -> None:
        pack = {
            'duration_sec': 15,
            'shot_grammar': 'PLANNED_MULTI_SHOT_SOURCE',
            'prompt': (
                '@Image1의 CHAR_GREEN, @Image2의 CHAR_WHITE, @Image3의 CHAR_BLACK이 '
                '각각 한 명씩만 존재한다. 15초 3숏 멜로드라마 패러디. '
                '0–5초 CHAR_GREEN이 @Audio1에 맞춰 "첫 메뉴"라고 말한다. '
                '5–10초 CHAR_WHITE가 @Audio2에 맞춰 "둘째 메뉴"라고 답한다. '
                '10–15초 CHAR_BLACK이 @Audio3에 맞춰 "마지막 메뉴"라고 외친 뒤 '
                '세 사람의 반응이 보이는 와이드로 끝난다.'
            ),
            'reference_role_map': [
                {'reference': '@Image1', 'role': 'CHAR_GREEN identity'},
                {'reference': '@Image2', 'role': 'CHAR_WHITE identity'},
                {'reference': '@Image3', 'role': 'CHAR_BLACK identity'},
                {'reference': '@Audio1', 'role': 'CHAR_GREEN performed line'},
                {'reference': '@Audio2', 'role': 'CHAR_WHITE performed line'},
                {'reference': '@Audio3', 'role': 'CHAR_BLACK performed line'},
            ],
            'prompt_rules_used': [
                harness.REFERENCE_CAST_LEDGER_RULE,
                harness.TIMED_PERFORMANCE_RULE,
                harness.EXACT_TEXT_DIALOGUE_RULE,
            ],
            'semantic_contract': {
                'visible_entity_count_total': 3,
                'entities': [
                    {'entity_id': 'CHAR_GREEN', 'count': 1, 'aliases': ['초록 인물'],
                     'reference_tokens': ['@Image1']},
                    {'entity_id': 'CHAR_WHITE', 'count': 1, 'aliases': ['흰옷 인물'],
                     'reference_tokens': ['@Image2']},
                    {'entity_id': 'CHAR_BLACK', 'count': 1, 'aliases': ['검은옷 인물'],
                     'reference_tokens': ['@Image3']},
                ],
                'reference_bindings': [
                    {'token': '@Image1', 'role': 'identity', 'entity_id': 'CHAR_GREEN',
                     'use': ['face', 'hair', 'wardrobe'],
                     'exclude': ['sheet background', 'layout', 'text']},
                    {'token': '@Image2', 'role': 'identity', 'entity_id': 'CHAR_WHITE',
                     'use': ['face', 'hair', 'wardrobe'],
                     'exclude': ['sheet background', 'layout', 'text']},
                    {'token': '@Image3', 'role': 'identity', 'entity_id': 'CHAR_BLACK',
                     'use': ['face', 'hair', 'wardrobe'],
                     'exclude': ['sheet background', 'layout', 'text']},
                ],
                'timed_beats': [
                    {'start_sec': 0, 'end_sec': 5, 'action': 'CHAR_GREEN의 절제된 첫 대사',
                     'camera': '오프센터 3/4 클로즈업'},
                    {'start_sec': 5, 'end_sec': 10, 'action': 'CHAR_WHITE의 낮은 응답',
                     'camera': '시선축을 지키는 역앵글'},
                    {'start_sec': 10, 'end_sec': 15, 'action': 'CHAR_BLACK의 외침과 세 사람 반응',
                     'camera': '랙 포커스 뒤 와이드 종료'},
                ],
                'dialogue': [
                    {'speaker_entity_id': 'CHAR_GREEN', 'exact_text': '첫 메뉴',
                     'language': 'ko-KR', 'delivery': '울음을 삼킨 낮은 톤',
                     'audio_reference_token': '@Audio1'},
                    {'speaker_entity_id': 'CHAR_WHITE', 'exact_text': '둘째 메뉴',
                     'language': 'ko-KR', 'delivery': '미안함을 누른 응답',
                     'audio_reference_token': '@Audio2'},
                    {'speaker_entity_id': 'CHAR_BLACK', 'exact_text': '마지막 메뉴',
                     'language': 'ko-KR', 'delivery': '절제 뒤 한 번의 외침',
                     'audio_reference_token': '@Audio3'},
                ],
                'on_screen_text': [],
            },
        }

        self.assertEqual(harness.validate_case_contract(pack), [])

    def test_rejects_mixed_template_alias_and_cast_collisions(self) -> None:
        pack = self.base_pack()
        pack['prompt'] += ' @{{Mixed 1}}과 @HARIN은 같은 인물이다.'
        pack['reference_role_map'].append({'reference': '@Image2', 'role': 'second identity'})
        self.add_reference_cast_contract(pack)
        pack['semantic_contract']['visible_entity_count_total'] = 2
        pack['semantic_contract']['entities'].append({
            'entity_id': 'CHAR_OTHER',
            'count': 1,
            'aliases': ['검객'],
            'reference_tokens': ['@Image1'],
        })

        errors = harness.validate_case_contract(pack)

        self.assertTrue(any('unresolved_mixed_template' in item for item in errors))
        self.assertIn('unresolved_reference_alias:@HARIN', errors)
        self.assertTrue(any('conflicting_entity_alias' in item for item in errors))
        self.assertTrue(any('conflicting_reference_entity' in item for item in errors))

    def test_rejects_spaced_parenthesized_reference_forms(self) -> None:
        pack = self.base_pack()
        pack['prompt'] = '@Image 1의 인물은 (Audio1)에 맞춰 노래한다.'
        pack['reference_role_map'] = [
            {'reference': '@Image 1', 'role': 'identity'},
            {'reference': '(Audio1)', 'role': 'music'},
        ]

        errors = harness.validate_case_contract(pack)

        self.assertTrue(any('invalid_reference_token' in item for item in errors))
        self.assertTrue(any('noncanonical_spaced_reference' in item for item in errors))
        self.assertTrue(any('noncanonical_parenthesized_reference' in item for item in errors))

    def test_rejects_one_take_cut_conflict_and_timeline_gap(self) -> None:
        pack = self.base_pack()
        pack['prompt'] += ' 빠른 컷 전환 템포와 하드 컷을 사용한다.'
        self.add_timed_one_take_effect_contract(pack)
        pack['semantic_contract']['timed_beats'][1]['start_sec'] = 4

        errors = harness.validate_case_contract(pack)

        self.assertTrue(any('one_take_conflicts_with_cut_direction' in item for item in errors))
        self.assertTrue(any('timed_beat_2_gap_or_overlap' in item for item in errors))

    def test_lipsync_master_audio_contract_passes(self) -> None:
        pack = self.base_pack()
        pack.update({
            'duration_sec': 15,
            'prompt': (
                '@Image1의 주인공이 @Audio1의 완성된 마스터 트랙만 들리도록 '
                '모든 음절을 정확히 립싱크한다. 다섯 댄서는 입을 움직이지 않는다.'
            ),
            'reference_role_map': [
                {'reference': '@Image1', 'role': 'lead performer identity'},
                {'reference': '@Audio1', 'role': 'exclusive finished master and lipsync'},
            ],
            'prompt_rules_used': [harness.AUDIO_LIPSYNC_RULE],
            'semantic_contract': {
                'audio_contract': {
                    'source_token': '@Audio1',
                    'exclusive_source': True,
                    'performer_entity_id': 'CHAR_LEAD',
                    'non_speaking_entity_ids': [
                        'DANCER_1', 'DANCER_2', 'DANCER_3', 'DANCER_4', 'DANCER_5'],
                    'face_visibility': 'sharp and unobstructed through every vocal syllable',
                    'lip_sync_segments': [
                        {'start_sec': 0.5, 'end_sec': 2.8, 'content': 'opening vocal'},
                        {'start_sec': 3.2, 'end_sec': 6.7, 'content': 'verse'},
                        {'start_sec': 7.5, 'end_sec': 13.7, 'content': 'hook'},
                    ],
                },
            },
        })

        self.assertEqual(harness.validate_case_contract(pack), [])

        bad = copy.deepcopy(pack)
        bad['semantic_contract']['audio_contract']['exclusive_source'] = False
        bad['semantic_contract']['audio_contract']['non_speaking_entity_ids'].append('CHAR_LEAD')
        errors = harness.validate_case_contract(bad)
        self.assertIn('audio_contract.exclusive_source_must_be_true', errors)
        self.assertIn('audio_contract.performer_cannot_be_non_speaker', errors)

    def test_exact_hangul_and_dialogue_require_literal_and_audio_guide(self) -> None:
        pack = self.base_pack()
        pack.update({
            'prompt': (
                '@Image1의 교사가 빈 칠판에 "한국어 이름"을 쓴 뒤 학생들을 보며 '
                '"반가워, 잘 부탁해."라고 정확한 한국어로 말한다. @Audio1의 발음과 '
                '호흡을 그대로 따른다.'
            ),
            'reference_role_map': [
                {'reference': '@Image1', 'role': 'teacher identity'},
                {'reference': '@Audio1', 'role': 'performed Korean dialogue guide'},
            ],
            'prompt_rules_used': [harness.EXACT_TEXT_DIALOGUE_RULE],
            'semantic_contract': {
                'dialogue': [{
                    'speaker_entity_id': 'CHAR_TEACHER',
                    'exact_text': '반가워, 잘 부탁해.',
                    'language': 'ko-KR',
                    'delivery': 'calm smile after finishing the writing',
                    'audio_reference_token': '@Audio1',
                }],
                'on_screen_text': [{
                    'exact_text': '한국어 이름',
                    'language': 'ko-KR',
                    'appearance_action': 'written one stroke at a time with chalk',
                    'qc_route': 'downloaded-frame text legibility and spelling inspection',
                }],
            },
        })

        self.assertEqual(harness.validate_case_contract(pack), [])

        bad = copy.deepcopy(pack)
        del bad['semantic_contract']['dialogue'][0]['audio_reference_token']
        bad['semantic_contract']['on_screen_text'][0]['exact_text'] = '다른 글자'
        errors = harness.validate_case_contract(bad)
        self.assertIn('dialogue_1_performed_audio_reference_required', errors)
        self.assertIn('on_screen_text_1_literal_missing_from_prompt', errors)

    def test_rejects_required_forbidden_and_flare_contradictions(self) -> None:
        pack = self.base_pack()
        pack['prompt_rules_used'] = [harness.CONSTRAINT_CONSISTENCY_RULE]
        pack['prompt'] += ' No lens flares. 마지막에는 sun flare held.'
        pack['semantic_contract'] = {
            'constraints': {
                'required': ['lens_flare', 'warm_sun'],
                'forbidden': ['lens_flare', 'neon'],
            },
        }

        errors = harness.validate_case_contract(pack)

        self.assertIn('constraint_required_and_forbidden:lens_flare', errors)
        self.assertIn('prompt_requires_and_forbids_lens_flare', errors)

    def test_existing_prompt_attestation_validator_runs_semantic_harness(self) -> None:
        pack = self.base_pack()
        pack['prompt'] += ' @HARIN은 아직 변환되지 않은 별칭이다.'

        errors = prompt_packet_utils.validate_seedance(pack)

        self.assertIn('unresolved_reference_alias:@HARIN', errors)


if __name__ == '__main__':
    unittest.main()
