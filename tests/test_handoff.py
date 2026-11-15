import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import parse_qs, quote, unquote, urlparse

sys.path.insert(0, str(Path(__file__).parents[1] / 'scripts'))
import workflow as w


class HandoffTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.target = self.root / 'app'
        self.bare = self.root / 'remote.git'
        self.real_run = subprocess.run
        config = self.root / 'gitconfig'
        config.write_text(f'[url "{self.bare}"]\n    insteadOf = https://github.com/owner/app.git\n')
        environment = patch.dict(os.environ, {
            'GIT_CONFIG_GLOBAL': str(config), 'GIT_CONFIG_NOSYSTEM': '1',
            'GIT_AUTHOR_NAME': 'Test', 'GIT_AUTHOR_EMAIL': 'test@example.invalid',
            'GIT_COMMITTER_NAME': 'Test', 'GIT_COMMITTER_EMAIL': 'test@example.invalid',
        })
        environment.start()
        self.addCleanup(environment.stop)
        self.real_run(['git', 'init', '--bare', str(self.bare)], check=True, capture_output=True)
        self.real_run(['git', 'init', '-b', 'task/next', str(self.target)],
                      check=True, capture_output=True)
        (self.target / '.github').mkdir()
        (self.target / '.github/workflow-state.json').write_text('{"repo":"owner/app"}')
        (self.target / 'docs/tasks').mkdir(parents=True)
        self.state = self.target / 'docs/STATE.md'
        self.state.write_text('# 현재 작업\n\n[작업](tasks/5-한 작업.md)\n')
        self.task = 'docs/tasks/5-한 작업.md'
        (self.target / self.task).write_text('# 작업 5\n\n- 다음 행동: 피드백 확인\n')
        self.git('add', '.')
        self.git('commit', '-m', 'baseline')
        self.git('remote', 'add', 'origin', 'https://github.com/owner/app.git')
        self.git('push', '-u', 'origin', 'task/next')
        self.head = self.git('rev-parse', 'HEAD')
        self.issue = 'https://github.com/owner/app/issues/5'
        self.comments = []
        self.calls = []
        self.corrupt = None
        self.fail_read = False
        self.fail_post_after_write = False
        self.remote_file_mismatch = False
        self.remote_branch_mismatch = False
        intercept = patch.object(subprocess, 'run', side_effect=self.process)
        intercept.start()
        self.addCleanup(intercept.stop)

    def git(self, *args):
        return self.real_run(['git', '-C', str(self.target), *args],
                             check=True, text=True, capture_output=True).stdout.strip()

    def comment(self, body):
        number = 10 + len(self.comments)
        row = {'id': number, 'body': body, 'html_url': self.issue + f'#issuecomment-{number}',
               'issue_url': 'https://api.github.com/repos/owner/app/issues/5'}
        self.comments.append(row)
        return row

    def process(self, args, **kwargs):
        args = list(args)
        if args[0] != 'gh':
            return self.real_run(args, **kwargs)
        self.calls.append(args)
        if args[1:3] == ['issue', 'view']:
            result = {'url': self.issue}
        elif args[1:3] == ['issue', 'comment']:
            row = self.comment(Path(args[args.index('--body-file') + 1]).read_text())
            return SimpleNamespace(returncode=0, stdout=row['html_url'], stderr='')
        elif args[1] == 'api':
            method = args[args.index('--method') + 1]
            endpoint = args[args.index('--method') + 2]
            if endpoint == 'repos/owner/app/issues/5':
                result = {'html_url': self.issue}
            elif '/git/ref/heads/' in endpoint:
                result = {'object': {'sha': ('0' * 40 if self.remote_branch_mismatch
                                            else self.git('rev-parse', 'HEAD'))}}
            elif '/contents/' in endpoint:
                relative = unquote(endpoint.split('/contents/', 1)[1].split('?', 1)[0])
                result = {'type': 'file', 'sha': ('0' * 40 if self.remote_file_mismatch
                                                else self.git('rev-parse', f'HEAD:{relative}'))}
            elif '/issues/comments/' in endpoint:
                if self.fail_read:
                    return SimpleNamespace(returncode=1, stdout='', stderr='HTTP 503')
                number = int(endpoint.rsplit('/', 1)[1])
                result = dict(next(row for row in self.comments if row['id'] == number))
                if self.corrupt:
                    result[self.corrupt] = 'unexpected'
            elif endpoint.startswith('repos/owner/app/issues/5/comments'):
                if method == 'POST':
                    result = self.comment(json.loads(kwargs['input'])['body'])
                    if self.fail_post_after_write:
                        return SimpleNamespace(returncode=1, stdout='', stderr='HTTP 503')
                else:
                    page = int(parse_qs(urlparse(endpoint).query).get('page', ['1'])[0])
                    result = self.comments[(page - 1) * 100:page * 100]
            else:
                raise AssertionError(args)
        else:
            raise AssertionError(args)
        return SimpleNamespace(returncode=0, stdout=json.dumps(result), stderr='')

    def invoke(self, **kwargs):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            w.handoff(self.target, self.issue, **kwargs)
        return output.getvalue()

    def test_dirty_snapshot_is_rejected_without_posting(self):
        self.state.write_text('아직 커밋하지 않은 작업')
        with self.assertRaises(ValueError):
            self.invoke()
        self.assertEqual(self.comments, [])

    def test_unpushed_commit_is_rejected_without_posting(self):
        self.state.write_text('새 작업')
        self.git('add', '.')
        self.git('commit', '-m', 'not pushed')
        with self.assertRaises(ValueError):
            self.invoke()
        self.assertEqual(self.comments, [])

    def test_pinned_state_link_replaces_relative_body_copy(self):
        output = self.invoke()
        body = self.comments[0]['body']
        self.assertIn(f'/blob/{self.head}/docs/STATE.md', body)
        self.assertNotIn('[작업](tasks/', body)
        self.assertIn('새 세션', output)
        self.assertIn('미실행', output)

    def test_comment_readback_mismatch_never_reports_success(self):
        for field in ['body', 'issue_url', 'html_url']:
            with self.subTest(field=field):
                self.corrupt = field
                with self.assertRaises(ValueError):
                    self.invoke()

    def test_same_handoff_reuses_comment(self):
        first = self.invoke()
        second = self.invoke()
        self.assertEqual(len(self.comments), 1)
        self.assertIn(self.comments[0]['html_url'], first)
        self.assertIn(self.comments[0]['html_url'], second)

    def test_unknown_comment_readback_is_not_success_and_retry_reuses_it(self):
        self.fail_read = True
        with self.assertRaises(ValueError):
            self.invoke()
        self.assertEqual(len(self.comments), 1)
        self.fail_read = False
        self.invoke()
        self.assertEqual(len(self.comments), 1)

    def test_selected_task_uses_encoded_pinned_link(self):
        self.invoke(task=self.task)
        body = self.comments[0]['body']
        self.assertIn(f'/blob/{self.head}/' + quote(self.task, safe='/'), body)
        self.assertIn(self.task, body)

    def test_dry_run_cli_checks_remote_without_posting(self):
        output = io.StringIO()
        with patch.object(sys, 'argv', ['workflow.py', 'handoff', str(self.target),
                                       '--issue', self.issue, '--task', self.task, '--dry-run']):
            with contextlib.redirect_stdout(output):
                self.assertEqual(w.main(), 0)
        self.assertEqual(self.comments, [])
        self.assertIn(self.head, output.getvalue())
        self.assertTrue(any('/contents/' in args[4] for args in self.calls))
        self.assertTrue(all('POST' not in args for args in self.calls))

    def test_origin_mismatch_is_rejected_before_github(self):
        self.git('remote', 'set-url', 'origin', 'https://github.com/other/app.git')
        with self.assertRaisesRegex(ValueError, 'origin'):
            self.invoke()
        self.assertEqual(self.calls, [])

    def test_hidden_worktree_modification_cannot_replace_committed_state(self):
        self.git('update-index', '--assume-unchanged', 'docs/STATE.md')
        self.state.write_text('숨겨진 미커밋 내용')
        self.assertEqual(self.git('status', '--porcelain'), '')
        with self.assertRaisesRegex(ValueError, '커밋과 전달 파일'):
            self.invoke()
        self.assertEqual(self.comments, [])

    def test_remote_file_mismatch_is_rejected_without_posting(self):
        self.remote_file_mismatch = True
        with self.assertRaisesRegex(ValueError, '원격 전달 파일'):
            self.invoke()
        self.assertEqual(self.comments, [])

    def test_rewritten_origin_cannot_hide_github_branch_mismatch(self):
        self.remote_branch_mismatch = True
        with self.assertRaisesRegex(ValueError, 'GitHub 브랜치'):
            self.invoke()
        self.assertEqual(self.comments, [])

    def test_invalid_task_paths_do_not_post(self):
        for path in ['../outside.md', str(self.state), 'docs/tasks', 'docs/missing.md']:
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.invoke(task=path)
        self.assertEqual(self.comments, [])

    def test_ignored_untracked_task_is_not_a_reusable_checkpoint(self):
        (self.target / '.gitignore').write_text('docs/ignored.md\n')
        self.git('add', '.')
        self.git('commit', '-m', 'ignore task')
        self.git('push', 'origin', 'task/next')
        (self.target / 'docs/ignored.md').write_text('원격에 없는 내용')
        with self.assertRaises(ValueError):
            self.invoke(task='docs/ignored.md')
        self.assertEqual(self.comments, [])

    def test_linked_worktree_is_supported(self):
        linked = self.root / 'linked'
        self.git('worktree', 'add', '-b', 'task/linked', str(linked))
        self.target = linked
        self.git('push', '-u', 'origin', 'task/linked')
        self.invoke(task=self.task)
        self.assertIn(self.head, self.comments[0]['body'])

    def test_unknown_post_response_reuses_existing_comment_after_retry(self):
        self.fail_post_after_write = True
        with self.assertRaises(ValueError):
            self.invoke()
        self.assertEqual(len(self.comments), 1)
        self.fail_post_after_write = False
        self.invoke()
        self.assertEqual(len(self.comments), 1)

    def test_existing_comment_is_found_after_first_page(self):
        for i in range(100):
            self.comment(f'기존 댓글 {i}')
        self.invoke()
        self.invoke()
        self.assertEqual(len(self.comments), 101)
