import unittest
import os
import tempfile
import pypandoc
from pathlib import Path

class TestDocxToMarkdownConversion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """创建测试用的DOCX文件"""
        cls.test_dir = tempfile.TemporaryDirectory()
        cls.base_path = Path(cls.test_dir.name)
        
        # 创建正常DOCX文件
        cls.valid_docx = cls.base_path / "normal.docx"
        cls.valid_docx.write_bytes(b'PK\x03\x04\x14\x00\x00\x00\x00\x00test_content')  # 最小DOCX文件头
        
        # 创建测试内容文件
        sample_content = """<?xml version="1.0" encoding="UTF-8"?>
        <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
            <w:body>
                <w:p><w:r><w:t>Hello World</w:t></w:r></w:p>
            </w:body>
        </w:document>"""
        
        # Create target directory first
        sample_dir = cls.base_path / "test_samples"
        sample_dir.mkdir(parents=True, exist_ok=True)
        
        # Use simple filename without spaces or special characters
        cls.sample_docx = sample_dir / "sample_content.docx"
        cls.sample_docx.write_text(sample_content)
        
        # 创建损坏的DOCX文件
        cls.invalid_docx = cls.base_path / "invalid.docx"
        cls.invalid_docx.write_bytes(b'INVALID_CONTENT')

    def test_successful_conversion(self):
        """测试正常DOCX文件转换"""
        output_path = self.base_path / "output.md"
        
        try:
            # 执行转换
            result = pypandoc.convert_file(
                str(self.sample_docx),
                'md',
                format='docx',
                outputfile=str(output_path),
                extra_args=['--standalone', '--columns=80']
            )
            
            # 验证输出文件
            self.assertTrue(output_path.exists())
            content = output_path.read_text()
            self.assertIn("Hello World", content)
            self.assertGreater(len(content), 10)
            
        except Exception as e:
            self.fail(f"Conversion failed unexpectedly: {str(e)}")

    def test_invalid_file_handling(self):
        """测试无效文件处理"""
        try:
            with self.assertRaises(RuntimeError) as context:
                pypandoc.convert_file(
                    str(self.invalid_docx),
                    'md',
                    format='docx',
                    extra_args=['--standalone', '--columns=80']
                )
            self.assertIn("Invalid", str(context.exception))
        except Exception as e:
            self.fail(f"Invalid file test failed unexpectedly: {str(e)}")

    def test_conversion_parameters(self):
        """测试转换参数是否生效"""
        output_path = self.base_path / "param_test.md"
        
        try:
            output = pypandoc.convert_file(
                '/Users/lijun/Git/ai-projects/ai-rag/ragflow/ragflow/temp/06-PPS_ClickGo用户操作手册_v2.3_0718.docx',
                'md',
                format='docx',
                extra_args=['--standalone', '--columns=80']
            )
            
            # Verify output file and parameters
            self.assertTrue(output_path.exists())
            content = output_path.read_text()
            self.assertIn("standalone", content.lower())
            self.assertNotIn("invalid-tag", content)
            
        except Exception as e:
            self.fail(f"Parameter test failed unexpectedly: {str(e)}")

    def test_conversion_parameters(self):
        """测试转换参数是否生效"""
        output_path = self.base_path / "param_test.md"
        file_path = '/Users/lijun/Git/ai-projects/ai-rag/ragflow/ragflow/temp/06-PPS_ClickGo用户操作手册'
        try:
            output = pypandoc.convert_file(
                '/Users/lijun/Git/ai-projects/ai-rag/ragflow/ragflow/temp/06-PPS_ClickGo用户操作手册_v2.3_0718.docx',
                'md',
                format='docx',
                extra_args=['--standalone', '--columns=80', '--extract-media', file_path]
            )
            
            # Verify output file and parameters
            self.assertTrue(output_path.exists())
            content = output_path.read_text()
            self.assertIn("standalone", content.lower())
            self.assertNotIn("invalid-tag", content)
            
        except Exception as e:
            self.fail(f"Parameter test failed unexpectedly: {str(e)}")

    @classmethod
    def tearDownClass(cls):
        """清理临时文件"""
        cls.test_dir.cleanup()

if __name__ == "__main__":
    unittest.main(verbosity=2)
