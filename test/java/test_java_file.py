import unittest
import filecmp
import os

from code_generation.java.source_file import JavaSourceFile
from code_generation.java.class_generator import JavaClass
from code_generation.java.variable_generator import JavaVariable
from code_generation.java.function_generator import JavaFunction


class TestJavaFileIo(unittest.TestCase):
    """
    Test Java code generation by writing to file
    """

    def test_java_class(self):
        """
        Test Java class generation
        """
        java_file = JavaSourceFile('MyClass.java')
        my_class = JavaClass(name='MyClass')
        my_class.add_variable(JavaVariable(name='myVariable',
                                           type='int',
                                           is_static=True,
                                           is_final=True,
                                           value='10'))
        my_class.add_method(JavaFunction(name='getVar',
                                         return_type='int',
                                         is_static=True,
                                         implementation='return myVariable;'))
        my_class.render_to_string(java_file)
        self.assertTrue(filecmp.cmpfiles('.', 'tests', 'MyClass.java'))
        if os.path.exists('MyClass.java'):
            os.remove('MyClass.java')

    def test_java_interface(self):
        """
        Test Java interface generation
        """
        java_file = JavaSourceFile('MyInterface.java')
        my_interface = JavaClass(name='MyInterface')
        my_interface.add_variable(JavaVariable(name='myVariable', type='int'))
        my_interface.add_method(JavaFunction(name='getVar', return_type='int'))
        my_interface.render_to_string(java_file)
        self.assertTrue(filecmp.cmpfiles('.', 'tests', 'MyInterface.java'))
        if os.path.exists('MyInterface.java'):
            os.remove('MyInterface.java')

    def test_java_enum(self):
        """
        Test Java enum generation
        """
        java_file = JavaSourceFile('MyEnum.java')
        my_enum = JavaClass(name='MyEnum')
        my_enum.add_variable(JavaVariable(name='ITEM1', type='int', value='1'))
        my_enum.add_variable(JavaVariable(name='ITEM2', type='int', value='2'))
        my_enum.add_method(JavaFunction(name='getItem', return_type='int', implementation='return ITEM1;'))
        my_enum.render_to_string(java_file)
        self.assertTrue(filecmp.cmpfiles('.', 'tests', 'MyEnum.java'))
        if os.path.exists('MyEnum.java'):
            os.remove('MyEnum.java')

    def test_missing_class_name(self):
        """
        Test case for missing class name
        """
        java_file = JavaSourceFile('Missing.java')
        my_class = JavaClass()
        my_class.render_to_string(java_file)
        self.assertRaises(RuntimeError, my_class.render_to_string, java_file)


if __name__ == "__main__":
    unittest.main()
