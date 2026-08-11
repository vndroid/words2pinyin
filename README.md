# words2pinyin

## Environment

Requires [uv](https://docs.astral.sh/uv/) and Python >= 3.13 (uv will download it automatically if missing).

```bash
# Install dependencies (creates .venv from uv.lock)
uv sync

# Run in development mode (auto-reload + debug)
uv run main.py

# Run in production mode
APP_ENV=production uv run main.py

# Specify the number of gunicorn workers (default: 2 * CPU cores + 1)
APP_ENV=production APP_WORKERS=4 uv run main.py
```

Other useful commands:

```bash
uv add <package>      # add a dependency
uv lock --upgrade     # upgrade locked dependency versions
uv run ruff check .   # lint
```

## API Endpoint
**POST** `/pinyin`

**Supported Content-Types:**
- `application/json`
- `text/yaml` or `application/x-yaml`

### Request Parameters

| Parameter | Required | Type           | Default  | Description                                                                                                                                                                                                                                                                                           |
|-----------|----------|----------------|----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `text`    | **Yes**  | string         | -        | The input text (Chinese characters, words, etc.) to be converted.                                                                                                                                                                                                                                     |
| `tones`   | No       | integer        | `1`      | Controls the pinyin tone marks. <br> `1`: Append tones to pinyin. <br> `0`: Output plain pinyin letters without tones.                                                                                                                                                                                |
| `combine` | No       | integer        | `0`      | Controls spacing between the pinyin tokens. <br> `0`: Separate each character's pinyin with a space. <br> `1`: Combine all pinyin strings together without spaces.                                                                                                                                    |
| `compact` | No       | integer/string | `0`      | Controls the capitalization mode of the pinyin output. <br> `0` or `lowercase`: All lowercase letters. <br> `1` or `uppercase`: All uppercase letters. <br> `2` or `camelcase`: CamelCase (Capitalize the first letter).                                                                              |
| `filter`  | No       | string         | `"none"` | Filters JSON response fields. <br> `"none"`: Returns all default fields (`original`, `separate`, `pinyin`). <br> `"original"`: Returns only the `original` text field. <br> `"separate"`: Returns only the `separate` array list field. `"pinyin"`: Returns only the assembled `pinyin` string field. |

### Note on Unsupported Parameters
Using any parameter key not listed above will trigger an HTTP `400` Error: `Detected unsupported parameters`.

### Testing with cURL

**JSON Payload Example:**
```bash
curl -X POST http://localhost:8080/pinyin \
    -H "Content-Type: application/json" \
    -d '{"text": "你好世界", "tones": 0, "combine": 1, "compact": 1}'
```

**YAML Payload Example:**
```bash
curl -X POST http://localhost:8080/pinyin \
    -H "Content-Type: text/yaml" \
    -d "
text: 你好世界
tones: 0
combine: 1
compact: 1"
```

### Response Format

By default (`filter="none"`), the API responds with:
```json
{
    "original": "Your original parsed text",
    "separate": ["pin", "yin", "list", "items"],
    "pinyin": "pinyin str joined by spaces or combined"
}
```
