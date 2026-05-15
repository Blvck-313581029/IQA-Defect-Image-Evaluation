import argparse

from src.config import load_config
from src.logger import setup_logger
from src.evaluator import IQAEvaluator


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to config yaml file"
    )

    parser.add_argument(
        "--input_path",
        type=str,
        default=None,
        help="Override input path in config"
    )

    parser.add_argument(
        "--output_dir",
        type=str,
        default=None,
        help="Override output directory in config"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    cfg = load_config(args.config)

    if args.input_path is not None:
        cfg["input"]["path"] = args.input_path

    if args.output_dir is not None:
        cfg["output"]["dir"] = args.output_dir

    logger = setup_logger(cfg["output"]["dir"])

    evaluator = IQAEvaluator(cfg, logger)
    df = evaluator.run(cfg["input"]["path"])

    print("\n================ IQA Summary ================")

    for _, row in df.iterrows():
        print(f"\nImage: {row['image_name']}")
        print(f"MUSIQ pass              : {row['MUSIQ_pass']}")
        print(f"NIQE pass               : {row['NIQE_pass']}")
        print(f"BRISQUE pass            : {row['BRISQUE_pass']}")
        print(f"Laplacian Variance pass : {row['Laplian_pass'] if 'Laplian_pass' in row else row['Laplacian_pass']}")
        print(f"Final pass              : {row['final_pass']}")

    print("\nDetailed information has been saved to log file.")
    print("=============================================")


if __name__ == "__main__":
    main()