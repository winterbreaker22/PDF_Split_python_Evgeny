import unittest
import os
import json
from unittest.mock import patch, mock_open, MagicMock
import shutil

import pdf_processor
from importlib import reload
reload(pdf_processor)

class TestPDFProcessor(unittest.TestCase):

    def setUp(self):
        self.root_dir = pdf_processor.ROOT_DIR
        self.config = {
            "reset_output": True,
            "output_folder": "test_output",
            "test_folder": "test_folder",
            "pdf_path": "/path/to/pdf",
            "toc_pages": [0],
            "token_size_input": 30
        }

    def test_read_config(self):
        mock_config = json.dumps(self.config)
        with patch('builtins.open', mock_open(read_data=mock_config)):
            result = pdf_processor.read_config()
            self.assertEqual(result, self.config)

    @patch('os.path.exists')
    @patch('os.path.isdir')
    @patch('shutil.rmtree')
    def test_delete_output_folder(self, mock_rmtree, mock_isdir, mock_exists):
        mock_exists.return_value = True
        mock_isdir.return_value = True
        result = pdf_processor.delete_output_folder(self.config)
        mock_rmtree.assert_called_once_with(os.path.join(self.root_dir, self.config['output_folder']))

    @patch('os.path.exists')
    @patch('os.mkdir')
    def test_initialize_output_folder(self, mock_mkdir, mock_exists):
        mock_exists.return_value = False
        result = pdf_processor.initialize_output_folder(self.config, 'output_folder')
        self.assertEqual(result, os.path.join(self.root_dir, self.config['output_folder']))
        mock_mkdir.assert_called_once_with(os.path.join(self.root_dir, self.config['output_folder']))

    @patch('builtins.open', new_callable=mock_open)
    def test_initialize_csv_log(self, mock_file):
        output_folder = "/test/folder"
        result = pdf_processor.initialize_csv_log(output_folder, self.config)
        self.assertEqual(result, "/test/folder/log.csv")
        mock_file.assert_called_once_with('/test/folder/log.csv', mode='w', newline='')

    def test_num_tokens_from_string(self):
        text = "This is a test string."
        result = pdf_processor.num_tokens_from_string(text, "gpt-3.5-turbo")
        self.assertIsInstance(result, int)
        self.assertTrue(result > 0)

    def test_sanitize_filename(self):
        filename = "This is a <test> filename: with /invalid\\ characters?"
        result = pdf_processor.sanitize_filename(filename)
        self.assertEqual(result, "This_is_a_test_filename_with_invalid_characters")

if __name__ == '__main__':
    unittest.main(argv=[''], verbosity=2, exit=False)
