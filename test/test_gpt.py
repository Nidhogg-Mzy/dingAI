import unittest
import os
import shutil   # for rmtree
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
        # delete two test cache folder
        cache_folder_1 = f'{GPTService._CACHE_FOLDER}/test1'
        cache_folder_2 = f'{GPTService._CACHE_FOLDER}/test2'
        # delete the folder and its content
        shutil.rmtree(cache_folder_1, ignore_errors=True)
        shutil.rmtree(cache_folder_2, ignore_errors=True)

        # reset the initialized flag
        GPTService._initialized = False

    def test_correctly_init(self):
        self.assertEqual(GPTService._initialized, True, 'GPTService should be initialized after calling load_config')

    def test_get_help(self):
        help_msg = GPTService.get_help()
        self.assertTrue('[Usage]' in help_msg)

        resp = GPTService.process_query(['chat', 'help'], 'test1')
        self.assertTrue('[Usage]' in resp)

    def test_invalid_query(self):
        with self.assertRaises(ValueError):
            GPTService.process_query(['invalid'], 'test1')
        with self.assertRaises(ValueError):
            GPTService.process_query([], 'test1')

        resp = GPTService.process_query(['chat'], 'test1')
        self.assertTrue(resp.startswith('[Error] Your query is not complete.'))

    def test_basic_chat(self):
        resp = GPTService.process_query(['chat', 'Who', 'won', 'the', 'world', 'series', 'in', '2020?'], 'test1')
        self.assertGreater(len(resp), 0)
        self.assertTrue('Los Angeles Dodgers' in resp)

        resp = GPTService.process_query(['chat', 'Where', 'was', 'it', 'played?'], 'test1')
        self.assertGreater(len(resp), 0)
        self.assertTrue('Arlington' in resp, 'GPT should have memory to answer this question')

    def test_chat_discard(self):
        resp = GPTService.process_query(['chat', 'Who', 'won', 'the', 'world', 'series', 'in', '2020?'], 'test1')
        self.assertGreater(len(resp), 0)
        self.assertTrue('Los Angeles Dodgers' in resp)

        # discard the memory
        resp = GPTService.process_query(['chatdiscard'], 'test1')
        self.assertTrue('Successfully **discarded**' in resp)

        # once we discard memory, gpt should not be able to answer this
        resp = GPTService.process_query(['chat', 'Where', 'was', 'it', 'played?'], 'test1')
        self.assertGreater(len(resp), 0)
        self.assertFalse('Arlington' in resp, 'GPT should NOT have memory to answer this question')


if __name__ == '__main__':
    unittest.main()
