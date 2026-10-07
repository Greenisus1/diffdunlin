import json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
import diffdunlin as l
class LineTests(unittest.TestCase):
    def test_equal(self):self.assertTrue(l.compare('a\n','a\n')['comparison_equal'])
    def test_empty(self):self.assertTrue(l.compare('','')['raw_equal'])
    def test_insert(self):r=l.compare('a\n','a\nb\n');self.assertEqual(r['changes'][0]['kind'],'insert');self.assertEqual(r['changes'][0]['new_range_zero_based_half_open'],[1,2])
    def test_delete(self):self.assertEqual(l.compare('a\nb\n','a\n')['changes'][0]['kind'],'delete')
    def test_replace(self):self.assertEqual(l.compare('a\n','b\n')['changes'][0]['kind'],'replace')
    def test_final_newline(self):r=l.compare('a','a\n');self.assertFalse(r['comparison_equal']);self.assertFalse(r['old_final_newline']);self.assertTrue(r['new_final_newline'])
    def test_crlf(self):self.assertFalse(l.compare('a\r\n','a\n')['comparison_equal'])
    def test_ignore_trailing(self):r=l.compare('a \t\n','a\n',True);self.assertTrue(r['comparison_equal']);self.assertFalse(r['raw_equal'])
    def test_preserve_newline_ignoring(self):self.assertFalse(l.compare('a \n','a',True)['comparison_equal'])
    def test_not_ignore_leading(self):self.assertFalse(l.compare(' a\n','a\n',True)['comparison_equal'])
    def test_not_ignore_internal(self):self.assertFalse(l.compare('a b\n','ab\n',True)['comparison_equal'])
    def test_unicode(self):self.assertFalse(l.compare('é','e')['comparison_equal'])
    def test_safe(self):self.assertNotIn('\x1b',l.safe('x\x1b[31m'))
    def test_read_preserve(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'file';p.write_bytes(b'a\r\n');self.assertEqual(l.read(p),'a\r\n');self.assertEqual(p.read_bytes(),b'a\r\n')
    def test_invalid_binary(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'file';p.write_bytes(b'\x00')
            with self.assertRaises(ValueError):l.read(p)
    def test_fifo(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'fifo';os.mkfifo(p)
            with self.assertRaises(ValueError):l.read(p)
    def test_output_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'file';p.write_text('safe')
            with self.assertRaises(FileExistsError):l.save({},p)
    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/'a';b=Path(d)/'b';a.write_text('x');b.write_text('y');run=subprocess.run([sys.executable,'diffdunlin.py',str(a),str(b)],capture_output=True,text=True);self.assertEqual(run.returncode,1);b.write_text('x');run=subprocess.run([sys.executable,'diffdunlin.py',str(a),str(b)],capture_output=True,text=True);self.assertEqual(run.returncode,0)
if __name__=='__main__':unittest.main()
