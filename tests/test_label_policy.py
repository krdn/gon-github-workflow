import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import parse_qs, unquote, urlparse

sys.path.insert(0, str(Path(__file__).parents[1] / 'scripts'))
import github_setup as setup


class LabelPolicyTests(unittest.TestCase):
    def setUp(self):
        self.labels = {
            'bug': {'name': 'bug', 'color': 'd73a4a', 'description': "Something isn't working"},
            'good first issue': {'name': 'good first issue', 'color': '7057ff', 'description': 'Good for newcomers'},
            'team:custom': {'name': 'team:custom', 'color': '000000', 'description': '보존할 분류'},
        }
        self.usage = {}
        self.writes = []
        self.fail_usage = False
        self.fail_delete = False
        patcher = patch('subprocess.run', side_effect=self.process)
        patcher.start()
        self.addCleanup(patcher.stop)

    def process(self, args, **kwargs):
        method = args[args.index('--method') + 1]
        endpoint = args[args.index('--method') + 2]
        path = urlparse(endpoint).path
        query = parse_qs(urlparse(endpoint).query)
        payload = json.loads(kwargs.get('input') or '{}')
        if method != 'GET': self.writes.append((method, endpoint))
        if path.endswith('/issues'):
            self.assertEqual(query['state'], ['all'])
            if self.fail_usage:
                return SimpleNamespace(returncode=1, stdout='', stderr='HTTP 503')
            result = self.usage.get(query['labels'][0], [])
        elif method == 'GET':
            result = list(self.labels.values())
        elif method == 'POST':
            self.assertNotIn(payload['name'].lower(), self.labels)
            self.labels[payload['name'].lower()] = payload
            result = payload
        elif method == 'PATCH':
            key = unquote(path.rsplit('/', 1)[1]).lower()
            existing = self.labels.pop(key)
            existing.update(name=payload['new_name'], color=payload['color'], description=payload['description'])
            self.labels[existing['name'].lower()] = existing
            result = existing
        elif method == 'DELETE':
            if self.fail_delete:
                return SimpleNamespace(returncode=1, stdout='', stderr='HTTP 503')
            self.labels.pop(unquote(path.rsplit('/', 1)[1]).lower())
            return SimpleNamespace(returncode=0, stdout='', stderr='')
        else:
            raise AssertionError(args)
        return SimpleNamespace(returncode=0, stdout=json.dumps(result), stderr='')

    def test_new_repository_removes_unused_defaults_and_preserves_custom_labels(self):
        setup.configure_labels('owner/app', remove_defaults=True)
        self.assertNotIn('bug', self.labels)
        self.assertNotIn('good first issue', self.labels)
        self.assertIn('type:bug', self.labels)
        self.assertIn('needs:input', self.labels)
        self.assertIn('team:custom', self.labels)
        self.assertEqual(len(self.labels), 10)
        self.assertTrue(any('good%20first%20issue' in endpoint for method, endpoint in self.writes if method == 'DELETE'))

    def test_labels_used_on_closed_issues_and_pull_requests_are_preserved(self):
        self.usage = {'bug': [{'state': 'closed'}], 'good first issue': [{'state': 'closed', 'pull_request': {}}]}
        setup.configure_labels('owner/app', remove_defaults=True)
        self.assertIn('bug', self.labels)
        self.assertIn('good first issue', self.labels)
        self.assertFalse(any(method == 'DELETE' for method, _ in self.writes))

    def test_adopted_repository_does_not_delete_its_existing_defaults(self):
        setup.configure_labels('owner/app', remove_defaults=False)
        self.assertIn('bug', self.labels)
        self.assertFalse(any(method == 'DELETE' for method, _ in self.writes))

    def test_repeat_is_noop_and_standard_metadata_is_updated_in_place(self):
        self.labels['workflow:ai'] = {'name': 'Workflow:AI', 'color': 'ffffff', 'description': 'old'}
        setup.configure_labels('owner/app', remove_defaults=True)
        self.assertEqual(self.labels['workflow:ai']['name'], 'workflow:ai')
        self.assertNotEqual(self.labels['workflow:ai']['description'], 'old')
        self.writes.clear()
        setup.configure_labels('owner/app', remove_defaults=True)
        self.assertEqual(self.writes, [])

    def test_usage_query_failure_never_deletes_a_label(self):
        self.fail_usage = True
        with self.assertRaisesRegex(ValueError, '503'):
            setup.configure_labels('owner/app', remove_defaults=True)
        self.assertIn('bug', self.labels)
        self.assertFalse(any(method == 'DELETE' for method, _ in self.writes))

    def test_delete_failure_can_resume_without_duplicate_standard_labels(self):
        self.fail_delete = True
        with self.assertRaisesRegex(ValueError, '503'):
            setup.configure_labels('owner/app', remove_defaults=True)
        self.fail_delete = False
        setup.configure_labels('owner/app', remove_defaults=True)
        self.assertEqual(len(self.labels), 10)
