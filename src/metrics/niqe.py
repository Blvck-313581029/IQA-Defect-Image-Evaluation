import cv2
import numpy as np
from scipy.special import gamma
from scipy.ndimage import convolve


GAMMA_RANGE = np.arange(0.2, 10.001, 0.001)
PREC_GAMMAS = (
    gamma(2.0 / GAMMA_RANGE) ** 2
    / (gamma(1.0 / GAMMA_RANGE) * gamma(3.0 / GAMMA_RANGE))
)


class NIQEMetric:
    def __init__(self, niqe_param_path):
        params = np.load(niqe_param_path)

        self.mu_pris_param = params["mu_pris_param"]
        self.cov_pris_param = params["cov_pris_param"]
        self.gaussian_window = params["gaussian_window"]

    def estimate_aggd_param(self, block):
        block = block.flatten()

        left_data = block[block < 0]
        right_data = block[block > 0]

        left_std = np.sqrt(np.mean(left_data ** 2)) if len(left_data) > 0 else 0
        right_std = np.sqrt(np.mean(right_data ** 2)) if len(right_data) > 0 else 0

        gammahat = left_std / right_std if right_std != 0 else np.inf

        rhat = (
            np.mean(np.abs(block)) ** 2
            / (np.mean(block ** 2) + 1e-12)
        )

        rhatnorm = (
            rhat
            * (gammahat ** 3 + 1)
            * (gammahat + 1)
            / ((gammahat ** 2 + 1) ** 2 + 1e-12)
        )

        alpha = GAMMA_RANGE[np.argmin((PREC_GAMMAS - rhatnorm) ** 2)]

        beta_l = left_std * np.sqrt(gamma(1.0 / alpha) / gamma(3.0 / alpha))
        beta_r = right_std * np.sqrt(gamma(1.0 / alpha) / gamma(3.0 / alpha))

        return alpha, beta_l, beta_r

    def compute_feature(self, block):
        feat = []

        alpha, beta_l, beta_r = self.estimate_aggd_param(block)
        feat.append(alpha)
        feat.append((beta_l + beta_r) / 2)

        shifts = [
            (0, 1),
            (1, 0),
            (1, 1),
            (1, -1),
        ]

        for shift in shifts:
            shifted_block = np.roll(block, shift, axis=(0, 1))
            pair_product = block * shifted_block

            alpha, beta_l, beta_r = self.estimate_aggd_param(pair_product)

            eta = (
                (beta_r - beta_l)
                * gamma(2.0 / alpha)
                / gamma(1.0 / alpha)
            )

            feat.extend([alpha, eta, beta_l, beta_r])

        return feat

    def calculate_mscn(self, img):
        mu = convolve(img, self.gaussian_window, mode="nearest")
        sigma = np.sqrt(
            np.abs(
                convolve(img ** 2, self.gaussian_window, mode="nearest")
                - mu ** 2
            )
        )

        return (img - mu) / (sigma + 1)

    def calculate(self, img_bgr):
        img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float64)

        block_size_h = 96
        block_size_w = 96

        h, w = img.shape
        num_block_h = h // block_size_h
        num_block_w = w // block_size_w

        if num_block_h == 0 or num_block_w == 0:
            raise ValueError("Image is too small for NIQE block size 96x96.")

        img = img[:num_block_h * block_size_h, :num_block_w * block_size_w]

        distparam = []

        for scale in [1, 2]:
            if scale == 1:
                img_scaled = img
            else:
                img_scaled = cv2.resize(
                    img,
                    (0, 0),
                    fx=1 / scale,
                    fy=1 / scale,
                    interpolation=cv2.INTER_CUBIC
                )

            mscn = self.calculate_mscn(img_scaled)

            cur_block_h = block_size_h // scale
            cur_block_w = block_size_w // scale

            for idx_w in range(num_block_w):
                for idx_h in range(num_block_h):
                    block = mscn[
                        idx_h * cur_block_h:(idx_h + 1) * cur_block_h,
                        idx_w * cur_block_w:(idx_w + 1) * cur_block_w
                    ]

                    feat = self.compute_feature(block)

                    if scale == 1:
                        distparam.append(feat)
                    else:
                        block_index = idx_w * num_block_h + idx_h
                        distparam[block_index].extend(feat)

        distparam = np.array(distparam)

        mu_distparam = np.nanmean(distparam, axis=0)

        valid_distparam = distparam[~np.isnan(distparam).any(axis=1)]
        cov_distparam = np.cov(valid_distparam, rowvar=False)

        invcov_param = np.linalg.pinv(
            (self.cov_pris_param + cov_distparam) / 2
        )

        diff = self.mu_pris_param - mu_distparam
        quality = np.sqrt(np.matmul(np.matmul(diff, invcov_param), diff.T))

        return float(quality)