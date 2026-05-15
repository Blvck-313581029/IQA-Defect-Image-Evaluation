# IQA Defect Image Evaluation

本專案是一個用於**瑕疵影像品質評估**的工具。

主要目標是針對輸入影像，透過多個 no-reference image quality assessment 指標，判斷該影像是否符合基本品質需求。目前支援四個指標：

1. MUSIQ
2. NIQE
3. BRISQUE
4. Laplacian Variance

本程式支援單張圖片輸入，也支援整個資料夾批次輸入。  
執行時，terminal 會輸出每個指標的 pass / fail 結果，而詳細的分數資訊會另外存成 log、CSV 與 Excel 檔案。

---

## 專案架構

```bash
iqa-defect-evaluation/
│
├── README.md
├── requirements.txt
├── config.yaml
│
├── main.py
├── download_assets.py
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── logger.py
│   ├── evaluator.py
│   ├── utils.py
│   │
│   └── metrics/
│       ├── __init__.py
│       ├── musiq.py
│       ├── niqe.py
│       ├── brisque.py
│       └── laplacian.py
│
├── assets/
│   ├── niqe_pris_params.npz
│   └── allmodel
│
└── outputs/
    ├── iqa_results.csv
    ├── iqa_results.xlsx
    └── logs/
        └── run.log
```

---

## 功能特色

- 使用四個影像品質指標進行評估。
- 支援單張影像與資料夾批次輸入。
- 可透過 `config.yaml` 設定輸入路徑、輸出路徑、threshold 與權重。
- terminal 只輸出簡潔的 pass / fail 結果。
- 詳細的 metric 數值會存入 log 檔。
- 評估結果會輸出成 CSV 與 Excel。
- 各個 metric 的實作分開管理，方便後續維護與修改。

---

## 安裝方式

建議先建立一個 Python 環境：

```bash
conda create -n iqa_env python=3.10
conda activate iqa_env
```

安裝所需套件：

```bash
pip install -r requirements.txt
```

`requirements.txt` 內容如下：

```txt
opencv-python
numpy
pandas
scipy
Pillow
torch
pyiqa
libsvm-official
openpyxl
PyYAML
```

---

## 下載必要模型檔案

本專案需要兩個外部模型檔案：

1. NIQE pristine natural image model parameters
2. BRISQUE pretrained SVR model

可以透過以下指令下載：

```bash
python download_assets.py
```

下載後，檔案會放在：

```bash
assets/
├── niqe_pris_params.npz
└── allmodel
```

這兩個檔案分別會被 NIQE 和 BRISQUE 使用。

---

## 設定檔說明

大部分參數都可以在 `config.yaml` 裡面修改。

範例：

```yaml
input:
  path: "./data/test.jpg"

output:
  dir: "./outputs"

assets:
  niqe_param_path: "./assets/niqe_pris_params.npz"
  brisque_model_path: "./assets/allmodel"

thresholds:
  MUSIQ: 23.0
  NIQE: 8.2
  BRISQUE: 64.0
  Laplacian_variance: 20.0

weights:
  MUSIQ: 0.25
  NIQE: 0.25
  BRISQUE: 0.25
  Laplacian_variance: 0.25
```

### Config 欄位說明

| 欄位 | 說明 |
|---|---|
| `input.path` | 輸入影像路徑，可以是單張圖片或資料夾 |
| `output.dir` | 輸出資料夾，用來存放 CSV、Excel 和 log |
| `assets.niqe_param_path` | NIQE pristine natural image model 參數路徑 |
| `assets.brisque_model_path` | BRISQUE pretrained SVR model 路徑 |
| `thresholds` | 每個 metric 的 pass / fail 門檻值 |
| `weights` | 計算 final score 時使用的權重 |

---

## 支援的評估指標

### 1. MUSIQ

MUSIQ 是一種 learning-based 的 no-reference image quality assessment 指標。

本專案中，MUSIQ 透過 `pyiqa` 套件載入。

- 分數越高通常代表影像品質越好。
- 當 MUSIQ 分數大於或等於設定的 threshold 時，代表通過。

```text
MUSIQ_pass = MUSIQ >= MUSIQ_threshold
```

---

### 2. NIQE

NIQE 是一種基於 natural scene statistics 的 no-reference image quality assessment 指標。

它不需要 reference image，而是將輸入影像的統計特徵與 pristine natural image model 進行比較。

- 分數越低通常代表影像品質越好。
- 當 NIQE 分數小於或等於設定的 threshold 時，代表通過。

```text
NIQE_pass = NIQE <= NIQE_threshold
```

---

### 3. BRISQUE

BRISQUE 也是一種基於 natural scene statistics 的 no-reference image quality assessment 指標。

它會從影像中抽取 NSS features，然後丟入 pretrained SVR model 預測影像品質分數。

- 分數越低通常代表影像品質越好。
- 當 BRISQUE 分數小於或等於設定的 threshold 時，代表通過。

```text
BRISQUE_pass = BRISQUE <= BRISQUE_threshold
```

---

### 4. Laplacian Variance

Laplacian Variance 主要用來估計影像的清晰程度。

它會先將影像轉成灰階，接著使用 Laplacian operator 偵測影像中的邊緣變化，最後計算 response 的 variance。

- 分數越高通常代表影像越清楚。
- 分數越低通常代表影像越模糊。
- 當 Laplacian Variance 大於或等於設定的 threshold 時，代表通過。

```text
Laplacian_pass = Laplacian_variance >= Laplacian_variance_threshold
```

---

## 指標方向整理

| 指標 | 越高越好 / 越低越好 | Pass 判斷方式 |
|---|---|---|
| MUSIQ | 越高越好 | `MUSIQ >= threshold` |
| NIQE | 越低越好 | `NIQE <= threshold` |
| BRISQUE | 越低越好 | `BRISQUE <= threshold` |
| Laplacian Variance | 越高越好 | `Laplacian_variance >= threshold` |

---

## 執行方式

### 使用預設 config 執行

```bash
python main.py --config config.yaml
```

### 評估單張影像

```bash
python main.py --config config.yaml --input_path ./data/test.jpg
```

### 評估整個資料夾

```bash
python main.py --config config.yaml --input_path ./data/images
```

### 指定輸出資料夾

```bash
python main.py --config config.yaml --output_dir ./my_outputs
```

---

## 輸出檔案

執行完成後，結果會儲存在 output 資料夾中。

```bash
outputs/
├── iqa_results.csv
├── iqa_results.xlsx
└── logs/
    └── run.log
```

---

## CSV 與 Excel 輸出內容

CSV 和 Excel 會針對每張圖片輸出一列結果。

欄位範例如下：

| 欄位 | 說明 |
|---|---|
| `image_name` | 影像檔名 |
| `MUSIQ` | MUSIQ 分數 |
| `NIQE` | NIQE 分數 |
| `BRISQUE` | BRISQUE 分數 |
| `Laplacian_variance` | Laplacian Variance 分數 |
| `MUSIQ_pass` | MUSIQ 是否通過 |
| `NIQE_pass` | NIQE 是否通過 |
| `BRISQUE_pass` | BRISQUE 是否通過 |
| `Laplacian_pass` | Laplacian Variance 是否通過 |
| `final_score` | 加權後的總覽分數 |
| `final_pass` | 四個指標是否全部通過 |
| `image_path` | 原始影像路徑 |

---

## Terminal 輸出

Terminal 只會顯示簡潔的 pass / fail 結果。

範例：

```text
================ IQA Summary ================

Image: aircraft1_missing_head_001.jpg
MUSIQ pass              : True
NIQE pass               : False
BRISQUE pass            : True
Laplacian Variance pass : True
Final pass              : False

Detailed information has been saved to log file.
=============================================
```

Terminal 輸出刻意保持簡潔。  
詳細分數會存放在 log 檔、CSV 和 Excel 裡面。

---

## Log 輸出

Log 檔會記錄更詳細的 metric 結果，方便後續檢查與追蹤。

範例：

```text
[2026-05-15 12:00:00] [INFO] Processing: ./data/test.jpg
[2026-05-15 12:00:01] [INFO] Image: test.jpg
[2026-05-15 12:00:01] [INFO]   MUSIQ               : 31.2045, pass=True
[2026-05-15 12:00:01] [INFO]   NIQE                : 9.1843, pass=False
[2026-05-15 12:00:01] [INFO]   BRISQUE             : 52.2910, pass=True
[2026-05-15 12:00:01] [INFO]   Laplacian Variance  : 33.7782, pass=True
[2026-05-15 12:00:01] [INFO]   Final Score         : 91.5022
[2026-05-15 12:00:01] [INFO]   Final Pass          : False
```

---

## Final Pass 判斷方式

每個 metric 都有自己的 threshold。

```text
MUSIQ_pass              = MUSIQ >= MUSIQ_threshold
NIQE_pass               = NIQE <= NIQE_threshold
BRISQUE_pass            = BRISQUE <= BRISQUE_threshold
Laplacian_pass          = Laplacian_variance >= Laplacian_variance_threshold
```

最後的 `final_pass` 會這樣計算：

```text
final_pass = MUSIQ_pass
             and NIQE_pass
             and BRISQUE_pass
             and Laplacian_pass
```

也就是說，只有當四個指標都通過時，該影像才會被判定為通過。

---

## Final Score

`final_score` 是一個 0 到 100 的加權總覽分數。

它主要是提供一個整體品質參考，但不會取代 `final_pass`。

預設權重如下：

```yaml
weights:
  MUSIQ: 0.25
  NIQE: 0.25
  BRISQUE: 0.25
  Laplacian_variance: 0.25
```

分數會先根據 threshold 做 normalization，再依照權重加總。

```text
final_score =
    MUSIQ_weight * MUSIQ_norm
  + NIQE_weight * NIQE_norm
  + BRISQUE_weight * BRISQUE_norm
  + Laplacian_weight * Laplacian_norm
```

對於越高越好的指標：

```text
score_norm = min(score / threshold, 1.0)
```

對於越低越好的指標：

```text
score_norm = min(threshold / score, 1.0)
```

`final_score` 主要用於快速觀察整體影像品質，但主要判斷仍以 `final_pass` 為準。

---

## Threshold 調整建議

目前的 threshold 是初版設定值：

```yaml
thresholds:
  MUSIQ: 23.0
  NIQE: 8.2
  BRISQUE: 64.0
  Laplacian_variance: 20.0
```

這些 threshold 建議要根據實際資料集的分布進行調整。

建議流程如下：

1. 先對一批影像進行評估。
2. 查看 CSV 或 Excel 輸出結果。
3. 將 metric 分數與人工判斷結果進行比較。
4. 調整 `config.yaml` 裡面的 threshold。
5. 重新執行評估。
6. 重複調整直到結果符合預期品質標準。

例如：

- 如果很多肉眼可接受的影像都因為 NIQE 沒過，可能需要放寬 NIQE threshold。
- 如果模糊影像仍然通過，可能需要提高 Laplacian Variance threshold。
- 如果資料集的 MUSIQ 分數普遍偏低，可能需要調整 MUSIQ threshold。
- 如果 BRISQUE 太嚴格或太寬鬆，也可以調整 BRISQUE threshold。

---

## 支援影像格式

目前支援以下影像格式：

```text
.jpg
.jpeg
.png
.bmp
.tif
.tiff
.webp
```

---

## 範例執行流程

```bash
# 1. 安裝套件
pip install -r requirements.txt

# 2. 下載 NIQE 和 BRISQUE 需要的模型檔案
python download_assets.py

# 3. 評估單張影像
python main.py --config config.yaml --input_path ./data/test.jpg

# 4. 評估整個資料夾
python main.py --config config.yaml --input_path ./data/images

# 5. 查看詳細 log
cat outputs/logs/run.log
```

---

## 設計說明

本專案將程式拆成幾個主要部分：

- `main.py`：處理 command line arguments，並啟動整體評估流程。
- `config.yaml`：存放使用者可調整的設定，例如 path、threshold、weights。
- `src/evaluator.py`：負責主要的影像評估流程與結果彙整。
- `src/metrics/`：存放四個 metric 的實作。
- `src/utils.py`：處理影像讀取與檔案蒐集。
- `src/logger.py`：處理 terminal 與 log file 的輸出。
- `outputs/`：存放所有評估結果。

這樣的架構可以避免所有程式都塞在同一個檔案裡，同時也不會切得太零散，方便後續維護與擴充。

---

## 關於 `__init__.py`

在 `src/` 和 `src/metrics/` 裡面會看到 `__init__.py`：

```bash
src/
├── __init__.py
└── metrics/
    ├── __init__.py
    ├── musiq.py
    ├── niqe.py
    ├── brisque.py
    └── laplacian.py
```

這兩個 `__init__.py` 可以是空檔案。

它們的用途是告訴 Python：

```text
src 是一個 package
metrics 也是一個 package
```

這樣在其他程式中就可以正常 import：

```python
from src.metrics.musiq import MUSIQMetric
from src.metrics.niqe import NIQEMetric
from src.metrics.brisque import BRISQUEMetric
from src.metrics.laplacian import calculate_laplacian_variance
```

雖然新版 Python 有時候沒有 `__init__.py` 也可以執行，但放著會比較標準，也比較適合整理成 GitHub repo。

---

## 總結

本專案提供一個可設定、可批次執行的瑕疵影像品質評估流程。

對每張輸入影像，程式會計算：

1. MUSIQ
2. NIQE
3. BRISQUE
4. Laplacian Variance

並輸出：

- 每個 metric 的 pass / fail 結果
- 最終 final pass / fail 結果
- 加權後的 final score
- CSV 結果檔
- Excel 結果檔
- 詳細 log 檔

主要的 pass / fail 判斷會根據四個 metric 的 threshold 決定，而 `final_score` 則提供整體品質的輔助參考。
