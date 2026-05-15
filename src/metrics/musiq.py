import cv2
import torch
import pyiqa


class MUSIQMetric:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = pyiqa.create_metric("musiq", device=self.device)

    def calculate(self, img_bgr):
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        img_tensor = (
            torch.from_numpy(img_rgb)
            .permute(2, 0, 1)
            .float()
            .unsqueeze(0)
            / 255.0
        ).to(self.device)

        with torch.no_grad():
            score = self.model(img_tensor)

        return float(score.item())