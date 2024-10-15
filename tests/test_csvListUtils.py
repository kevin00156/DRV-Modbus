import unittest
import os
from utils.csvListUtils import writeListToCsv, readListFromCsv

class TestCsvListUtils(unittest.TestCase):

    def setUp(self):
        self.test_file = 'test_data.csv'
        self.test_data = {
            'key1': [1, 2, 3],
            'key2': ["string1", "string2", "string3", "string4"],
            'key3': [1.23, 4.56]
        }

    def tearDown(self):
        pass
        #if os.path.exists(self.test_file):
        #    os.remove(self.test_file)
    
    def test_writeListToCsv(self):
        self.assertTrue(writeListToCsv(self.test_data, self.test_file))
        self.assertTrue(os.path.exists(self.test_file))

        with open(self.test_file, 'r', encoding='utf-8') as file:
            content = file.read()
            self.assertIn('key1,"[1, 2, 3]"', content)
            self.assertIn('key2,"[\'string1\', \'string2\', \'string3\', \'string4\']"', content)
            self.assertIn('key3,"[1.23, 4.56]"', content)

    def test_readListFromCsv(self):
        writeListToCsv(self.test_data, self.test_file)
        read_data = readListFromCsv(self.test_file)
        
        self.assertEqual(read_data, self.test_data)
        self.assertEqual(read_data['key1'], [1, 2, 3])
        self.assertEqual(read_data['key2'], ["string1", "string2", "string3", "string4"])
        self.assertEqual(read_data['key3'], [1.23, 4.56])

    def test_empty_dict(self):
        empty_data = {}
        self.assertFalse(writeListToCsv(empty_data, self.test_file))
        
if __name__ == '__main__':
    unittest.main()