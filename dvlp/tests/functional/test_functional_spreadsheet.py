import json
import unittest

from sauth.tests.helpers import make_user
from sfile.tests.helpers import make_file

from dvlp.tests import helpers as TH
from dvlp.spreadsheet import main
from dvlp.spreadsheet import model as M


class TestEmpty(unittest.TestCase):

    def setUp(self):
        self.api = TH.configure_functional_oauth_app(main.main)
        self.user = make_user(
            oauth=[dict(client_id=None, token='token-value')],
            password='foobar')
        self.api.authorize('token-value')

    def test_root(self):
        res = self.api.get('/1.0/', status=200)
        self.assertEqual(
            res.json, dict(user='test@example.com', version='1.0'))

    def test_lists(self):
        res = self.api.get('/1.0/list/', status=200)
        self.assertEqual(res.json, dict(lists=[]))

    def test_list_from_url(self):
        f = make_file(
            self.user, 'test.csv',
            'test@example.com\n')
        mapping = dict(header=False, sheet=0, email=0)
        res = self.api.post(
            '/1.0/list/',
            params=json.dumps(dict(
                file_nonce=f.metadata.nonce,
                mapping=mapping)),
            status=201)
        self.assertEqual(res.json['mapping'], mapping)


class TestWithList(unittest.TestCase):

    def setUp(self):
        self.api = TH.configure_functional_oauth_app(main.main)
        self.user = make_user(
            oauth=[dict(client_id=None, token='token-value')],
            password='foobar')
        self.api.authorize('token-value')
        content = '\n'.join([
            'id,name,email',
            '1,Example1,test1@example.com',
            '2,Example2,test2@example.com',
            '3,Example3,test3@example.com',
            '4,Example4,test4@example.com'])
        f = make_file(
            self.user, 'test.csv',
            content=content)
        self.lst = TH.make_list(
            self.user, f,
            mapping=dict(header=True, sheet=0, email=2))

    def test_lists(self):
        res = self.api.get('/1.0/list/', status=200)
        self.assertEqual(len(res.json['lists']), 1)
        res_lst = res.json['lists'][0]
        self.assertIn('mapping', res_lst)

    def test_get_list(self):
        res = self.api.get(
            str('/1.0/list/%s/' % self.lst._id),
            status=200)
        self.assertIn('mapping', res.json)

    def test_remap_list(self):
        mapping = dict(header=True, sheet=4, email=1)
        res = self.api.put(
            str('/1.0/list/%s/mapping/' % self.lst._id),
            params=json.dumps(mapping),
            status=200)
        self.assertEqual(res.json, mapping)

    def test_delete_list(self):
        res = self.api.delete(
            str('/1.0/list/%s/' % self.lst._id),
            status=204)
        self.assertEqual(
            M.List.query.find(dict(status='active')).count(), 0)
        self.assertEqual(
            M.List.query.find(dict(status='inactive')).count(), 1)
        res = self.api.get('/1.0/list/', status=200)
        self.assertEqual(res.json, dict(lists=[]))

    def test_get_subscribers(self):
        res = self.api.get(
            str('/1.0/list/%s/subscribers/' % self.lst._id))
        self.assertEqual(
            res.body,
            '1,test1@example.com\r\n'
            '2,test2@example.com\r\n'
            '3,test3@example.com\r\n'
            '4,test4@example.com\r\n')

