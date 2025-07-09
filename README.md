# Brain Age Regression

This project uses 3D convolutional neural networks to predict brain age from structural MRI data. The model was trained on the OASIS dataset using a ResNet3D architecture and includes post-hoc bias correction using Target Age Transformation (tAT) to improve accuracy and fairness across age groups.

## Features
- 3D ResNet model trained on full brain MRI volumes  
- Age-weighted loss and stratified sampling to address data imbalance  
- Post-hoc calibration to reduce age-related bias  
- Evaluation on held-out test set with MAE and R² metrics  

## Results
- **MAE (before correction):** 9.28 years  
- **MAE (after tAT correction):** 7.54 years  
- **R² (after correction):** 0.83  

## Paper  
For full methodology, results, and figures, see the project write-up:  
📄 [BrainAgeRegression.pdf](BrainAgeRegression/BrainAgeRegression.pdf)

## Dataset
This project uses publicly available structural MRI scans from the [OASIS dataset](https://www.oasis-brains.org/).

## License
This project is for academic and educational purposes only.
