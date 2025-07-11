# -*- coding: utf-8 -*-
"""eval_utils.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1NsTfTudsNoV0p_1UBHXfOf3X9O-VbftD

# 1.) Imports
"""

import torch
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression

class BrainAgeEvaluator:
    def __init__(self, model, device, metadata_df=None):
        self.model = model.to(device)
        self.device = device
        self.metadata = metadata_df.reset_index(drop=True) if metadata_df is not None else None

    # Core Evaluation
    def evaluate(self, dataloader, criterion=None):
        self.model.eval()
        total_loss = 0.0
        preds, targets = [], []

        with torch.no_grad():
            for images, ages in dataloader:
                images, ages = images.to(self.device), ages.to(self.device)
                outputs = self.model(images)

                if criterion:
                    loss = criterion(outputs, ages)
                    total_loss += loss.item() * images.size(0)

                preds.extend(outputs.cpu().numpy().reshape(-1))
                targets.extend(ages.cpu().numpy().reshape(-1))

        metrics = self.compute_metrics(targets, preds)
        if criterion:
            metrics['mse'] = total_loss / len(dataloader.dataset)
            metrics['rmse'] = np.sqrt(metrics['mse'])

        return metrics, preds, targets

    def compute_metrics(self, y_true, y_pred):
        return {
            'mae': mean_absolute_error(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'r2': r2_score(y_true, y_pred)
        }

    # Post-Hoc Bias Correction
    def apply_posthoc_bias_correction(self, y_true, y_pred, return_model=False):
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        residuals = y_pred - y_true

        bias_model = LinearRegression().fit(y_true.reshape(-1, 1), residuals)
        predicted_bias = bias_model.predict(y_true.reshape(-1, 1))
        corrected_pred = y_pred - predicted_bias

        metrics = self.compute_metrics(y_true, corrected_pred)

        if return_model:
            return corrected_pred, metrics, bias_model
        return corrected_pred, metrics

    # Visualization
    def plot_predictions(self, y_true, y_pred, title="Predicted vs. True Age", color='blue'):
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.scatter(y_true, y_pred, alpha=0.6, color=color)
        min_age = min(min(y_true), min(y_pred))
        max_age = max(max(y_true), max(y_pred))
        ax.plot([min_age, max_age], [min_age, max_age], 'k--')
        ax.set_xlabel("True Age")
        ax.set_ylabel("Predicted Age")
        ax.set_title(title)
        ax.grid(True)
        fig.tight_layout()
        return fig


    def plot_prediction_distribution(self, y_pred, bins=20):
        fig, ax = plt.subplots()
        ax.hist(y_pred, bins=bins, color='skyblue', edgecolor='black')
        ax.set_title("Distribution of Predicted Ages")
        ax.set_xlabel("Predicted Age")
        ax.set_ylabel("Count")
        ax.grid(True)
        fig.tight_layout()
        return fig

    def plot_residuals(self, y_true, y_pred):
        fig, ax = plt.subplots()
        ax.scatter(y_true, np.array(y_pred) - np.array(y_true), alpha=0.6)
        ax.axhline(0, color='red', linestyle='--')
        ax.set_xlabel("True Age")
        ax.set_ylabel("Residual (Predicted - True)")
        ax.set_title("Residuals")
        ax.grid(True)
        fig.tight_layout()
        return fig

    def plot_prediction_bias(self, y_true, y_pred, bins=10, method='qcut'):
        df = pd.DataFrame({'true': y_true, 'pred': y_pred})
        df['error'] = df['pred'] - df['true']
        df['age_bin'] = self.get_age_bins(df['true'], bins=bins, method=method)

        bias = df.groupby('age_bin')['error'].mean().reset_index()

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(bias['age_bin'].astype(str), bias['error'], color='salmon')
        ax.axhline(0, color='black', linestyle='--')
        ax.set_xticklabels(bias['age_bin'].astype(str), rotation=45, ha='right')
        ax.set_ylabel("Mean Prediction Error")
        ax.set_title("🎯 Prediction Bias by Age Bin")
        ax.grid(axis='y')
        fig.tight_layout()
        return fig

    def stratified_mae(self, y_true, y_pred, bins=10, method='qcut'):
        df = pd.DataFrame({'true': y_true, 'pred': y_pred})
        df['age_bin'] = self.get_age_bins(df['true'], bins=bins, method=method)

        stratified = df.groupby('age_bin').apply(lambda g: mean_absolute_error(g['true'], g['pred']))
        stratified = stratified.reset_index()
        stratified.columns = ['Age Group', 'MAE']

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(stratified['Age Group'].astype(str), stratified['MAE'], color='skyblue')
        ax.set_xticklabels(stratified['Age Group'].astype(str), rotation=45, ha='right')
        ax.set_ylabel("MAE (years)")
        ax.set_title("📊 Stratified MAE by Age Group")
        ax.grid(axis='y')
        fig.tight_layout()
        return fig

    def get_age_bins(self, y_true, bins=10, method='qcut'):
        if method == 'qcut':
            return pd.qcut(y_true, q=bins, duplicates='drop')
        elif method == 'cut':
            return pd.cut(y_true, bins=bins)

    # Save Predictions
    def save_predictions(self, save_path, **kwargs):
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        np.savez(save_path, **kwargs)
        print(f"✅ Saved predictions to {save_path}")