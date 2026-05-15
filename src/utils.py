from pathlib import Path
import cv2


IMG_EXTS = {
    ".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"
}


def collect_image_files(input_path):
    input_path = Path(input_path)

    if input_path.is_file():
        if input_path.suffix.lower() not in IMG_EXTS:
            raise ValueError(f"Unsupported image format: {input_path}")
        return [str(input_path)]

    if input_path.is_dir():
        image_files = [
            str(p)
            for p in sorted(input_path.iterdir())
            if p.is_file() and p.suffix.lower() in IMG_EXTS
        ]

        if len(image_files) == 0:
            raise FileNotFoundError(f"No image files found in: {input_path}")

        return image_files

    raise FileNotFoundError(f"Input path not found: {input_path}")


def read_image_bgr(image_path):
    img_bgr = cv2.imread(image_path, cv2.IMREAD_COLOR)

    if img_bgr is None:
        raise ValueError(f"Failed to read image: {image_path}")

    return img_bgr