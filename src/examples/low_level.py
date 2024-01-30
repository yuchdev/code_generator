from code_generation.core.source_file import SourceFile
from code_generation.core.code_formatter import CodeFormatterFactory, CodeFormat

__doc__ = """
"""


code = SourceFile('example.cpp', formatter=CodeFormat.ANSI_CPP)
code('import java.util.*;')

with code.block('public class Application'):
    with code.block('public static void main(String[] args)'):
        code('System.out.println("Hello world!");')
