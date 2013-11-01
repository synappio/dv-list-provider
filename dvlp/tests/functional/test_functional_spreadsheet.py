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
        content1 = '\n'.join([
            'id,name,email',
            'r1,Example1,test1@example.com',
            'r2,Example2,test2@example.com',
            'r3,Example3,test3@example.com',
            'r4,Example4,test4@example.com'])
        content2 = '\n'.join([
            's1,Example1,test1@example.com',
            's2,Example2,test2@example.com',
            's3,Example3,test3@example.com',
            's4,Example4,test4@example.com'])
        f1 = make_file(
            self.user, 'test.csv',
            content=content1)
        f2 = make_file(
            self.user, 'test.csv',
            content=content2)
        self.lst1 = TH.make_list(
            self.user, f1,
            mapping=dict(header=True, sheet=0, email=2))
        self.lst2 = TH.make_list(
            self.user, f2,
            mapping=dict(header=False, sheet=0, email=2))

    def test_lists(self):
        res = self.api.get('/1.0/list/', status=200)
        self.assertEqual(len(res.json['lists']), 2)
        res_lst = res.json['lists'][0]
        self.assertIn('mapping', res_lst)

    def test_get_list(self):
        res = self.api.get(
            str('/1.0/list/%s/' % self.lst1._id),
            status=200)
        self.assertIn('mapping', res.json)

    def test_remap_list(self):
        mapping = dict(header=True, sheet=4, email=1)
        res = self.api.put(
            str('/1.0/list/%s/mapping/' % self.lst1._id),
            params=json.dumps(mapping),
            status=200)
        self.assertEqual(res.json, mapping)

    def test_delete_list(self):
        res = self.api.delete(
            str('/1.0/list/%s/' % self.lst1._id),
            status=204)
        self.assertEqual(
            M.List.query.find(dict(status='active')).count(), 1)
        self.assertEqual(
            M.List.query.find(dict(status='inactive')).count(), 1)
        res = self.api.get('/1.0/list/', status=200)
        self.assertEqual(len(res.json['lists']), 1)

    def test_get_subscribers(self):
        res = self.api.get(
            str('/1.0/list/%s/subscribers.csv' % self.lst1._id))
        self.assertEqual(
            res.body,
            '1,test1@example.com\r\n'
            '2,test2@example.com\r\n'
            '3,test3@example.com\r\n'
            '4,test4@example.com\r\n')

    def test_get_subscribers_nohdr(self):
        res = self.api.get(
            str('/1.0/list/%s/subscribers.csv' % self.lst2._id))
        self.assertEqual(
            res.body,
            '1,test1@example.com\r\n'
            '2,test2@example.com\r\n'
            '3,test3@example.com\r\n'
            '4,test4@example.com\r\n')

    def test_append_list(self):
        content = '\n'.join([
            '0,A,B,C,D',
            '1,a,b,c,d',
            '2,a,b,c,d',
            '3,a,b,c,d',
            '4,a,b,c,d',
        ])
        f = make_file(
            self.user, 'test-appended.csv',
            content=content)
        self.api.post(
            str('/1.0/list/%s/' % self.lst1._id),
            params=json.dumps(dict(file_nonce=f.metadata.nonce)),
            status=200)
        res = self.api.get(
            str('/1.0/list/%s/appended.csv' % self.lst1._id),
            status=200)
        self.assertEqual(
            res.body,
            '0,A,B,C,D,id,name,email\r\n'
            '1,a,b,c,d,r1,Example1,test1@example.com\r\n'
            '2,a,b,c,d,r2,Example2,test2@example.com\r\n'
            '3,a,b,c,d,r3,Example3,test3@example.com\r\n'
            '4,a,b,c,d,r4,Example4,test4@example.com\r\n')

    def test_append_list_nohdr(self):
        content = '\n'.join([
            '0,A,B,C,D',
            '1,a,b,c,d',
            '2,a,b,c,d',
            '3,a,b,c,d',
            '4,a,b,c,d',
        ])
        f = make_file(
            self.user, 'test-appended.csv',
            content=content)
        self.api.post(
            str('/1.0/list/%s/' % self.lst2._id),
            params=json.dumps(dict(file_nonce=f.metadata.nonce)),
            status=200)
        res = self.api.get(
            str('/1.0/list/%s/appended.csv' % self.lst2._id),
            status=200)
        self.assertEqual(
            res.body,
            '0,A,B,C,D\r\n'
            '1,a,b,c,d,s1,Example1,test1@example.com\r\n'
            '2,a,b,c,d,s2,Example2,test2@example.com\r\n'
            '3,a,b,c,d,s3,Example3,test3@example.com\r\n'
            '4,a,b,c,d,s4,Example4,test4@example.com\r\n')



