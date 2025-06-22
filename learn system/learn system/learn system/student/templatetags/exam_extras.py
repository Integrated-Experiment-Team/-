from django import template
import json

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    自定义模板过滤器，用于从字典中获取指定键的值
    支持字符串和字典类型的输入
    """
    try:
        # 如果是字符串，尝试解析为字典
        if isinstance(dictionary, str):
            dictionary = json.loads(dictionary)

        # 转换 key 为字符串，因为 JSON 解析后的键可能是字符串
        key = str(key)

        return dictionary.get(key)
    except (TypeError, ValueError, AttributeError):
        return None

@register.filter(name='chr')
def chr_filter(value):
    """
    将数字转换为对应的字符
    用于生成选项标识 A、B、C、D等
    """
    try:
        return chr(int(value))
    except (ValueError, TypeError):
        return ''