# supreme-adventure

此專案提供一個小型 CLI，協助將「BarTender（Bartender）」標籤檔匯出的文字格式檔案做資料來源調整。

> 注意：BarTender `.btw` 通常是二進位格式；請先從 BarTender 匯出成 XML 或其他文字格式，再用本工具批次替換資料來源字串。

## 功能

- 以 JSON 定義資料來源替換規則。
- 可指定單一檔案或整個資料夾。
- 支援遞迴掃描資料夾。
- 預設在修改前建立 `.bak` 備份。
- 支援 `--dry-run` 預覽替換數量，不寫入檔案。

## 使用方式

建立替換設定，例如 `replacements.json`：

```json
{
  "replacements": [
    {
      "old": "Server=OLD-SQL;Database=Labels;",
      "new": "Server=NEW-SQL;Database=Labels;"
    },
    {
      "old": "C:\\\\old-share\\\\datasource.csv",
      "new": "C:\\\\new-share\\\\datasource.csv"
    }
  ]
}
```

預覽將會修改哪些檔案：

```bash
python3 tools/bartender_datasource_adjuster.py exported-label.xml --config replacements.json --dry-run
```

實際修改單一檔案：

```bash
python3 tools/bartender_datasource_adjuster.py exported-label.xml --config replacements.json
```

遞迴修改整個資料夾：

```bash
python3 tools/bartender_datasource_adjuster.py ./exported-labels --config replacements.json --recursive
```

若不想產生備份：

```bash
python3 tools/bartender_datasource_adjuster.py exported-label.xml --config replacements.json --no-backup
```

## 設定格式

`replacements` 可以是陣列：

```json
{
  "replacements": [
    {"old": "舊資料來源", "new": "新資料來源"}
  ]
}
```

也可以是物件：

```json
{
  "replacements": {
    "舊資料來源": "新資料來源"
  }
}
```

## 測試範例

範例替換設定放在 `tests/fixtures/replacements.json`，可用來驗證 CLI 能否讀取多筆替換規則。
