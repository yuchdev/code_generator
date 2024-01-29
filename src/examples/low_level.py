from code_generation.core.source_file import SourceFile

__doc__ = """
"""


code = SourceFile('example.java')
code('import java.util.*;')

with code.block('public class Application'):
    with code.block('public static void main(String[] args)'):
        code('System.out.println("Hello world!");')
