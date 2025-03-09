# zip-data-explained
- raw-data-structured-renamed
  - renamed with year and quarter e.g., 2014Q2
  - structured 2025Q1 partial data, since this quarter data is not yet released
- raw-data-grouped
  - grouped by transaction type
    - property-sales：一般不動產買賣
    - pre-construction-sales：預售屋買賣
    - property-rentals：不動產租賃

# 命名規則解析
## 範例： h_lvr_land_a_land.csv
- h → 代表桃園市（不同縣市用不同字母，如 a 為台北市，f 為新北市）
- lvr → 可能代表 Land Value Registration（地價登錄）
- land → 可能是通用的標記，代表此為不動產（房地產）交易相關資料
- a → 交易類別：
  - a：一般不動產買賣
  - b：預售屋買賣
  - c：不動產租賃
- land → 資料分類：
  - build：建物不動產（房屋）
  - land：土地不動產
  - park：停車場不動產
  - 無後綴（如 h_lvr_land_a.csv）：代表包含所有類別的綜合交易資料

## 不動產例子
| file name | schema file | description |
|-----------|-------------|-------------|
| a_lvr_land_a.csv | schema-main.csv | 臺北市不動產買賣 |
| a_lvr_land_a_build.csv | schema-build.csv | 臺北市建物不動產買賣 |
| a_lvr_land_a_land.csv | schema-land.csv | 臺北市土地不動產買賣 |
| a_lvr_land_a_park.csv | schema-park.csv | 臺北市停車場不動產買賣 |

## 預售屋例子
| file name | schema file | description |
|-----------|-------------|-------------|
| a_lvr_land_b.csv | schema-main-sale.csv | 臺北市預售屋買賣 |
| a_lvr_land_b_land.csv | schema-land.csv | 臺北市土地預售屋買賣 |
| a_lvr_land_b_park.csv | schema-park.csv | 臺北市停車場預售屋買賣 |

## 不動產租賃例子
| file name | schema file | description |
|-----------|-------------|-------------|
| a_lvr_land_c.csv | schema-main-rent.csv | 臺北市不動產租賃 |
| a_lvr_land_c_build.csv | schema-build.csv | 臺北市建物不動產租賃 |
| a_lvr_land_c_land.csv | schema-land.csv | 臺北市土地不動產租賃 |
| a_lvr_land_c_park.csv | schema-park.csv | 臺北市停車場不動產租賃 |

## 縣市代碼圖表
| 代碼 | 城市名稱 |
|--|--|
| a | 台北市 |
| b | 台中市 |
| c | 基隆市 |
| d | 台南市 |
| e | 高雄市 |
| f | 新北市 |
| g | 宜蘭縣 |
| h | 桃園市 |
| i | 嘉義市 |
| j | 新竹縣 |
| k | 苗栗縣 |
| m | 南投縣 |
| n | 彰化縣 |
| o | 新竹市 |
| p | 雲林縣 |
| q | 嘉義縣 |
| t | 屏東縣 |
| u | 花蓮縣 |
| v | 台東縣 |
| w | 金門縣 |
| x | 澎湖縣 |
| z | 連江縣 |

## 資料內容涵蓋日期
- 2020Q4為例
- 資料內容：登記日期自 109年9月11 至 109年12月10日之買賣案件，申報日期自 109年8月11 至 109年11月10日之租賃案件，及交易日期自109年8月11 至 109年11月10日之預售屋案件
- 因此如果民國35年買賣的案件，直到2020Q4才去登記的話，這樣的資料還是會被涵蓋在2020Q4的資料中，所以部分資料會涵蓋到非當期的資料是正常的！

