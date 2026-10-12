import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import disposable_video_qc as qc
import media_registry as registry


class DisposableQCTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.project = self.root / 'project'; self.project.mkdir()
        self.write('manifest.json', {'media_schema_version': registry.MEDIA_SCHEMA_VERSION})
        registry.init_registry(self.project)
        self.auth = self.write('auth.json', {'mode': qc.MODE, 'user_quote': 'review then remove QC copy',
            'source': 'current_explicit_user_request', 'max_concurrent_local_clips': 1})
        self.baseline = self.write('baseline.json', {})
        self.source = registry.folder(self.project, 'videos_candidates') / '_qc_temp' / 'run' / 'test.mp4'
        self.source.parent.mkdir(parents=True); self.source.write_bytes(b'fixture-video')
        self.receipt_data = {'block_id': 'A', 'path': str(self.source), 'owned_by_qc_run': True,
            'cloud_preserved': True, 'source_ui': 'exact card and source verified',
            'download_original_path': str(self.root / 'Downloads/new.mp4'),
            'download_baseline': str(self.baseline), 'bytes': self.source.stat().st_size,
            'sha256': registry.sha256(self.source)}
        self.receipt = self.write('receipt.json', self.receipt_data)
        self.env = patch.dict(os.environ, VIDEO_TEAM_TRASH_ROOT=str(self.root/'Trash'))
        self.env.start(); self.addCleanup(self.env.stop)

    def write(self, name, data):
        path = self.project / name; path.write_text(json.dumps(data)); return path

    def register(self):
        return qc.register(self.project, self.receipt, self.auth)

    def report(self, asset):
        return self.write('qc.json', {'disposable_copy_review': {
            'asset_id': asset['asset_id'], 'source_sha256': asset['sha256'],
            'review_complete_for_declared_scope': True, 'disposal_approved': True,
            'method': 'sampled_frames', 'findings': ['background fails medium lock'],
            'unverified_checks': ['full playback', 'audio'], 'cloud_preserved': True}})

    def test_dry_run_then_trash_and_idempotent(self):
        user_file = self.root / 'personal.mp4'; user_file.write_bytes(b'keep')
        asset = self.register(); report = self.report(asset)
        self.assertFalse(self.source.exists())
        self.assertEqual(qc.cleanup(self.project, asset['asset_id'], report)['state'], 'DRY_RUN')
        self.assertTrue(Path(asset['current_path']).exists())
        result = qc.cleanup(self.project, asset['asset_id'], report, True)
        self.assertEqual(result['state'], 'TRASHED')
        self.assertEqual(registry.sha256(Path(result['event']['trashed_path'])), asset['sha256'])
        self.assertFalse(result['disk_space_freed'])
        self.assertEqual(qc.cleanup(self.project, asset['asset_id'], report, True)['state'], 'ALREADY_TRASHED')
        self.assertEqual(user_file.read_bytes(), b'keep')

    def test_old_download_not_adopted(self):
        self.write('baseline.json', {self.receipt_data['download_original_path']: {'bytes': 1}})
        with self.assertRaisesRegex(ValueError, 'PREEXISTING'):
            self.register()

    def test_changed_file_rejected(self):
        asset = self.register(); report = self.report(asset)
        Path(asset['current_path']).write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'OWNED_FILE_CHANGED'):
            qc.cleanup(self.project, asset['asset_id'], report, True)

    def test_incomplete_report_rejected(self):
        asset = self.register(); report = self.write('qc.json', {})
        with self.assertRaisesRegex(ValueError, 'SOURCE_BOUND'):
            qc.cleanup(self.project, asset['asset_id'], report, True)

    def test_authorization_change_rejected(self):
        asset = self.register(); report = self.report(asset)
        data = json.loads(self.auth.read_text()); data['user_quote'] = 'changed'
        self.auth.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'AUTHORIZATION_CHANGED'):
            qc.cleanup(self.project, asset['asset_id'], report, True)

    def test_second_owned_copy_rejected(self):
        self.register()
        self.source.write_bytes(b'fixture-video')
        with self.assertRaisesRegex(ValueError, 'ONE_PENDING'):
            self.register()

    def test_nonvideo_rejected(self):
        other = self.source.with_suffix('.png'); self.source.rename(other)
        self.receipt_data['path'] = str(other); self.write('receipt.json', self.receipt_data)
        with self.assertRaisesRegex(ValueError, 'VIDEO_ONLY'):
            self.register()

    def test_link_and_outside_rejected(self):
        linked = self.source.with_name('symlink.mp4'); linked.symlink_to(self.source)
        with self.assertRaisesRegex(ValueError, 'SYMLINK'):
            qc.checked_file(self.project, linked)
        hard = self.source.with_name('hard.mp4'); os.link(self.source, hard)
        with self.assertRaisesRegex(ValueError, 'SINGLE_LINK'):
            qc.checked_file(self.project, hard)
        with self.assertRaisesRegex(ValueError, 'OUTSIDE'):
            qc.checked_file(self.project, self.root/'personal.mp4')

    def test_approved_asset_is_protected(self):
        asset = self.register(); report = self.report(asset)
        with registry.connect(self.project) as conn:
            conn.execute('UPDATE assets SET state=? WHERE asset_id=?', ('approved', asset['asset_id']))
        with self.assertRaisesRegex(ValueError, 'PROTECTED'):
            qc.cleanup(self.project, asset['asset_id'], report, True)

    def test_receipt_tamper_rejected(self):
        asset = self.register(); report = self.report(asset)
        self.write('receipt.json', {})
        with self.assertRaisesRegex(ValueError, 'RECEIPT_CHANGED'):
            qc.cleanup(self.project, asset['asset_id'], report, True)

    def permission(self):
        return self.write('permanent.json', {'mode': 'PERMANENT_QC_COPY_DELETE',
            'source': 'current_explicit_user_request', 'user_quote': 'delete QC copy from Trash too',
            'permanent_delete': True, 'scope': 'manifest_owned_qc_copies_only',
            'project': str(self.project)})

    def trashed(self):
        asset = self.register(); report = self.report(asset)
        event = qc.cleanup(self.project, asset['asset_id'], report, True)
        return asset, report, Path(event['event']['trashed_path'])

    def test_permanent_dry_run_then_exact_delete_idempotent(self):
        asset, report, target = self.trashed(); permission = self.permission()
        other = target.parent/'user-saved.mp4'; other.write_bytes(b'keep')
        self.assertEqual(qc.purge(self.project, asset['asset_id'], report, permission)['state'], 'PURGE_DRY_RUN')
        self.assertTrue(target.exists())
        result = qc.purge(self.project, asset['asset_id'], report, permission, True)
        self.assertEqual(result['state'], 'PERMANENTLY_DELETED'); self.assertFalse(target.exists())
        self.assertEqual(other.read_bytes(), b'keep')
        self.assertEqual(qc.purge(self.project, asset['asset_id'], report, permission, True)['state'], 'ALREADY_DELETED')

    def test_cleanup_chains_permanent_only_with_permission(self):
        asset = self.register(); report = self.report(asset); permission = self.permission()
        self.assertEqual(qc.cleanup(self.project, asset['asset_id'], report, permanent_authorization=permission)['state'], 'DRY_RUN')
        result = qc.cleanup(self.project, asset['asset_id'], report, True, permission)
        self.assertEqual(result['state'], 'PERMANENTLY_DELETED')

    def test_wrong_project_permission_rejected(self):
        asset, report, target = self.trashed(); permission = self.permission()
        data = json.loads(permission.read_text()); data['project'] = '/unrelated'
        permission.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'PERMANENT_QC_PERMISSION'):
            qc.purge(self.project, asset['asset_id'], report, permission, True)
        self.assertTrue(target.exists())

    def test_changed_trashed_copy_not_deleted(self):
        asset, report, target = self.trashed(); target.write_bytes(b'other-file')
        with self.assertRaisesRegex(ValueError, 'TRASH_COPY_CHANGED'):
            qc.purge(self.project, asset['asset_id'], report, self.permission(), True)
        self.assertTrue(target.exists())

    def test_unexplained_missing_not_claimed_deleted(self):
        asset, report, target = self.trashed(); target.unlink()
        with self.assertRaisesRegex(ValueError, 'MISSING_WITHOUT'):
            qc.purge(self.project, asset['asset_id'], report, self.permission(), True)

    def test_same_path_new_file_after_purge_is_never_deleted(self):
        asset, report, target = self.trashed(); permission = self.permission()
        qc.purge(self.project, asset['asset_id'], report, permission, True)
        target.write_bytes(b'new-user-file')
        with self.assertRaisesRegex(ValueError, 'REAPPEARED'):
            qc.purge(self.project, asset['asset_id'], report, permission, True)
        self.assertTrue(target.exists())

    def test_crash_after_unlink_reconciles_saved_intent(self):
        asset, report, target = self.trashed(); permission = self.permission()
        unlink = Path.unlink
        def crash(path, *args, **kwargs):
            unlink(path, *args, **kwargs)
            raise OSError('simulated interruption after unlink')
        with patch.object(Path, 'unlink', crash), self.assertRaises(OSError):
            qc.purge(self.project, asset['asset_id'], report, permission, True)
        result = qc.purge(self.project, asset['asset_id'], report, permission, True)
        self.assertTrue(result['recovered_saved_intent_absence'])

    def test_trashed_symlink_or_hardlink_rejected(self):
        asset, report, target = self.trashed(); permission = self.permission()
        other = self.root/'other.mp4'; other.write_bytes(target.read_bytes())
        target.unlink(); target.symlink_to(other)
        with self.assertRaisesRegex(ValueError, 'SYMLINK'):
            qc.purge(self.project, asset['asset_id'], report, permission, True)
        target.unlink(); os.link(other, target)
        with self.assertRaisesRegex(ValueError, 'SINGLE_LINK'):
            qc.purge(self.project, asset['asset_id'], report, permission, True)
        self.assertTrue(other.exists())


if __name__ == '__main__':
    unittest.main()
