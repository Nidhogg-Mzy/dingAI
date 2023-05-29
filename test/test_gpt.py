import unittest
import configparser
from services.gpt import GPTService

# pylint: disable=protected-access
class GPTTests(unittest.TestCase):

    def setUp(self) -> None:
        configs = configparser.ConfigParser()
        # You may need to modify the path below, if your config file is in another folder
        configs.read('./config.ini')
        GPTService.load_config(configs)

        # if not enabled, skip the whole test
        if not GPTService._ENABLED or not GPTService._CHAT_ENABLED:
            self.skipTest('GPTService/Chat Service is not enabled in config.ini')

    def tearDown(self) -> None:
        # reset the initialized flag
        GPTService._initialized = False

    def test_correctly_init(self):
        self.assertEqual(GPTService._initialized, True, 'GPTService should be initialized after calling load_config')

    def test_get_help(self):
        help_msg = GPTService.get_help()
        self.assertTrue('[Usage]' in help_msg)

        resp = GPTService.process_query(['chat', 'help'], 'test')
        self.assertTrue('[Usage]' in resp)

    def test_invalid_query(self):
        with self.assertRaises(ValueError):
            GPTService.process_query(['invalid'], 'test')
        with self.assertRaises(ValueError):
            GPTService.process_query([], 'test')

        resp = GPTService.process_query(['chat'], 'test')
        self.assertTrue(resp.startswith('[Error] Your query is not complete.'))

    def test_basic_chat(self):
        resp = GPTService.process_query(['chat', 'Who', 'won', 'the', 'world', 'series', 'in', '2020?'], 'test')
        self.assertGreater(len(resp), 0)
        self.assertTrue('Los Angeles Dodgers' in resp)

        resp = GPTService.process_query(['chat', 'Where', 'was', 'it', 'played?'], 'test')
        self.assertGreater(len(resp), 0)
        self.assertTrue('Arlington' in resp, 'GPT should have memory to answer this question')


if __name__ == '__main__':
    unittest.main()
