from unittest.mock import patch
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTests(TestCase):
    def test_wait_for_db_ready(self):
        """Test waiting for db when db is available"""

        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 1)

    @patch('time.sleep', return_value=True)
    def test_wait_for_db_not_ready(self, time_sleep):
        """Test waiting for db when db is not available"""

        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # Adding True to exit the loop
            gi.side_effect = [OperationalError,
                              OperationalError,
                              OperationalError,
                              OperationalError,
                              OperationalError,
                              True]
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 6)
