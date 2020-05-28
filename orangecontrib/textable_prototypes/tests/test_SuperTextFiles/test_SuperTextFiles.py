import unittest
import pathlib

import orangecontrib.textable_prototypes.widgets.SuperTextFiles as stf

ASSETS_DIR = 'assets/'


class SuperTextFilesTests(unittest.TestCase):

    def setUp(self):
        """ Prepare some values to make tests"""
        self.raw_text_filepath = Path(ASSETS_DIR, 'test_raw_text.txt')
        self.image_filepath = Path(ASSETS_DIR, 'test_image_manuscript.jpg')
        self.textual_pdf_filepath  = Path(ASSETS_DIR, 'test_texual_pdf.pdf')
        self.non_textual_pdf_filepath  = Path(ASSETS_DIR, 'test_non_textual_pdf.pdf')
        self.filepathes = [
            self.raw_text_filepath,
            self.image_filepath,
            self.textual_pdf_filepath,
            self.non_textual_pdf_filepath
        ]

    def test_filetype(self):
        """ Test the detection of the filetype"""
        pass

    def test_is_textual_pdf_files(self):
        textual_file = stf.is_textual_pdf_files(self.textual_pdf_filepath)
        assertTrue(textual_file)

        non_textual_file = stf.is_textual_pdf_files(self.non_textual_pdf_filepath)
        assertFalse(non_textual_file)



if __name__ == '__main__':
    unittest.main()