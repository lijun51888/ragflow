#
#  Copyright 2024 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import re

def replace_template_placeholders(template_string, variables):
    """
    该函数用于将模板字符串中的占位符（格式为 ${{key}}）替换为 variables 字典中对应的值。
    :param template_string: 包含占位符的模板字符串
    :param variables: 存储占位符键值对的字典
    :return: 替换后的字符串
    """
    # 定义一个函数用于替换匹配到的占位符
    def replace_placeholder(match):
        key = match.group(1)
        return variables.get(key, match.group(0))

    # 使用正则表达式匹配占位符并进行替换
    pattern = re.compile(r'\$\{\{(\w+)\}\}')
    result = pattern.sub(replace_placeholder, template_string)
    return result