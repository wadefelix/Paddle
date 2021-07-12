#! /usr/bin/env python

# Copyright (c) 2021 PaddlePaddle Authors. All Rights Reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
TestCases for check_api_compatible.py
"""
import unittest
import sys
import os
import tempfile
import inspect

from check_api_compatible import read_argspec_from_file
from check_api_compatible import check_compatible


class Test_check_compatible(unittest.TestCase):
    def setUp(self) -> None:
        self.fullargspec_prefix = 'inspect.Full'
        self.argspec_str_o = self.fullargspec_prefix + '''ArgSpec(args=['shape', 'dtype', 'name'], varargs=None, varkw=None, defaults=(None, None), kwonlyargs=[], kwonlydefaults=None, annotations={})'''
        return super().setUp()

    def test_normal_not_changed(self):
        argspec_o = eval(self.argspec_str_o)
        argspec_n = eval(self.argspec_str_o)
        self.assertTrue(check_compatible(argspec_o, argspec_n))

    def test_args_added(self):
        argspec_str_n = '''ArgSpec(args=['shape', 'dtype', 'name', 'arg4'], varargs=None, varkw=None, defaults=(None, None), kwonlyargs=[], kwonlydefaults=None, annotations={})'''
        argspec_o = eval(self.argspec_str_o)
        argspec_n = eval(self.fullargspec_prefix + argspec_str_n)
        self.assertFalse(check_compatible(argspec_o, argspec_n))

        argspec_str_n = '''ArgSpec(args=['shape', 'dtype', 'name', 'arg4'], varargs=None, varkw=None, defaults=(None, None, None), kwonlyargs=[], kwonlydefaults=None, annotations={})'''
        argspec_n = eval(self.fullargspec_prefix + argspec_str_n)
        self.assertTrue(check_compatible(argspec_o, argspec_n))

    def test_args_places_exchanged(self):
        argspec_str_n = '''ArgSpec(args=['shape', 'name', 'dtype'], varargs=None, varkw=None, defaults=(None, None), kwonlyargs=[], kwonlydefaults=None, annotations={})'''
        argspec_o = eval(self.argspec_str_o)
        argspec_n = eval(self.fullargspec_prefix + argspec_str_n)
        self.assertFalse(check_compatible(argspec_o, argspec_n))

    def test_args_reduced(self):
        argspec_str_n = '''ArgSpec(args=['shape', 'name'], varargs=None, varkw=None, defaults=(None,), kwonlyargs=[], kwonlydefaults=None, annotations={})'''
        argspec_o = eval(self.argspec_str_o)
        argspec_n = eval(self.fullargspec_prefix + argspec_str_n)
        self.assertFalse(check_compatible(argspec_o, argspec_n))


class Test_read_argspec_from_file(unittest.TestCase):
    def setUp(self):
        self.api_spec_file = tempfile.TemporaryFile('w+t')
        if self.api_spec_file:
            self.api_spec_file.write("\n".join([
                """paddle.ones (ArgSpec(args=['shape', 'dtype', 'name'], varargs=None, varkw=None, defaults=(None, None), kwonlyargs=[], kwonlydefaults=None, annotations={}), ('document', '50a3b3a77fa13bb2ae4337d8f9d091b7'))""",
                # """paddle.four_plus_four (paddle.four_plus_four, ('document', 'ff0f188c95030158cc6398d2a6c5four'))""",
                """paddle.five_plus_five (ArgSpec(), ('document', 'ff0f188c95030158cc6398d2a6c5five'))""",
            ]))
            self.api_spec_file.seek(0)

    def tearDown(self):
        pass

    def test_case_normal(self):
        if self.api_spec_file:
            api_argspec_dict = read_argspec_from_file(self.api_spec_file)
            self.assertEqual(
                api_argspec_dict.get('paddle.ones'),
                '''ArgSpec(args=['shape', 'dtype', 'name'], varargs=None, varkw=None, defaults=(None, None), kwonlyargs=[], kwonlydefaults=None, annotations={})'''
            )
            self.assertEqual(
                api_argspec_dict.get('paddle.five_plus_five'), '''ArgSpec()''')
        else:
            self.fail('api_spec_file error')


if __name__ == '__main__':
    unittest.main()
