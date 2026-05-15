# IQA Defect Image Evaluation

This repository provides an image quality evaluation pipeline for defect images.

The goal of this project is to evaluate whether an input image passes basic image quality requirements using multiple no-reference image quality metrics. The current version supports four metrics:

1. MUSIQ
2. NIQE
3. BRISQUE
4. Laplacian Variance

The program supports both single-image input and folder input. It prints the pass/fail result of each metric in the terminal, while detailed metric values are saved into log, CSV, and Excel files.

---

## Repository Structure

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

## Features

- Evaluate image quality using four metrics.
- Support both single image and folder input.
- Configure input path, output path, thresholds, and weights through `config.yaml`.
- Print concise pass/fail results in the terminal.
- Save detailed metric values into a log file.
- Export final results to CSV and Excel files.
- Keep metric implementations separated for easier maintenance.

---

## Installation

Create a Python environment:

```bash
conda create -n iqa_env python=3.10
conda activate iqa_env
```

Install the required packages:

```bash
pip install -r requirements.txt
```

The `requirements.txt` file should contain:

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

## Download Required Assets

This project requires two external model files:

1. NIQE pristine natural image model parameters
2. BRISQUE pretrained SVR model

Download them by running:

```bash
python download_assets.py
```

After downloading, the assets should be placed under:

```bash
assets/
├── niqe_pris_params.npz
└── allmodel
```

These files are required by NIQE and BRISQUE.

---

## Configuration

Most settings are controlled by `config.yaml`.

Example:

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

### Config Field Description

| Field | Description |
|---|---|
| `input.path` | Path to a single image or an image folder |
| `output.dir` | Directory used to save CSV, Excel, and log files |
| `assets.niqe_param_path` | Path to NIQE pristine natural image model parameters |
| `assets.brisque_model_path` | Path to BRISQUE pretrained SVR model |
| `thresholds` | Pass/fail threshold of each metric |
| `weights` | Weights used to calculate the final overview score |

---

## Supported Metrics

### 1. MUSIQ

MUSIQ is a learned no-reference image quality assessment metric.

In this project, MUSIQ is loaded through the `pyiqa` package.

- Higher score means better image quality.
- The image passes MUSIQ if the score is greater than or equal to the MUSIQ threshold.

```text
MUSIQ_pass = MUSIQ >= MUSIQ_threshold
```

---

### 2. NIQE

NIQE is a no-reference image quality metric based on natural scene statistics.

It does not require a distorted reference image. Instead, it compares the statistical features of the input image with a pristine natural image model.

- Lower score means better image quality.
- The image passes NIQE if the score is less than or equal to the NIQE threshold.

```text
NIQE_pass = NIQE <= NIQE_threshold
```

---

### 3. BRISQUE

BRISQUE is also a no-reference image quality metric based on natural scene statistics.

It extracts NSS features from the image and sends them into a pretrained SVR model to predict an image quality score.

- Lower score means better image quality.
- The image passes BRISQUE if the score is less than or equal to the BRISQUE threshold.

```text
BRISQUE_pass = BRISQUE <= BRISQUE_threshold
```

---

### 4. Laplacian Variance

Laplacian Variance is used to estimate image sharpness.

It applies the Laplacian operator to the grayscale image and calculates the variance of the response.

- Higher score usually means the image is sharper.
- Lower score usually means the image is blurrier.
- The image passes Laplacian Variance if the score is greater than or equal to the Laplacian threshold.

```text
Laplacian_pass = Laplacian_variance >= Laplacian_variance_threshold
```

---

## Metric Direction

| Metric | Better Direction | Pass Rule |
|---|---|---|
| MUSIQ | Higher is better | `MUSIQ >= threshold` |
| NIQE | Lower is better | `NIQE <= threshold` |
| BRISQUE | Lower is better | `BRISQUE <= threshold` |
| Laplacian Variance | Higher is better | `Laplacian_variance >= threshold` |

---

## Run the Program

### Run with the default config

```bash
python main.py --config config.yaml
```

### Run on a single image

```bash
python main.py --config config.yaml --input_path ./data/test.jpg
```

### Run on an image folder

```bash
python main.py --config config.yaml --input_path ./data/images
```

### Change output directory

```bash
python main.py --config config.yaml --output_dir ./my_outputs
```

---

## Output Files

After evaluation, the results will be saved in the output directory.

```bash
outputs/
├── iqa_results.csv
├── iqa_results.xlsx
└── logs/
    └── run.log
```

---

## CSV and Excel Output

The CSV and Excel files contain one row for each image.

Example columns:

| Column | Description |
|---|---|
| `image_name` | Image file name |
| `MUSIQ` | MUSIQ score |
| `NIQE` | NIQE score |
| `BRISQUE` | BRISQUE score |
| `Laplacian_variance` | Laplacian Variance score |
| `MUSIQ_pass` | Whether MUSIQ passes |
| `NIQE_pass` | Whether NIQE passes |
| `BRISQUE_pass` | Whether BRISQUE passes |
| `Laplacian_pass` | Whether Laplacian Variance passes |
| `final_score` | Weighted overview score |
| `final_pass` | Whether all four metrics pass |
| `image_path` | Original image path |

---

## Terminal Output

The terminal output only shows a concise pass/fail summary.

Example:

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

The terminal output is intentionally kept simple. Detailed scores are stored in the log file and output tables.

---

## Log Output

The log file stores detailed metric information.

Example:

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

## Final Pass Rule

Each metric has its own threshold.

```text
MUSIQ_pass              = MUSIQ >= MUSIQ_threshold
NIQE_pass               = NIQE <= NIQE_threshold
BRISQUE_pass            = BRISQUE <= BRISQUE_threshold
Laplacian_pass          = Laplacian_variance >= Laplacian_variance_threshold
```

The final pass result is calculated as:

```text
final_pass = MUSIQ_pass
             and NIQE_pass
             and BRISQUE_pass
             and Laplacian_pass
```

Therefore, an image passes only when all four metrics pass.

---

## Final Score

The `final_score` is a weighted overview score from 0 to 100.

It is used as an additional reference, but it does not replace `final_pass`.

The default weights are:

```yaml
weights:
  MUSIQ: 0.25
  NIQE: 0.25
  BRISQUE: 0.25
  Laplacian_variance: 0.25
```

The score is calculated from normalized metric values:

```text
final_score =
    MUSIQ_weight * MUSIQ_norm
  + NIQE_weight * NIQE_norm
  + BRISQUE_weight * BRISQUE_norm
  + Laplacian_weight * Laplacian_norm
```

The normalized values are computed based on the thresholds.

For metrics where higher is better:

```text
score_norm = min(score / threshold, 1.0)
```

For metrics where lower is better:

```text
score_norm = min(threshold / score, 1.0)
```

The final score is mainly used to provide a quick overall quality reference.

---

## Threshold Adjustment

The default thresholds are only initial values.

```yaml
thresholds:
  MUSIQ: 23.0
  NIQE: 8.2
  BRISQUE: 64.0
  Laplacian_variance: 20.0
```

These thresholds should be adjusted after observing the actual score distribution of the target dataset.

A recommended workflow is:

1. Run the evaluation on a batch of images.
2. Check the CSV or Excel output.
3. Compare metric results with human judgment.
4. Adjust thresholds in `config.yaml`.
5. Run the evaluation again.
6. Repeat until the thresholds match the expected quality standard.

For example:

- If many acceptable images fail only because of NIQE, the NIQE threshold may need to be relaxed.
- If blurry images still pass, the Laplacian Variance threshold may need to be increased.
- If MUSIQ scores are generally low for this dataset, the MUSIQ threshold may need to be adjusted.
- If BRISQUE is too strict or too loose, its threshold can also be modified.

---

## Supported Image Formats

The following image formats are supported:

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

## Example Workflow

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download NIQE and BRISQUE assets
python download_assets.py

# 3. Run evaluation on one image
python main.py --config config.yaml --input_path ./data/test.jpg

# 4. Run evaluation on a folder
python main.py --config config.yaml --input_path ./data/images

# 5. Check detailed logs
cat outputs/logs/run.log
```

---

## Design Notes

The project is separated into several parts:

- `main.py` handles command line arguments and starts the evaluation.
- `config.yaml` stores user-adjustable settings.
- `src/evaluator.py` controls the main evaluation process.
- `src/metrics/` contains the implementation of each metric.
- `src/utils.py` handles image loading and file collection.
- `src/logger.py` handles terminal and file logging.
- `outputs/` stores all evaluation results.

This structure keeps the code readable and maintainable. It avoids putting everything into one large script, while also avoiding overly fragmented files.

---

## Summary

This repository provides a configurable image quality assessment pipeline for defect image evaluation.

For each input image, the program calculates:

1. MUSIQ
2. NIQE
3. BRISQUE
4. Laplacian Variance

Then it outputs:

- Pass/fail result for each metric
- Final pass/fail result
- Weighted final score
- CSV result file
- Excel result file
- Detailed log file

The main pass/fail decision is based on the four metric thresholds, while the final score is used only as an additional overview reference.
