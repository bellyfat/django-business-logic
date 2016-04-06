# -*- coding: utf-8 -*-
from django.utils.six import StringIO

from lxml import etree

from .common import *

#NAMESPACES = {'xmlns': 'http://www.w3.org/1999/xhtml'}

# https://blockly-demo.appspot.com/static/demos/code/index.html


class BlocklyXmlBuilderConstantTest(TestCase):
    def _constant_test(self, statement, block_type, field_name):
        root = Node.add_root()
        node = root.add_child(content_object=statement)
        xml_str = BlocklyXmlBuilder().build(node)
        xml = etree.parse(StringIO(xml_str))
        block = xml.xpath('/xml/block')
        self.assertEqual(1, len(block))
        block = block[0]
        self.assertEqual(block_type, block.get('type'))
        field = block.find('field')
        self.assertIsNotNone(field)
        self.assertEqual(field_name, field.get('name'))
        self.assertEqual(str(statement.value), field.text)

    def test_integer_constant(self):
        # https://blockly-demo.appspot.com/static/demos/code/index.html#hs3z8u
        self._constant_test(IntegerConstant(value=112), 'math_number', 'NUM')

    def test_float_constant(self):
        # https://blockly-demo.appspot.com/static/demos/code/index.html#zv7x7e
        self._constant_test(FloatConstant(value=1.11456), 'math_number', 'NUM')

    def test_string_constant(self):
        # https://blockly-demo.appspot.com/static/demos/code/index.html#94euw4
        self._constant_test(StringConstant(value='hello'), 'text', 'TEXT')


class BlocklyXmlBuilderAssignmentTest(TestCase):
    def test_assignment(self):
        # https://blockly-demo.appspot.com/static/demos/code/index.html#b7driq
        entry_point = var_A_assign_1()
        assign_node = entry_point.get_children()[1]

        xml_str = BlocklyXmlBuilder().build(assign_node)
        xml = etree.parse(StringIO(xml_str))

        block = xml.xpath('/xml/block')
        self.assertEqual(1, len(block))
        block = block[0]
        self.assertEqual('variables_set', block.get('type'))

        field, value = block.getchildren()

        self.assertEqual('field', field.tag)
        self.assertEqual('VAR', field.get('name'))
        self.assertEqual('A', field.text)

        self.assertEqual('value', value.tag)
        self.assertEqual('VALUE', value.get('name'))

        block_value, = value.getchildren()
        self.assertEqual('block', block_value.tag)
        self.assertEqual('math_number', block_value.get('type'))


class BlocklyXmlBuilderBlockTest(TestCase):
    def test_block(self):
        # https://blockly-demo.appspot.com/static/demos/code/index.html#h333qt
        root = Node.add_root()
        vars = ('A', 'B', 'C', 'D')
        var_defs = {}

        for var in vars:
            var_def = VariableDefinition(name=var)
            var_defs[var] = var_def
            root.add_child(content_object=var_def)
            root = Node.objects.get(id=root.id)

        for i, var in enumerate(vars, 1):
            assignment_node = root.add_child(content_object=Assignment())
            assignment_node.add_child(content_object=Variable(definition=var_defs[var]))
            assignment_node.add_child(content_object=IntegerConstant(value=i))
            root = Node.objects.get(id=root.id)

        xml_str = BlocklyXmlBuilder().build(root)
        xml = etree.parse(StringIO(xml_str))

        for i, var in enumerate(vars):
            var_value = i + 1
            variables_set_block_xpath = '/xml/block' + '/next/block' * i
            block = xml.xpath(variables_set_block_xpath)
            self.assertEqual(1, len(block))
            block = block[0]
            self.assertEqual('variables_set', block.get('type'))

            field = block.find('field')
            self.assertEqual('VAR', field.get('name'))
            self.assertEqual(var, field.text)

            value = block.find('value')
            self.assertEqual('VALUE', value.get('name'))

            math_number, = value.getchildren()
            self.assertEqual('math_number', math_number.get('type'))

            field, = math_number.getchildren()
            self.assertEqual('NUM', field.get('name'))
            self.assertEqual(str(var_value), field.text)


class BlocklyXmlBuilderBinaryOperatorTest(TestCase):
    #def _constant_test(self, statement, block_type, field_name):

    def _test_binary_operator(self, operator, field_value):
        root = Node.add_root(content_object=BinaryOperator(operator=operator))

        for i in (1, 2):
            root.add_child(content_object=IntegerConstant(value=i))
            root = Node.objects.get(id=root.id)

        xml_str = BlocklyXmlBuilder().build(root)
        xml = etree.parse(StringIO(xml_str))
        block = xml.xpath('/xml/block')
        self.assertEqual(1, len(block))
        block = block[0]
        self.assertEqual('math_arithmetic', block.get('type'))
        field = xml.xpath('/xml/block/field')[0]
        self.assertEqual('OP', field.get('name'))
        self.assertEqual(field_value, field.text)
        for field_value, field_name in enumerate(('A', 'B'), 1):
            value = xml.xpath('/xml/block/value[@name="{}"]'.format(field_name))[0]
            math_number = value.find('block')
            self.assertEqual('math_number', math_number.get('type'))
            field, = math_number.getchildren()
            self.assertEqual('NUM', field.get('name'))
            self.assertEqual(str(field_value), field.text)

    def test_operator_add(self):
        # https://blockly-demo.appspot.com/static/demos/code/index.html#mzvwas
        self._test_binary_operator('+', 'ADD')

    def test_operator_minus(self):
        # https://blockly-demo.appspot.com/static/demos/code/index.html#ec7z5c
        self._test_binary_operator('-', 'MINUS')

    def test_operator_mul(self):
        # https://blockly-demo.appspot.com/static/demos/code/index.html#nzq3w5
        self._test_binary_operator('*', 'MULTIPLY')

    def test_operator_div(self):
        # https://blockly-demo.appspot.com/static/demos/code/index.html#qzqt69
        self._test_binary_operator('/', 'DIVIDE')

    def test_operator_pow(self):
        # https://blockly-demo.appspot.com/static/demos/code/index.html#skakny
        self._test_binary_operator('^', 'POWER')

    def test_1plus2mul3(self):
        # https://blockly-demo.appspot.com/static/demos/code/index.html#b8dsrg
        root = tree_1plus2mul3()
        xml_str = BlocklyXmlBuilder().build(root)
        #print xml_str