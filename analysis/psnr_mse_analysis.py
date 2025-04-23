import os
import csv
from utils import metrics

def analyze(original_image_path, stego_image_paths, results_dir):
    psnr_results = []
    mse_results = []

    for method, stego_path in stego_image_paths.items():
        psnr = metrics.calculate_psnr(original_image_path, stego_path)
        mse = metrics.calculate_mse(original_image_path, stego_path)
        psnr_results.append({'Method': method, 'PSNR': psnr})
        mse_results.append({'Method': method, 'MSE': mse})

    # Save results to CSV
    os.makedirs(results_dir, exist_ok=True)
    with open(os.path.join(results_dir, 'psnr_results.csv'), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Method', 'PSNR'])
        writer.writeheader()
        writer.writerows(psnr_results)

    with open(os.path.join(results_dir, 'mse_results.csv'), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Method', 'MSE'])
        writer.writeheader()
        writer.writerows(mse_results)
