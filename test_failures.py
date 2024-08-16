import unittest
from unittest.mock import patch, mock_open
from IPython.display import display, HTML
import pdf_processor
from importlib import reload
reload(pdf_processor)

class TestFailedContentSplit(unittest.TestCase):
    def setUp(self):
        self.max_length = 10

    def test_split_text(self):
        text = "This is a test. This is only a test."
        result = pdf_processor.split_text(text, 10)  # Using 10 as max_length
        
        print("Result:", result)  # Debug print to see the result
        
        # Check that each chunk is no longer than max_length
        self.assertTrue(all(len(chunk) <= 10 for chunk in result))
        
        # Check that the original text can be reconstructed from the chunks
        self.assertEqual(text, ' '.join(result))
        
        # Check specific expectations based on the splitting logic
        expected_chunks = ["This is a", "test. This", "is only a", "test."]
        self.assertEqual(result, expected_chunks)

class TestFailedPDFProcessor(unittest.TestCase):
    def setUp(self):
        self.root_dir = "root_directory_placeholder"
        self.config = {
            "reset_output": True,
            "output_folder": "test_output",
            "test_folder": "test_folder",
            "pdf_path": "/path/to/pdf",
            "toc_pages": [0],
            "token_size_input": 30
        }

    def test_parse_toc(self):
        toc_text = "Chapter 1..............10\nChapter 2..............20\n"
        result = pdf_processor.parse_toc(toc_text)
        self.assertEqual(result, {"Chapter 1": 9, "Chapter 2": 19})  # Adjusted to account for zero-based index

    def test_split_text(self):
        # Test case 1: Normal splitting
        text1 = "This is a test. It has multiple sentences. Let's see how it splits. This is another sentence."
        result1 = pdf_processor.split_text(text1, 30)
        
        print("Result1:", result1)  # Debug print to see the result1
        
        expected_chunks1 = ["This is a test. It has", "multiple sentences. Let's see", "how it splits. This is", "another sentence."]
        self.assertEqual(result1, expected_chunks1)
        self.assertTrue(all(len(chunk) <= 30 for chunk in result1))

        # Test case 2: Long sentence
        text2 = "This is a very long sentence that should be split into multiple chunks because it exceeds the maximum length."
        result2 = pdf_processor.split_text(text2, 30)
        
        print("Result2:", result2)  # Debug print to see the result2
        
        self.assertTrue(len(result2) > 1)
        self.assertTrue(all(len(chunk) <= 30 for chunk in result2))

        # Test case 3: Short text
        text3 = "Short text."
        result3 = pdf_processor.split_text(text3, 30)
        
        print("Result3:", result3)  # Debug print to see the result3
        
        self.assertEqual(len(result3), 1)
        self.assertEqual(result3[0], "Short text.")

if __name__ == '__main__':
    unittest.main(argv=[''], verbosity=2, exit=False)
    