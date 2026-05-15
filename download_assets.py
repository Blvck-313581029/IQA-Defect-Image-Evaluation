import os
import urllib.request


ASSETS = {
    "niqe_pris_params.npz": (
        "https://raw.githubusercontent.com/XPixelGroup/BasicSR/master/"
        "basicsr/metrics/niqe_pris_params.npz"
    ),
    "allmodel": (
        "https://raw.githubusercontent.com/spmallick/learnopencv/master/"
        "ImageMetrics/Python/allmodel"
    ),
}


def main():
    os.makedirs("assets", exist_ok=True)

    for filename, url in ASSETS.items():
        save_path = os.path.join("assets", filename)

        if os.path.exists(save_path):
            print(f"[SKIP] {save_path} already exists")
            continue

        print(f"[DOWNLOAD] {filename}")
        urllib.request.urlretrieve(url, save_path)
        print(f"[OK] saved to {save_path}")


if __name__ == "__main__":
    main()