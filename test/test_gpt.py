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
        self.assertTrue('[Basic Usage]' in help_msg)

        resp = GPTService.process_query(['chat', 'help'], 'test1')
        self.assertTrue('[Basic Usage]' in resp)

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

    def test_chat_save(self):
        resp = GPTService.process_query(['chat', 'Who', 'won', 'the', 'world', 'series', 'in', '2020?'], 'test1')
        self.assertGreater(len(resp), 0)
        self.assertTrue('Los Angeles Dodgers' in resp)

        # save the current chat
        resp = GPTService.process_query(['chatsave'], 'test1')
        self.assertTrue('Error' in resp)  # invalid syntax, chatsave should provide a name
        resp = GPTService.process_query(['chatsave', 'testsave'], 'test1')
        self.assertTrue('Successfully saved current chat history' in resp)
        self.assertTrue('1. testsave' in resp)

        # now the current chat should be saved in the cache folder
        saved_hist = f'{GPTService._CACHE_FOLDER}/test1/1-testsave.json'
        self.assertTrue(os.path.exists(saved_hist), 'Saved a chat, but 1-testsave.json does not exist.')
        # also check its content
        with open(saved_hist, 'r', encoding='utf-8') as f:
            saved_hist = f.read()
        self.assertTrue('Los Angeles Dodgers' in saved_hist)

    def test_chat_save_hist_load_delete(self):
        # check stored history when there is no saved chat
        resp = GPTService.process_query(['chathist'], 'test1')
        self.assertTrue('You don\'t have any chat history yet.' in resp, 'There should be no saved chat history yet')

        _ = GPTService.process_query(['chat', 'Who', 'won', 'the', 'world', 'series', 'in', '2020?'], 'test1')
        _ = GPTService.process_query(['chatsave', 'testsave'], 'test1')

        # check stored history
        resp = GPTService.process_query(['chathist'], 'test1')
        self.assertTrue('Your chat histories:' in resp)
        self.assertTrue('1. testsave' in resp)

        # load the saved chat
        # some invalid queries
        resp = GPTService.process_query(['chatload'], 'test1')
        self.assertTrue('Error' in resp)  # invalid syntax, chatload should provide a name
        resp = GPTService.process_query(['chatload', 'testsave'], 'test1')
        self.assertTrue('Error' in resp)  # invalid syntax, chatload should provide number
        resp = GPTService.process_query(['chatload', '2'], 'test1')
        self.assertTrue('Error' in resp)  # invalid number provided
        # valid query
        resp = GPTService.process_query(['chatload', '1'], 'test1')
        self.assertTrue('History 1 loaded successfully' in resp)
        self.assertTrue('Los Angeles Dodgers' in resp, 'chatload should display the last response')

        # once we load memory, gpt should be able to answer this
        resp = GPTService.process_query(['chat', 'Where', 'was', 'it', 'played?'], 'test1')
        self.assertTrue('Arlington' in resp, 'GPT should have memory to answer this question')

        # now try to save another chat
        resp = GPTService.process_query(['chat', 'Who', 'invented', 'Java', 'language'], 'test1')
        self.assertTrue('James Gosling' in resp)
        resp = GPTService.process_query(['chatsave', 'testjava'], 'test1')
        self.assertTrue('2. testjava' in resp)

        # check stored history
        resp = GPTService.process_query(['chathist'], 'test1')
        self.assertTrue('Your chat histories:' in resp)
        self.assertTrue('1. testsave' in resp)
        self.assertTrue('2. testjava' in resp)

        # load the saved chat
        resp = GPTService.process_query(['chatload', '2'], 'test1')
        self.assertTrue('History 2 loaded successfully' in resp)
        self.assertTrue('James Gosling' in resp, 'chatload should display the last response')

        # delete the saved chat
        resp = GPTService.process_query(['chatdelete'], 'test1')
        self.assertTrue('Error' in resp)  # invalid syntax, chatdelete should provide a name
        resp = GPTService.process_query(['chatdelete', 'testsave'], 'test1')
        self.assertTrue('Error' in resp)  # invalid syntax, chatdelete should provide an integer
        resp = GPTService.process_query(['chatdelete', '1'], 'test1')
        self.assertTrue('Successfully deleted history 1' in resp)

        # check stored history
        resp = GPTService.process_query(['chathist'], 'test1')
        self.assertTrue('Your chat histories:' in resp)
        self.assertFalse('1. testsave' in resp, 'History 1 should be deleted')
        self.assertTrue('1. testjava' in resp, 'History 2 should be renamed to 1.')

        # try load new 1st chat
        resp = GPTService.process_query(['chatload', '1'], 'test1')
        self.assertTrue('History 1 loaded successfully' in resp)
        self.assertFalse('Los Angeles Dodgers' in resp, 'chatload loads the wrong chat.')
        self.assertTrue('James Gosling' in resp, 'chatload should display the last response.')

        # then also delete it
        resp = GPTService.process_query(['chatdelete', '1'], 'test1')
        self.assertTrue('Successfully deleted history 1' in resp)
        resp = GPTService.process_query(['chathist'], 'test1')
        self.assertTrue('You don\'t have any chat history yet.' in resp, 'All chat history should be deleted')

    def test_chat_save_mult_times(self):
        self.skipTest('Not Implemented.')

    def test_chat_mult_user(self):
        self.skipTest('Not Implemented.')


if __name__ == '__main__':
    unittest.main()
