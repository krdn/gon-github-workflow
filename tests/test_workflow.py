import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('workflow', Path(__file__).parents[1] / 'scripts/workflow.py')
w = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(w)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'source'
        (self.source / 'templates/docs').mkdir(parents=True)
        (self.source / 'templates/docs/WORKFLOW.md').write_text('repo={{REPO}} version=1')
        self.target = self.root / 'app'
        self.lock = {'schema': 1, 'sources': {'ccpm': {'sha': 'a' * 40}}}

    def test_start_and_repeat_preserves_user_state(self):
        w.apply_templates(self.target, 'owner/app', self.lock, self.source)
        state = self.target / 'docs/STATE.md'
        state.write_text('user progress')
        w.apply_templates(self.target, 'owner/app', self.lock, self.source)
        self.assertEqual(state.read_text(), 'user progress')
        self.assertIn('owner/app', (self.target / 'docs/WORKFLOW.md').read_text())

    def test_existing_unmanaged_file_blocks_all_writes(self):
        (self.target / 'docs').mkdir(parents=True)
        (self.target / 'docs/WORKFLOW.md').write_text('existing')
        with self.assertRaisesRegex(ValueError, '충돌'):
            w.apply_templates(self.target, 'owner/app', self.lock, self.source)
        self.assertFalse((self.target / '.github/workflow-state.json').exists())
        self.assertEqual((self.target / 'docs/WORKFLOW.md').read_text(), 'existing')

    def test_modified_managed_file_blocks_upgrade(self):
        w.apply_templates(self.target, 'owner/app', self.lock, self.source)
        (self.target / 'docs/WORKFLOW.md').write_text('user edit')
        (self.source / 'templates/docs/new.md').write_text('new')
        with self.assertRaisesRegex(ValueError, '충돌'):
            w.apply_templates(self.target, 'owner/app', self.lock, self.source)
        self.assertFalse((self.target / 'docs/new.md').exists())

    def test_clean_managed_file_upgrades(self):
        w.apply_templates(self.target, 'owner/app', self.lock, self.source)
        (self.source / 'templates/docs/WORKFLOW.md').write_text('version=2')
        w.apply_templates(self.target, 'owner/app', self.lock, self.source)
        self.assertEqual((self.target / 'docs/WORKFLOW.md').read_text(), 'version=2')

    def test_symlink_escape_blocks_writes(self):
        self.target.mkdir()
        outside = self.root / 'outside'
        outside.mkdir()
        (self.target / 'docs').symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, '심볼릭'):
            w.apply_templates(self.target, 'owner/app', self.lock, self.source)
        self.assertEqual(list(outside.iterdir()), [])

    def test_generated_task_template_and_user_session_records_survive_reapply(self):
        w.apply_templates(self.target, 'owner/app', self.lock, w.ROOT)
        template = self.target / 'docs/tasks/TEMPLATE.md'
        self.assertTrue(template.is_file(), 'new projects need a session task template')
        self.assertIn('https://github.com/owner/app/issues', template.read_text())
        state = self.target / 'docs/STATE.md'
        self.assertIn('현재 작업:', state.read_text())
        task = self.target / 'docs/tasks/005-ledger.md'
        task.write_text('완료: 테스트 60개. 다음: 독립 리뷰. 기존 실패를 반복하지 않음.')
        state.write_text('현재 작업: [005](tasks/005-ledger.md)')
        expected = (task.read_bytes(), state.read_bytes())
        w.apply_templates(self.target, 'owner/app', self.lock, w.ROOT)
        self.assertEqual((task.read_bytes(), state.read_bytes()), expected)
        managed = w.read_json(self.target / '.github/workflow-state.json')['files']
        self.assertNotIn('docs/tasks/005-ledger.md', managed)
        self.assertNotIn('docs/STATE.md', managed)

    def test_changed_upstream_is_reported(self):
        latest = json.loads(json.dumps(self.lock))
        latest['sources']['ccpm']['sha'] = 'b' * 40
        self.assertEqual(w.check_updates(self.lock, latest), ['ccpm'])
        self.assertEqual(w.check_updates(self.lock, self.lock), [])


class NetworkGateTests(unittest.TestCase):
    def setUp(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'templates/docs').mkdir(parents=True)
        (self.root / 'templates/docs/WORKFLOW.md').write_text('workflow')
        self.new_sha = 'a' * 40
        self.fail = False
        self.release_mode = True
        self.calls = []

        def network(*args, **kwargs):
            import base64
            command = args[0]
            endpoint = command[-1]
            self.calls.append(endpoint)
            if self.fail:
                return SimpleNamespace(returncode=1, stderr='network unavailable', stdout='')
            repo = '/'.join(endpoint.split('/')[1:3])
            if '/releases/latest' in endpoint:
                if not self.release_mode:
                    return SimpleNamespace(returncode=1, stderr='HTTP 404', stdout='')
                result = {'tag_name': 'v1', 'draft': False, 'prerelease': False}
            elif '/commits/' in endpoint:
                result = {'sha': self.new_sha}
            elif '/readme?' in endpoint:
                result = {'content': base64.b64encode(b'official docs').decode(),
                          'html_url': f'https://github.com/{repo}/blob/main/README.md'}
            else:
                result = {'full_name': repo, 'archived': False, 'default_branch': 'main'}
            return SimpleNamespace(returncode=0, stderr='', stdout=json.dumps(result))
        patcher = patch.object(w.subprocess, 'run', side_effect=network)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.lock = w.inspect_sources()
        w.write_json(self.root / 'upstreams.lock.json', self.lock)
        (self.root / 'review.md').write_text('fixture review')
        w.record_review(self.root, 'review.md', 'test fixture')

    def test_every_start_rechecks_network(self):
        target = self.root / 'app'
        w.prepare_project(self.root, target, 'owner/app')
        count = len(self.calls)
        w.prepare_project(self.root, target, 'owner/app')
        self.assertGreater(len(self.calls), count)
        self.assertEqual(w.read_json(target / '.github/start-check.json')['status'], 'upstreams_current')

    def test_update_blocks_start_without_creating_target(self):
        self.new_sha = 'b' * 40
        with self.assertRaisesRegex(ValueError, '미반영'):
            w.prepare_project(self.root, self.root / 'app', 'owner/app')
        self.assertFalse((self.root / 'app').exists())
        self.assertEqual(w.read_json(self.root / 'upstreams.lock.json'), self.lock)

    def test_unreviewed_lock_blocks_start(self):
        self.new_sha = 'b' * 40
        w.refresh(self.root, apply=True)
        with self.assertRaisesRegex(ValueError, '영향 검토'):
            w.prepare_project(self.root, self.root / 'app', 'owner/app')
        self.assertFalse((self.root / 'app').exists())

    def test_network_failure_blocks_start(self):
        self.fail = True
        with self.assertRaisesRegex(ValueError, 'network unavailable'):
            w.prepare_project(self.root, self.root / 'app', 'owner/app')
        self.assertFalse((self.root / 'app').exists())

    def test_upgrade_writes_candidate_and_is_idempotent(self):
        self.new_sha = 'b' * 40
        latest, changes = w.refresh(self.root, apply=True)
        self.assertEqual(len(changes), 5)
        self.assertEqual(w.read_json(self.root / 'upstreams.lock.json'), latest)
        report = (self.root / 'docs/upstream-update.md').read_text()
        self.assertIn('/compare/', report)
        self.assertIn('미완료', report)
        _, changes = w.refresh(self.root, apply=True)
        self.assertEqual(changes, [])
        self.assertEqual((self.root / 'docs/upstream-update.md').read_text(), report)

    def test_stable_release_and_branch_fallback(self):
        self.assertTrue(all(row['ref'] == 'v1' for row in self.lock['sources'].values()))
        self.release_mode = False
        latest = w.inspect_sources()
        self.assertTrue(all(row['ref'] == 'main' and row['mode'] == 'branch'
                            for row in latest['sources'].values()))

    def test_pending_research_cannot_pass_ready(self):
        target = self.root / 'app'
        w.prepare_project(self.root, target, 'owner/app')
        with self.assertRaisesRegex(ValueError, '미완료'):
            w.implementation_ready(target)
        context = {'checked_at': w.now(), 'objective': 'build', 'decisions': 'use stdlib',
                   'sources': [{'url': 'https://docs.python.org/3/', 'finding': 'checked'}],
                   'status': 'reviewed'}
        w.write_json(target / 'docs/start-context.json', context)
        w.implementation_ready(target)
        context['checked_at'] = '2020-01-01T00:00:00+00:00'
        w.write_json(target / 'docs/start-context.json', context)
        with self.assertRaisesRegex(ValueError, '24시간'):
            w.implementation_ready(target)

    def test_invalid_research_fields_fail_with_clear_error(self):
        target = self.root / 'app'
        w.prepare_project(self.root, target, 'owner/app')
        context = {'checked_at': w.now(), 'objective': 'build', 'decisions': 'stdlib',
                   'sources': [{'url': 'https://docs.python.org/3/', 'finding': 3}],
                   'status': 'reviewed'}
        w.write_json(target / 'docs/start-context.json', context)
        with self.assertRaisesRegex(ValueError, '출처'):
            w.implementation_ready(target)

    def test_handoff_wrong_repository_rejected_before_network(self):
        target = self.root / 'app'
        w.prepare_project(self.root, target, 'owner/app')
        count = len(self.calls)
        with self.assertRaisesRegex(ValueError, '현재 저장소'):
            w.handoff(target, 'https://github.com/other/app/issues/1')
        self.assertEqual(len(self.calls), count)


class InstallerTests(unittest.TestCase):
    def test_install_preserves_and_backs_up_existing_instructions(self):
        spec = importlib.util.spec_from_file_location('installer', Path(__file__).parents[1] / 'scripts/install.py')
        installer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(installer)
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            (home / '.codex').mkdir()
            path = home / '.codex/AGENTS.md'
            path.write_text('original instructions')
            installer.install(home, home / '.codex')
            first = path.read_text()
            installer.install(home, home / '.codex')
            self.assertEqual(path.read_text(), first)
            self.assertTrue(first.startswith('original instructions'))
            backups = list(home.glob('.local/state/gon-github-workflow/backups/*/codex-AGENTS.md'))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), 'original instructions')
            self.assertTrue((home / '.local/bin/gon-workflow').is_symlink())


class UpdatePrTests(unittest.TestCase):
    def setUp(self):
        import sys
        from unittest.mock import patch
        from types import SimpleNamespace
        sys.path.insert(0, str(Path(__file__).parents[1] / 'scripts'))
        import propose_update
        self.bot = propose_update
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'upstreams.lock.json').write_text(json.dumps({'sources': {'x': {'sha': 'abc', 'readme_commit': 'doc1'}}}))
        self.calls = []
        self.remote = False
        self.opened = []
        self.remote_content = (self.root / 'upstreams.lock.json').read_bytes()
        import os
        old = Path.cwd()
        self.addCleanup(os.chdir, old)
        env = patch.dict(os.environ, {'GH_REPO': 'owner/repo'})
        env.start()
        self.addCleanup(env.stop)

        def process(command, **kwargs):
            import base64
            self.calls.append(command)
            out = ''
            if command[:3] == ('git', 'diff', '--name-only'):
                out = 'upstreams.lock.json'
            elif command[:3] == ('gh', 'pr', 'list'):
                out = json.dumps(self.opened if '--head' not in command else [])
            elif command[:2] == ('git', 'ls-remote'):
                out = 'abc refs/heads/candidate' if self.remote else ''
            elif command[:2] == ('gh', 'api'):
                out = base64.b64encode(self.remote_content).decode()
            return SimpleNamespace(returncode=0, stdout=out, stderr='')
        patcher = patch.object(self.bot.run.__globals__['subprocess'], 'run', side_effect=process)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_orphan_branch_resumes_pr_without_second_push(self):
        self.remote = True
        self.bot.propose(self.root)
        self.assertTrue(any(c[:3] == ('gh', 'pr', 'create') for c in self.calls))
        self.assertFalse(any(c[:2] == ('git', 'push') for c in self.calls))

    def test_unrelated_document_commit_reuses_candidate_branch(self):
        self.remote = True
        self.remote_content = json.dumps({'sources': {'x': {'sha': 'abc', 'readme_commit': 'doc0'}}}).encode()
        self.bot.propose(self.root)
        self.assertTrue(any(c[:3] == ('gh', 'pr', 'create') for c in self.calls))
        self.assertFalse(any(c[:2] == ('git', 'push') for c in self.calls))

    def test_existing_candidate_prevents_multiple_prs(self):
        self.opened = [{'headRefName': 'chore/upstream-old', 'url': 'https://github.com/o/r/pull/1'}]
        self.bot.propose(self.root)
        self.assertFalse(any(c[:3] == ('gh', 'pr', 'create') for c in self.calls))
        self.assertFalse(any(c[:2] == ('git', 'push') for c in self.calls))

    def test_orphan_branch_with_wrong_content_is_rejected(self):
        self.remote = True
        self.remote_content = b'{"sources": {}}'
        with self.assertRaisesRegex(ValueError, '내용이 다릅니다'):
            self.bot.propose(self.root)
        self.assertFalse(any(c[:3] == ('gh', 'pr', 'create') for c in self.calls))


if __name__ == '__main__':
    unittest.main()
