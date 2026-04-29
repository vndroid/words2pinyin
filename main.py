import json
import os
import re
import yaml
from bottle import Bottle, request, response, run
from pypinyin import pinyin, Style

# 全角到半角映射表，包含常见中文字符及标点符号
FULL2HALF = {i + 0xfee0: i for i in range(0x21, 0x7f)}
FULL2HALF[0x3000] = 0x0020
CH_PUNC_MAP = {
    ord('，'): ord(','),
    ord('。'): ord('.'),
    ord('！'): ord('!'),
    ord('？'): ord('?'),
    ord('：'): ord(':'),
    ord('；'): ord(';'),
    ord('“'): ord('"'),
    ord('”'): ord('"'),
    ord('‘'): ord("'"),
    ord('’'): ord("'"),
    ord('（'): ord('('),
    ord('）'): ord(')'),
    ord('【'): ord('['),
    ord('】'): ord(']'),
    ord('《'): ord('<'),
    ord('》'): ord('>'),
    ord('、'): ord(','),
}
FULL2HALF.update(CH_PUNC_MAP)

app = Bottle()


@app.post('/pinyin')
def get_pinyin():
    content_type = request.content_type or ''
    body = request.body.read().decode('utf-8')

    if 'application/json' in content_type:
        try:
            data = json.loads(body)
        except ValueError:
            response.status = 400
            return {'error': 'Invalid JSON'}
    elif 'yaml' in content_type:
        try:
            data = yaml.safe_load(body)
        except yaml.YAMLError:
            response.status = 400
            return {'error': 'Invalid YAML'}
    else:
        # 尝试通过内容来猜测
        try:
            data = json.loads(body)
        except ValueError:
            try:
                data = yaml.safe_load(body)
            except yaml.YAMLError:
                response.status = 400
                return {'error': 'Cannot parse input as JSON or YAML'}

    if not isinstance(data, dict) or 'text' not in data:
        response.status = 400
        return {'error': 'Missing "text" field in the request payload'}

    allowed_params = {
        'text', 'tones', 'combine', 'compact',
        'lowercase', 'uppercase', 'camelcase', 'filter'
    }
    if any(key not in allowed_params for key in data.keys()):
        response.status = 400
        return {'error': 'Detected unsupported parameters'}

    original_text = data['text']
    text = original_text.translate(FULL2HALF)  # 标点全角转半角
    # 对于不在映射表中且未经转换的其余特殊符号/字符（即非中文且非基础 ASCII 的部分），替换为空格
    text = re.sub(r'[^\u4e00-\u9fa5\x20-\x7e]', ' ', text)
    tones = data.get('tones', 1)
    combine = data.get('combine', 0)
    compact = data.get('compact', 0)
    filter_val = data.get('filter', 0)

    # 兼容通过独立参数或 compact 值传入的写法
    if data.get('lowercase') is not None or compact == 'lowercase':
        compact = 0
    elif data.get('uppercase') is not None or compact == 'uppercase':
        compact = 1
    elif data.get('camelcase') is not None or compact == 'camelcase':
        compact = 2

    # 为 filter=0 增加 none 兼容选项
    if filter_val == 'none':
        filter_val = 0

    if (tones not in (0, 1, '0', '1') or
        combine not in (0, 1, '0', '1') or
        compact not in (0, 1, 2, '0', '1', '2')):
        response.status = 400
        return {'error': 'Illegal parameter values'}

    if filter_val not in (0, '0', 'original', 'separate', 'pinyin'):
        response.status = 400
        return {'error': 'Nonexistent request value'}

    # 转换为拼音
    style = Style.NORMAL if int(tones) == 0 else Style.TONE
    py_result = pinyin(text, style=style)

    # 将包含空格的英文等整块结果按空格进行拆分，保证单词与空格分离
    raw_list = [item[0] for item in py_result]
    py_list_raw = []
    for item in raw_list:
        py_list_raw.extend(re.findall(r'\S+|\s+', item))

    # 处理拼音大小写模式
    compact = int(compact)
    if compact == 1:
        py_list = [item.upper() for item in py_list_raw]
    elif compact == 2:
        py_list = [item.capitalize() for item in py_list_raw]
    else:
        py_list = [item.lower() for item in py_list_raw]

    separator = '' if int(combine) == 1 else ' '

    result = {
        'original': original_text,
        'separate': py_list,
        'pinyin': separator.join(py_list)
    }

    if filter_val not in (0, '0'):
        filter_key = str(filter_val)
        result = {filter_key: result[filter_key]}

    response.content_type = 'application/json'
    return result


if __name__ == '__main__':
    # 获取 CPU 核心数，并通常以 2 * cpu_count + 1 作为较佳的新工作进程数
    cpu_count = os.cpu_count() or 1
    workers = cpu_count * 2 + 1

    # 判断是否为生产环境 (默认开发环境)
    env = os.environ.get('APP_ENV', 'development')
    is_reload = env != 'production'

    run(app, host='0.0.0.0', port=8080, server='gunicorn', workers=workers, reload=is_reload)
