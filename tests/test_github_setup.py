import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / 'scripts'))
import github_setup as setup
import workflow as w


class GitHubSetupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir='/tmp')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.target = self.root / 'app'
        self.bare = self.root / 'remote.git'
        self.real_run = subprocess.run
        self.real_run(['git', 'init', '--bare', str(self.bare)], check=True, capture_output=True)
        config = self.root / 'gitconfig'
        config.write_text(f'[url "{self.bare}"]\n    insteadOf = https://github.com/owner/app.git\n')
        env = patch.dict(os.environ, {
            'GIT_CONFIG_GLOBAL': str(config), 'GIT_CONFIG_NOSYSTEM': '1',
            'GIT_AUTHOR_NAME': 'Test', 'GIT_AUTHOR_EMAIL': 'test@example.invalid',
            'GIT_COMMITTER_NAME': 'Test', 'GIT_COMMITTER_EMAIL': 'test@example.invalid',
        })
        env.start()
        self.addCleanup(env.stop)
        self.metadata = None
        self.milestones = []
        self.labels = []
        self.issues = []
        self.projects = []
        self.items = []
        self.calls = []
        self.fail_project = False
        self.fail_pr = False
        self.prs = []
        self.upstreams = {}
        self.issue_url = 'https://github.com/owner/app/issues/1'
        self.metadata_template = {'full_name': 'owner/app', 'archived': False,
                                  'clone_url': 'https://github.com/owner/app.git',
                                  'ssh_url': 'git@github.com:owner/app.git',
                                  'html_url': 'https://github.com/owner/app',
                                  'default_branch': 'main', 'has_issues': True,
                                  'has_discussions': False, 'private': True}
        intercept = patch.object(subprocess, 'run', side_effect=self.process)
        intercept.start()
        self.addCleanup(intercept.stop)

    def process(self, args, **kwargs):
        args = list(args)
        if args[0] != 'gh':
            return self.real_run(args, **kwargs)
        self.calls.append(args)
        result = None
        if args[1] == 'api':
            method = args[args.index('--method') + 1]
            endpoint = args[args.index('--method') + 2]
            payload = json.loads(kwargs.get('input') or '{}')
            upstream = next((row for row in self.upstreams.values()
                             if endpoint.startswith('repos/' + row['repo'])), None)
            if upstream:
                if '/releases/latest' in endpoint:
                    if upstream['mode'] == 'branch':
                        return SimpleNamespace(returncode=1, stdout='', stderr='HTTP 404')
                    result = {'tag_name': upstream['ref']}
                elif '/commits/' in endpoint:
                    result = {'sha': upstream['sha']}
                elif '/readme?' in endpoint:
                    result = {'content': base64.b64encode(b'test upstream').decode(), 'html_url': 'https://example.invalid/README'}
                else:
                    result = {'full_name': upstream['repo'], 'archived': False, 'default_branch': 'main'}
            elif endpoint == 'repos/owner/app':
                if self.metadata is None:
                    return SimpleNamespace(returncode=1, stdout='', stderr='HTTP 404')
                if method == 'PATCH': self.metadata.update(payload)
                result = self.metadata
            else:
                resource = endpoint.split('/')[3].split('?')[0]
                target = {'milestones': self.milestones, 'labels': self.labels, 'issues': self.issues}[resource]
                if method == 'GET':
                    result = target
                else:
                    result = dict(payload, number=len(target) + 1)
                    if resource == 'issues': result['html_url'] = self.issue_url
                    target.append(result)
        elif args[1:3] == ['repo', 'create']:
            self.metadata = dict(self.metadata_template)
            result = None
        elif args[1:4] == ['config', 'get', 'git_protocol']:
            return SimpleNamespace(returncode=0, stdout='https', stderr='')
        elif args[1:3] == ['project', 'list']:
            result = {'projects': self.projects, 'totalCount': len(self.projects)}
        elif args[1:3] == ['project', 'create']:
            if self.fail_project:
                return SimpleNamespace(returncode=1, stdout='', stderr='network interrupted')
            result = {'number': 1, 'title': 'ggw-app', 'closed': False,
                      'url': 'https://github.com/users/owner/projects/1'}
            self.projects.append(result)
        elif args[1:3] == ['project', 'item-list']:
            result = {'items': self.items, 'totalCount': len(self.items)}
        elif args[1:3] == ['project', 'item-add']:
            self.items.append({'content': {'url': args[args.index('--url') + 1]}})
        elif args[1:3] == ['project', 'link']:
            pass
        elif args[1:3] == ['issue', 'view']:
            result = {'url': args[3], 'milestone': {'title': '첫 AI 작업', 'number': 1}}
        elif args[1:3] == ['pr', 'list']:
            result = self.prs
        elif args[1:3] == ['pr', 'create']:
            if self.fail_pr:
                return SimpleNamespace(returncode=1, stdout='', stderr='PR network interrupted')
            self.prs.append({'url': 'https://github.com/owner/app/pull/2', 'state': 'OPEN'})
            return SimpleNamespace(returncode=0, stdout=self.prs[0]['url'], stderr='')
        else:
            raise AssertionError(args)
        return SimpleNamespace(returncode=0, stdout=json.dumps(result) if result is not None else '', stderr='')

    def prepare(self):
        metadata = setup.preflight(self.target, 'owner/app')
        lock = w.read_json(w.ROOT / 'upstreams.lock.json')
        w.apply_templates(self.target, 'owner/app', lock)
        gate = self.target / '.github/start-check.json'
        if not gate.exists(): w.write_json(gate, {'status': 'upstreams_current', 'checked_at': w.now()})
        return metadata

    def test_real_git_initial_commit_push_and_idempotent_reuse(self):
        metadata = self.prepare()
        (self.target / '.env').write_text('SECRET=do-not-commit')
        (self.target / 'unrelated.txt').write_text('user file')
        setup.configure(self.target, 'owner/app', 'private', metadata)
        first = setup.git(self.target, 'rev-parse', 'HEAD')
        tracked = setup.git(self.target, 'ls-files').splitlines()
        self.assertIn('README.md', tracked)
        self.assertNotIn('.env', tracked)
        self.assertNotIn('unrelated.txt', tracked)
        self.assertEqual(w.read_json(self.target / 'docs/start-context.json')['status'], 'pending_research')
        metadata = self.prepare()
        setup.configure(self.target, 'owner/app', 'public', metadata)
        self.assertTrue(self.metadata['private'])
        self.assertEqual(setup.git(self.target, 'rev-parse', 'HEAD'), first)
        self.assertEqual([len(self.issues), len(self.milestones), len(self.projects), len(self.items)], [1, 1, 1, 1])
        setup.verify(self.target)

    def test_failed_project_creation_resumes_without_duplicate_issue(self):
        metadata = self.prepare()
        self.fail_project = True
        with self.assertRaisesRegex(ValueError, 'network interrupted'):
            setup.configure(self.target, 'owner/app', 'private', metadata)
        self.fail_project = False
        metadata = self.prepare()
        setup.configure(self.target, 'owner/app', 'private', metadata)
        self.assertEqual(len(self.issues), 1)
        self.assertEqual(len(self.milestones), 1)
        self.assertEqual(len(self.projects), 1)

    def test_wrong_origin_rejected_before_files_or_remote_mutation(self):
        self.target.mkdir()
        setup.git(self.target, 'init', '-b', 'main')
        setup.git(self.target, 'remote', 'add', 'origin', 'https://github.com/other/repo.git')
        with self.assertRaisesRegex(ValueError, 'origin'):
            setup.preflight(self.target, 'owner/app')
        self.assertEqual(self.calls, [])
        self.assertFalse((self.target / 'AGENTS.md').exists())

    def test_parent_repository_is_not_accidentally_committed(self):
        setup.git(self.root, 'init', '-b', 'main')
        with self.assertRaisesRegex(ValueError, '다른 Git 저장소'):
            setup.preflight(self.target, 'owner/app')
        self.assertEqual(self.calls, [])

    def test_empty_git_directory_in_parent_is_not_a_repository(self):
        (self.root / '.git').mkdir()
        self.assertIsNone(setup.preflight(self.target, 'owner/app'))

    def test_staged_user_change_is_preserved_and_blocks_setup(self):
        self.target.mkdir()
        setup.git(self.target, 'init', '-b', 'main')
        (self.target / 'private.txt').write_text('user data')
        setup.git(self.target, 'add', 'private.txt')
        with self.assertRaisesRegex(ValueError, '기존 Git 변경'):
            setup.preflight(self.target, 'owner/app')
        self.assertEqual(setup.git(self.target, 'diff', '--cached', '--name-only'), 'private.txt')
        self.assertEqual(self.calls, [])

    def test_configuration_ready_does_not_require_ai_research(self):
        with self.assertRaisesRegex(ValueError, 'GitHub 구성이 미완료'):
            setup.verify(self.target)
        metadata = self.prepare()
        setup.configure(self.target, 'owner/app', 'private', metadata)
        setup.verify(self.target)
        self.assertEqual(w.read_json(self.target / 'docs/start-context.json')['objective'], '')

    def test_new_repository_uses_github_default_branch(self):
        self.metadata_template['default_branch'] = 'trunk'
        metadata = self.prepare()
        setup.configure(self.target, 'owner/app', 'private', metadata)
        self.assertEqual(setup.git(self.target, 'branch', '--show-current'), 'trunk')
        self.prepare()

    def test_existing_repository_update_pr_resumes_and_is_reused(self):
        metadata = self.prepare()
        setup.configure(self.target, 'owner/app', 'private', metadata)
        main = setup.git(self.target, 'rev-parse', 'HEAD')
        (self.target / 'AGENTS.md').write_text('updated workflow')
        self.fail_pr = True
        with self.assertRaisesRegex(ValueError, 'PR network interrupted'):
            setup.publish(self.target, 'owner/app', 'main')
        branch = setup.git(self.target, 'branch', '--show-current')
        self.assertTrue(branch.startswith('chore/ggw-setup-'))
        self.fail_pr = False
        for _ in range(2):
            with self.assertRaisesRegex(ValueError, '구성 변경 PR'):
                setup.preflight(self.target, 'owner/app')
        self.assertEqual(len(self.prs), 1)
        self.assertEqual(setup.git(self.target, 'rev-parse', 'main'), main)
        self.assertEqual(setup.git(self.target, 'status', '--porcelain'), '')
        self.prs[0]['state'] = 'MERGED'
        setup.git(self.target, 'merge', '--ff-only', branch)
        setup.git(self.target, 'push', 'origin', 'main')
        setup.git(self.target, 'branch', '-d', branch)
        setup.preflight(self.target, 'owner/app')

    def test_existing_local_feature_branch_is_not_pushed_to_new_default(self):
        self.target.mkdir()
        setup.git(self.target, 'init', '-b', 'feature-x')
        setup.git(self.target, 'commit', '--allow-empty', '-m', 'user work')
        before = setup.git(self.target, 'rev-parse', 'HEAD')
        metadata = self.prepare()
        with self.assertRaisesRegex(ValueError, '기본 브랜치'):
            setup.configure(self.target, 'owner/app', 'private', metadata)
        self.assertEqual(setup.git(self.target, 'rev-parse', 'HEAD'), before)
        self.assertEqual(setup.git(self.target, 'ls-remote', '--heads', 'origin'), '')

    def test_existing_untracked_personal_notes_are_not_published(self):
        (self.target / 'docs').mkdir(parents=True)
        (self.target / 'docs/STATE.md').write_text('personal notes')
        (self.target / 'docs/start-context.json').write_text('{"private":"user draft"}')
        metadata = self.prepare()
        setup.configure(self.target, 'owner/app', 'private', metadata)
        tracked = setup.git(self.target, 'ls-files').splitlines()
        self.assertNotIn('docs/STATE.md', tracked)
        self.assertNotIn('docs/start-context.json', tracked)
        self.assertEqual((self.target / 'docs/STATE.md').read_text(), 'personal notes')

    def test_existing_dependabot_configuration_is_preserved(self):
        (self.target / '.github').mkdir(parents=True)
        existing = 'version: 2\nupdates: []\n'
        (self.target / '.github/dependabot.yml').write_text(existing)
        metadata = self.prepare()
        setup.configure(self.target, 'owner/app', 'private', metadata)
        self.assertEqual((self.target / '.github/dependabot.yml').read_text(), existing)
        self.assertNotIn('.github/dependabot.yml', setup.git(self.target, 'ls-files').splitlines())

    def test_canonical_repository_case_does_not_break_configuration_verification(self):
        self.metadata_template['full_name'] = 'Owner/App'
        self.metadata_template['html_url'] = 'https://github.com/Owner/App'
        self.issue_url = 'https://github.com/Owner/App/issues/1'
        metadata = self.prepare()
        setup.configure(self.target, 'owner/app', 'private', metadata)
        setup.verify(self.target)

    def test_initial_commit_hook_failure_unstages_and_resumes(self):
        metadata = self.prepare()
        setup.git(self.target, 'init', '-b', 'main')
        hook = self.target / '.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\nexit 1\n')
        hook.chmod(0o755)
        with self.assertRaises(ValueError):
            setup.configure(self.target, 'owner/app', 'private', metadata)
        self.assertEqual(setup.git(self.target, 'diff', '--cached', '--name-only'), '')
        hook.write_text('#!/bin/sh\nexit 0\n')
        metadata = self.prepare()
        setup.configure(self.target, 'owner/app', 'private', metadata)

    def test_update_commit_failure_restores_branch_and_resumes_exact_files(self):
        metadata = self.prepare()
        setup.configure(self.target, 'owner/app', 'private', metadata)
        (self.target / 'AGENTS.md').write_text('updated configuration')
        hook = self.target / '.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\nexit 1\n')
        hook.chmod(0o755)
        with self.assertRaises(ValueError):
            setup.publish(self.target, 'owner/app', 'main')
        self.assertEqual(setup.git(self.target, 'diff', '--cached', '--name-only'), '')
        self.assertEqual(setup.git(self.target, 'branch', '--show-current'), 'main')
        hook.write_text('#!/bin/sh\nexit 0\n')
        setup.preflight(self.target, 'owner/app')
        with self.assertRaisesRegex(ValueError, '구성 변경 PR'):
            setup.publish(self.target, 'owner/app', 'main')

    def test_start_runs_upstream_gate_and_complete_setup_twice(self):
        standard = self.root / 'standard'
        shutil.copytree(w.ROOT / 'templates', standard / 'templates')
        lock = w.read_json(w.ROOT / 'upstreams.lock.json')
        for row in lock['sources'].values():
            row['readme_sha256'] = w.digest(b'test upstream')
        self.upstreams = lock['sources']
        w.write_json(standard / 'upstreams.lock.json', lock)
        (standard / 'review.md').write_text('test fixture review')
        w.write_json(standard / 'upstream-review.json', {
            'lock_sha256': w.lock_hash(lock), 'notes': 'review.md',
            'notes_sha256': w.digest(b'test fixture review'), 'reviewer': 'test fixture',
        })
        w.start(standard, self.target, 'owner/app')
        head = setup.git(self.target, 'rev-parse', 'HEAD')
        w.start(standard, self.target, 'owner/app')
        w.ready(self.target)
        self.assertEqual(setup.git(self.target, 'rev-parse', 'HEAD'), head)
        self.assertEqual(len(self.issues), 1)


if __name__ == '__main__':
    unittest.main()
