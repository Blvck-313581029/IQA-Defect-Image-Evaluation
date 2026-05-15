import os
import pandas as pd

from src.utils import collect_image_files, read_image_bgr
from src.metrics.musiq import MUSIQMetric
from src.metrics.niqe import NIQEMetric
from src.metrics.brisque import BRISQUEMetric
from src.metrics.laplacian import calculate_laplacian_variance


class IQAEvaluator:
    def __init__(self, cfg, logger):
        self.cfg = cfg
        self.logger = logger

        self.thresholds = cfg["thresholds"]
        self.weights = cfg["weights"]

        self.output_dir = cfg["output"]["dir"]
        os.makedirs(self.output_dir, exist_ok=True)

        self.logger.info("Loading IQA metrics...")

        self.musiq = MUSIQMetric()
        self.niqe = NIQEMetric(cfg["assets"]["niqe_param_path"])
        self.brisque = BRISQUEMetric(cfg["assets"]["brisque_model_path"])

        self.logger.info("All IQA metrics loaded.")

    def judge_with_thresholds(self, result):
        musiq_pass = result["MUSIQ"] >= self.thresholds["MUSIQ"]
        niqe_pass = result["NIQE"] <= self.thresholds["NIQE"]
        brisque_pass = result["BRISQUE"] <= self.thresholds["BRISQUE"]
        laplacian_pass = (
            result["Laplacian_variance"]
            >= self.thresholds["Laplacian_variance"]
        )

        final_pass = (
            musiq_pass
            and niqe_pass
            and brisque_pass
            and laplacian_pass
        )

        return {
            "MUSIQ_pass": bool(musiq_pass),
            "NIQE_pass": bool(niqe_pass),
            "BRISQUE_pass": bool(brisque_pass),
            "Laplacian_pass": bool(laplacian_pass),
            "final_pass": bool(final_pass),
        }

    def calculate_final_score(self, result):
        eps = 1e-8

        musiq_norm = min(
            result["MUSIQ"] / self.thresholds["MUSIQ"],
            1.0
        )

        laplacian_norm = min(
            result["Laplacian_variance"]
            / self.thresholds["Laplacian_variance"],
            1.0
        )

        niqe_norm = min(
            self.thresholds["NIQE"] / max(result["NIQE"], eps),
            1.0
        )

        brisque_norm = min(
            self.thresholds["BRISQUE"] / max(result["BRISQUE"], eps),
            1.0
        )

        final_score = (
            self.weights["MUSIQ"] * musiq_norm
            + self.weights["NIQE"] * niqe_norm
            + self.weights["BRISQUE"] * brisque_norm
            + self.weights["Laplacian_variance"] * laplacian_norm
        ) * 100

        return {
            "MUSIQ_norm": musiq_norm,
            "NIQE_norm": niqe_norm,
            "BRISQUE_norm": brisque_norm,
            "Laplacian_norm": laplacian_norm,
            "final_score": final_score,
        }

    def evaluate_one_image(self, image_path):
        img_bgr = read_image_bgr(image_path)

        result = {
            "image_name": os.path.basename(image_path),
            "image_path": image_path,
            "MUSIQ": self.musiq.calculate(img_bgr),
            "NIQE": self.niqe.calculate(img_bgr),
            "BRISQUE": self.brisque.calculate(img_bgr),
            "Laplacian_variance": calculate_laplacian_variance(img_bgr),
        }

        pass_result = self.judge_with_thresholds(result)
        score_result = self.calculate_final_score(result)

        output = {
            **result,
            **score_result,
            **pass_result,
        }

        self.logger.info(f"Image: {output['image_name']}")
        self.logger.info(f"  MUSIQ               : {output['MUSIQ']:.4f}, pass={output['MUSIQ_pass']}")
        self.logger.info(f"  NIQE                : {output['NIQE']:.4f}, pass={output['NIQE_pass']}")
        self.logger.info(f"  BRISQUE             : {output['BRISQUE']:.4f}, pass={output['BRISQUE_pass']}")
        self.logger.info(f"  Laplacian Variance  : {output['Laplacian_variance']:.4f}, pass={output['Laplacian_pass']}")
        self.logger.info(f"  Final Score         : {output['final_score']:.4f}")
        self.logger.info(f"  Final Pass          : {output['final_pass']}")

        return output

    def run(self, input_path):
        image_files = collect_image_files(input_path)

        results = []

        for image_path in image_files:
            self.logger.info(f"Processing: {image_path}")
            result = self.evaluate_one_image(image_path)
            results.append(result)

        df = pd.DataFrame(results)

        display_cols = [
            "image_name",
            "MUSIQ",
            "NIQE",
            "BRISQUE",
            "Laplacian_variance",
            "MUSIQ_pass",
            "NIQE_pass",
            "BRISQUE_pass",
            "Laplacian_pass",
            "final_score",
            "final_pass",
            "image_path",
        ]

        df = df[display_cols]

        round_cols = [
            "MUSIQ",
            "NIQE",
            "BRISQUE",
            "Laplacian_variance",
            "final_score",
        ]

        df[round_cols] = df[round_cols].round(4)

        csv_path = os.path.join(self.output_dir, "iqa_results.csv")
        xlsx_path = os.path.join(self.output_dir, "iqa_results.xlsx")

        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        df.to_excel(xlsx_path, index=False)

        self.logger.info(f"CSV saved to : {csv_path}")
        self.logger.info(f"XLSX saved to: {xlsx_path}")

        return df