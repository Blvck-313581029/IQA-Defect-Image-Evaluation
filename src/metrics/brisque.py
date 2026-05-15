import cv2
import numpy as np
from scipy.special import gamma
from libsvm.svmutil import svm_load_model, svm_predict


GAMMA_RANGE = np.arange(0.2, 10.001, 0.001)
PREC_GAMMAS = (
    gamma(2.0 / GAMMA_RANGE) ** 2
    / (gamma(1.0 / GAMMA_RANGE) * gamma(3.0 / GAMMA_RANGE))
)


BRISQUE_FEATURE_MIN = np.array([
    0.336999, 0.019667, 0.230000, -0.125959, 0.000167, 0.000616,
    0.231000, -0.125873, 0.000165, 0.000600, 0.241000, -0.128814,
    0.000179, 0.000386, 0.243000, -0.133080, 0.000182, 0.000421,
    0.436998, 0.016929, 0.247000, -0.200231, 0.000104, 0.000834,
    0.257000, -0.200017, 0.000112, 0.000876, 0.257000, -0.155072,
    0.000112, 0.000356, 0.258000, -0.154374, 0.000117, 0.000351
])

BRISQUE_FEATURE_MAX = np.array([
    9.999411, 0.807472, 1.644021, 0.202917, 0.712384, 0.468672,
    1.644021, 0.169548, 0.713132, 0.467896, 1.553016, 0.101368,
    0.687324, 0.533087, 1.554016, 0.101000, 0.689177, 0.533133,
    3.639918, 0.800955, 1.096995, 0.175286, 0.755547, 0.399270,
    1.095995, 0.155928, 0.751488, 0.402398, 1.041992, 0.093209,
    0.623516, 0.532925, 1.042992, 0.093714, 0.621958, 0.534484
])


class BRISQUEMetric:
    def __init__(self, model_path):
        self.model = svm_load_model(model_path)

    def aggd_fit(self, structdis):
        structdis = structdis.flatten()

        left_data = structdis[structdis < 0]
        right_data = structdis[structdis > 0]

        left_std = np.sqrt(np.mean(left_data ** 2)) if len(left_data) > 0 else 0
        right_std = np.sqrt(np.mean(right_data ** 2)) if len(right_data) > 0 else 0

        gammahat = left_std / right_std if right_std != 0 else np.inf

        rhat = (
            np.mean(np.abs(structdis)) ** 2
            / (np.mean(structdis ** 2) + 1e-12)
        )

        rhatnorm = (
            rhat
            * (gammahat ** 3 + 1)
            * (gammahat + 1)
            / ((gammahat ** 2 + 1) ** 2 + 1e-12)
        )

        alpha = GAMMA_RANGE[np.argmin((PREC_GAMMAS - rhatnorm) ** 2)]

        return alpha, left_std, right_std

    def compute_features(self, gray_img):
        feat = []
        im_original = gray_img.copy().astype(np.float64)

        for _ in range(2):
            im = im_original / 255.0

            mu = cv2.GaussianBlur(im, (7, 7), 1.166)
            mu_sq = mu * mu

            sigma = cv2.GaussianBlur(im * im, (7, 7), 1.166)
            sigma = np.sqrt(np.abs(sigma - mu_sq))

            structdis = (im - mu) / (sigma + 1.0 / 255)

            alpha, left_std, right_std = self.aggd_fit(structdis)

            feat.append(alpha)
            feat.append((left_std ** 2 + right_std ** 2) / 2)

            shifts = [
                (0, 1),
                (1, 0),
                (1, 1),
                (-1, 1),
            ]

            for shift in shifts:
                shifted = np.roll(structdis, shift, axis=(0, 1))
                pair_product = structdis * shifted

                alpha, left_std, right_std = self.aggd_fit(pair_product)

                constant = np.sqrt(gamma(1.0 / alpha) / gamma(3.0 / alpha))

                mean_param = (
                    (right_std - left_std)
                    * gamma(2.0 / alpha)
                    / gamma(1.0 / alpha)
                    * constant
                )

                feat.append(alpha)
                feat.append(mean_param)
                feat.append(left_std ** 2)
                feat.append(right_std ** 2)

            im_original = cv2.resize(
                im_original,
                (0, 0),
                fx=0.5,
                fy=0.5,
                interpolation=cv2.INTER_CUBIC
            )

        return np.array(feat, dtype=np.float64)

    def calculate(self, img_bgr):
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        features = self.compute_features(gray)

        scaled_features = -1 + 2.0 * (
            (features - BRISQUE_FEATURE_MIN)
            / (BRISQUE_FEATURE_MAX - BRISQUE_FEATURE_MIN)
        )

        pred, _, _ = svm_predict(
            [0],
            [scaled_features.tolist()],
            self.model,
            options="-q"
        )

        return float(pred[0])