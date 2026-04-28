import json
import yaml
from bottle import Bottle, request, response, run
from pypinyin import pinyin, Style

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

    text = data['text']
    tones = data.get('tones', 1)
    combine = data.get('combine', 0)

    if tones not in (0, 1, '0', '1') or combine not in (0, 1, '0', '1'):
        response.status = 401
        return {'error': 'Illegal parameters'}

    # 转换为拼音
    style = Style.NORMAL if int(tones) == 0 else Style.TONE
    py_result = pinyin(text, style=style)
    py_list = [item[0] for item in py_result]

    separator = '' if int(combine) == 1 else ' '

    response.content_type = 'application/json'
    return {
        'original': text,
        'pinyin': py_list,
        'pinyin_str': separator.join(py_list)
    }


if __name__ == '__main__':
    run(app, host='0.0.0.0', port=8080, debug=True)
