import unittest
import urllib2

from flask_testing import LiveServerTestCase
from app import app


class MyTest(LiveServerTestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_server_is_up_and_running(self):
        #print self.get_server_url() + '/user/Henrik/messages/unread'
        response = urllib2.urlopen(self.get_server_url() + '/user/Henrik/messages/unread')
        self.assertEqual(response.code, 200)


if __name__ == '__main__':
    unittest.main()
