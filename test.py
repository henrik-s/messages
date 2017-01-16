import unittest
import urllib2
import json

SERVER_URL = 'http://127.0.0.1:5000'
USER_1 = 'Foo'
USER_2 = 'Bar'
NON_EXISTING_USER = 'Roger'


class MyTest(unittest.TestCase):
    def setUp(self):
        # Make sure USER_1 and USER_2 exist
        url = SERVER_URL + '/user/'+USER_1
        self.send_request(url, method='PUT')

        url = SERVER_URL + '/user/'+USER_2
        self.send_request(url, method='PUT')

    def test_create_user(self):
        url = SERVER_URL + '/user/'+'Donald'

        request_head, request_body = self.send_request(url, method='PUT')

        # First request should respond with status 201 CREATED
        self.assertEqual(request_head.code, 201)

        # Second request should respond with status 200
        request_head, request_body = self.send_request(url, method='PUT')

        self.assertEqual(request_head.code, 200)

    def test_send_message(self):
        url = SERVER_URL + '/user/'+USER_1+'/messages'
        data = json.dumps({"sender": USER_2, "message": "Hello me"})

        request_head, request_body = self.send_request(url, body=data, method='POST')

        self.assertEqual(request_head.code, 200)

    def test_send_message_missing_receiver(self):
        url = SERVER_URL + '/user/'+NON_EXISTING_USER+'/messages'
        data = json.dumps({"sender": USER_1, "message": "Hello me"})

        request_head, request_body = self.send_request(url, body=data, method='POST')

        self.assertEqual(request_head.code, 404)

    def test_send_message_missing_sender(self):
        url = SERVER_URL + '/user/'+USER_2+'/messages'
        data = json.dumps({"sender": NON_EXISTING_USER, "message": "Hello you"})

        request_head, request_body = self.send_request(url, body=data, method='POST')

    def test_send_message_missing_sender_param(self):
        url = SERVER_URL + '/user/'+USER_1+'/messages'
        data = json.dumps({"message": "Hello you"})

        request_head, request_body = self.send_request(url, body=data, method='POST')
        json_body = json.loads(request_body)

        self.assertEqual(request_head.code, 400)
        self.assertTrue('sender' in json_body)
        self.assertTrue('message' not in json_body)

    def test_send_message_missing_message_param(self):
        url = SERVER_URL + '/user/'+USER_1+'/messages'
        data = json.dumps({"sender": USER_2})

        request_head, request_body = self.send_request(url, body=data, method='POST')
        json_body = json.loads(request_body)

        self.assertEqual(request_head.code, 400)
        self.assertTrue('sender' not in json_body)
        self.assertTrue('message' in json_body)

    def test_send_message_missing_both_params(self):
        url = SERVER_URL + '/user/'+USER_1+'/messages'

        request_head, request_body = self.send_request(url, method='POST')
        json_body = json.loads(request_body)

        self.assertEqual(request_head.code, 400)
        self.assertTrue('sender' in json_body)
        self.assertTrue('message' in json_body)

    def test_fetch_unread_messages(self):
        # Start by purging unread messages
        url = SERVER_URL + '/user/'+USER_1+'/messages/unread'
        self.send_request(url)

        # Send a second request
        request_head, request_body = self.send_request(url)
        json_body = json.loads(request_body)

        # And verify that request is ok but response is empty
        self.assertEqual(request_head.code, 200)
        self.assertFalse(json_body)

        # Send a message from USER_2 to USER_1
        url = SERVER_URL + '/user/'+USER_1+'/messages'
        data = json.dumps({"sender": USER_2, "message": "Hello! Whats up?"})
        self.send_request(url, body=data, method='POST')

        # Now it is time to request unread messages for USER_1
        url = SERVER_URL + '/user/'+USER_1+'/messages/unread'
        request_head, request_body = self.send_request(url)
        json_body = json.loads(request_body)

        self.assertEqual(request_head.code, 200)
        self.assertEqual(json_body[0]['message'], 'Hello! Whats up?')
        self.assertEqual(json_body[0]['from'], USER_2)

    def test_fetch_unread_messages_missing_user(self):
        url = SERVER_URL + '/user/'+NON_EXISTING_USER+'/messages/unread'

        request_head, request_body = self.send_request(url)

        self.assertEqual(request_head.code, 404)

    def test_fetch_messages_within_interval(self):
        # Let's start by sending three message to USER_1
        url = SERVER_URL + '/user/'+USER_1+'/messages'
        data_1 = json.dumps({"sender": USER_2, "message": "First message"})
        data_2 = json.dumps({"sender": USER_2, "message": "Second message"})
        data_3 = json.dumps({"sender": USER_2, "message": "Third message"})
        self.send_request(url, body=data_1, method='POST')
        self.send_request(url, body=data_2, method='POST')
        self.send_request(url, body=data_3, method='POST')

        # Then get messages with index 0-1
        url = SERVER_URL + '/user/'+USER_1+'/messages?start=0&stop=1'

        request_head, request_body = self.send_request(url)
        json_body = json.loads(request_body)

        self.assertEqual(request_head.code, 200)
        self.assertEqual(json_body[0]['message'], 'Third message')
        self.assertEqual(json_body[1]['message'], 'Second message')

    def test_fetch_messages_within_interval_missing_start_param(self):
        url = SERVER_URL + '/user/'+USER_1+'/messages?stop=1'

        request_head, request_body = self.send_request(url)
        json_body = json.loads(request_body)

        self.assertEqual(request_head.code, 400)
        self.assertTrue('start' in json_body)

    def test_fetch_messages_within_interval_missing_stop_param(self):
        url = SERVER_URL + '/user/'+USER_1+'/messages?start=1'

        request_head, request_body = self.send_request(url)
        json_body = json.loads(request_body)

        self.assertEqual(request_head.code, 400)
        self.assertTrue('stop' in json_body)

    def test_fetch_messages_within_interval_missing_both_param(self):
        url = SERVER_URL + '/user/'+USER_1+'/messages'

        request_head, request_body = self.send_request(url)
        json_body = json.loads(request_body)

        self.assertEqual(request_head.code, 400)
        self.assertTrue('start' in json_body)
        self.assertTrue('stop' in json_body)

    def test_fetch_messages_within_interval_invalid_start_param(self):
        url = SERVER_URL + '/user/'+USER_1+'/messages?start=a&stop=1'

        request_head, request_body = self.send_request(url)
        json_body = json.loads(request_body)

        self.assertEqual(request_head.code, 400)
        self.assertFalse(json_body)

    def test_fetch_messages_within_interval_invalid_stop_param(self):
        url = SERVER_URL + '/user/'+USER_1+'/messages?start=0&stop=1aa'

        request_head, request_body = self.send_request(url)
        json_body = json.loads(request_body)

        self.assertEqual(request_head.code, 400)
        self.assertFalse(json_body)

    def test_fetch_messages_within_interval_missing_user(self):
        url = SERVER_URL + '/user/'+NON_EXISTING_USER+'/messages?start=0&stop=1'

        request_head, request_body = self.send_request(url)

        self.assertEqual(request_head.code, 404)

    def test_delete_messages(self):
        # Let's start by sending four message to USER_1
        url = SERVER_URL + '/user/'+USER_1+'/messages'
        data_1 = json.dumps({"sender": USER_2, "message": "Foo"})
        data_2 = json.dumps({"sender": USER_2, "message": "Foo bar"})
        data_3 = json.dumps({"sender": USER_2, "message": "bar foo"})
        data_4 = json.dumps({"sender": USER_2, "message": "foofoo"})
        self.send_request(url, body=data_1, method='POST')
        self.send_request(url, body=data_2, method='POST')
        self.send_request(url, body=data_3, method='POST')
        self.send_request(url, body=data_4, method='POST')

        # Find out the id for these two messages
        url = SERVER_URL + '/user/'+USER_1+'/messages?start=0&stop=1'
        request_head, request_body = self.send_request(url)
        json_body = json.loads(request_body)
        id_1 = str(json_body[0]['id'])
        id_2 = str(json_body[1]['id'])

        # Then delete these two
        url = SERVER_URL + '/user/'+USER_1+'/messages?id='+id_1+'&id='+id_2

        request_head, request_body = self.send_request(url, method='DELETE')
        json_body = json.loads(request_body)

        self.assertEqual(request_head.code, 200)
        self.assertTrue(int(id_1) in json_body)
        self.assertTrue(int(id_2) in json_body)

        # Finaly, verify that these message are not present in a second get request
        url = SERVER_URL + '/user/'+USER_1+'/messages?start=0&stop=1'
        request_head, request_body = self.send_request(url)
        json_body = json.loads(request_body)
        second_id_1 = json_body[0]['id']
        second_id_2 = json_body[1]['id']

        self.assertNotEqual(second_id_1, id_1)
        self.assertNotEqual(second_id_2, id_2)

    def test_delete_message_missing_param(self):
        url = SERVER_URL + '/user/'+USER_1+'/messages'

        request_head, request_body = self.send_request(url, method='DELETE')
        json_body = json.loads(request_body)

        self.assertEqual(request_head.code, 400)
        self.assertTrue('id' in json_body)

    def test_delete_message_invalid_id_param(self):
        url = SERVER_URL + '/user/'+USER_1+'/messages?id=fobo'

        request_head, request_body = self.send_request(url, method='DELETE')
        json_body = json.loads(request_body)

        self.assertEqual(request_head.code, 400)
        self.assertFalse(json_body)

    def test_delete_message_mssing_user(self):
        url = SERVER_URL + '/user/'+NON_EXISTING_USER+'/messages?id=fobo'

        request_head, request_body = self.send_request(url, method='DELETE')

        self.assertEqual(request_head.code, 404)

    def send_request(self, url, body=None, method='GET'):
        method = method
        handler = urllib2.HTTPHandler()
        opener = urllib2.build_opener(handler)
        request = urllib2.Request(url, data=body)

        if body:
            request.add_header("Content-Type", 'application/json')
        request.get_method = lambda: method
        request.add_header('Accept', '*/*')

        try:
            connection = opener.open(request)
        except urllib2.HTTPError, e:
            connection = e

        data = connection.read()

        connection.close()
        opener.close()
        return connection, data


if __name__ == '__main__':
    unittest.main()
