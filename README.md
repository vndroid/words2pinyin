# words2pinyin

## Environment

```bash
APP_ENV=production python3 main.py
```

## API Endpoint
**POST** `/pinyin`

**Supported Content-Types:**
- `application/json`
- `text/yaml` or `application/x-yaml`

### Request Parameters

| Parameter   | Required | Type             | Default | Description                                                                                                                                                                                                                                                                                                  |
|-------------|----------|------------------|---------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `text`      | **Yes**  | String           | -       | The input text (Chinese characters, words, etc.) to be converted.                                                                                                                                                                                                                                            |
| `tones`     | No       | Integer / String | `1`     | Controls the pinyin tone marks. <br> `1`: Append tones to pinyin. <br> `0`: Output plain pinyin letters without tones.                                                                                                                                                                                       |
| `combine`   | No       | Integer / String | `0`     | Controls spacing between the pinyin tokens. <br> `0`: Separate each character's pinyin with a space. <br> `1`: Combine all pinyin strings together without spaces.                                                                                                                                           |
| `compact`   | No       | Integer / String | `0`     | Controls the capitalization mode of the pinyin output. <br> `0` or `lowercase`: All lowercase letters. <br> `1` or `uppercase`: All uppercase letters. <br> `2` or `camelcase`: CamelCase (Capitalize the first letter).                                                                                     |
| `filter`    | No       | Integer / String | `0`     | Filters JSON response fields. <br> `0` or `"none"`: Returns all default fields (`original`, `separate`, `pinyin`). <br> `"original"`: Returns only the `original` text field. <br> `"separate"`: Returns only the `separate` array list field. `"pinyin"`: Returns only the assembled `pinyin` string field. |

### Note on Unsupported Parameters
Using any parameter key not listed above will trigger an HTTP `400` Error: `Detected unsupported parameters`.

### Response Format

By default (`filter=0`), the API responds with:
```json
{
    "original": "Your original parsed text",
    "separate": ["pin", "yin", "list", "items"],
    "pinyin": "pinyin str joined by spaces or combined"
}
```
