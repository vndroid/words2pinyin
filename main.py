import json
import re
import yaml
from bottle import Bottle, request, response, run
from pypinyin import pinyin, Style

# 全角到半角映射表，包含常见中文字符及标点符号
FULL2HALF = dict((i + 0xfee0, i) for i in range(0x21, 0x7f))
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
    content_type = request.content_type
    body = request.body.read().decode('utf-8')
    data = None

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

    original_text = data['text']
    text = original_text.translate(FULL2HALF) # 标点全角转半角
    # 对于不在映射表中且未经转换的其余特殊符号/字符（即非中文且非基础 ASCII 的部分），替换为空格
    text = re.sub(r'[^\u4e00-\u9fa5\x20-\x7e]', ' ', text)
    tones = data.get('tones', 1)
    combine = data.get('combine', 0)
    compact = data.get('compact', 0)

    # 兼容通过独立参数或 compact 值传入的写法
    if data.get('lowercase') is not None or compact == 'lowercase':
        compact = 0
    elif data.get('uppercase') is not None or compact == 'uppercase':
        compact = 1
    elif data.get('camelcase') is not None or compact == 'camelcase':
        compact = 2

    if tones not in (0, 1, '0', '1') or combine not in (0, 1, '0', '1') or compact not in (0, 1, 2, '0', '1', '2'):
        response.status = 401
        return {'error': 'Illegal parameters'}

    # 转换为拼音
    style = Style.NORMAL if int(tones) == 0 else Style.TONE
    py_result = pinyin(text, style=style)

    # 处理拼音大小写模式
    compact = int(compact)
    if compact == 1:
        py_list = [item[0].upper() for item in py_result]
    elif compact == 2:
        py_list = [item[0].capitalize() for item in py_result]
    else:
        py_list = [item[0].lower() for item in py_result]

    separator = '' if int(combine) == 1 else ' '

    response.content_type = 'application/json'
    return {
        'original': original_text,
        'separate': py_list,
        'pinyin': separator.join(py_list)
    }


if __name__ == '__main__':
    run(app, host='0.0.0.0', port=8080, debug=True)
