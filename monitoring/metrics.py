import json
import time
from pathlib import Path
from typing import Dict, Any
from collections import defaultdict


class MetricsCollector:
    """Collect and track inference metrics."""

    def __init__(self, metrics_file='metrics/inference_metrics.json'):
        self.metrics_file = metrics_file
        self.metrics = {
            'requests': 0,
            'successful': 0,
            'failed': 0,
            'total_latency': 0,
            'min_latency': float('inf'),
            'max_latency': 0,
            'predictions_by_class': defaultdict(int),
            'confidence_distribution': []
        }
        Path(metrics_file).parent.mkdir(exist_ok=True)

    def record_inference(self, predicted_class: str, confidence: float, latency: float):
        """Record a single inference."""
        self.metrics['requests'] += 1
        self.metrics['successful'] += 1
        self.metrics['total_latency'] += latency
        self.metrics['min_latency'] = min(self.metrics['min_latency'], latency)
        self.metrics['max_latency'] = max(self.metrics['max_latency'], latency)
        self.metrics['predictions_by_class'][predicted_class] += 1
        self.metrics['confidence_distribution'].append(confidence)

    def record_error(self):
        """Record a failed inference."""
        self.metrics['requests'] += 1
        self.metrics['failed'] += 1

    def get_summary(self) -> Dict[str, Any]:
        """Get current metrics summary."""
        avg_latency = (
            self.metrics['total_latency'] / self.metrics['successful']
            if self.metrics['successful'] > 0
            else 0
        )

        avg_confidence = (
            sum(self.metrics['confidence_distribution']) / len(self.metrics['confidence_distribution'])
            if self.metrics['confidence_distribution'] else 0
        )

        return {
            'total_requests': self.metrics['requests'],
            'successful_requests': self.metrics['successful'],
            'failed_requests': self.metrics['failed'],
            'success_rate': (
                self.metrics['successful'] / self.metrics['requests']
                if self.metrics['requests'] > 0 else 0
            ),
            'average_latency_ms': avg_latency * 1000,
            'min_latency_ms': self.metrics['min_latency'] * 1000,
            'max_latency_ms': self.metrics['max_latency'] * 1000,
            'average_confidence': avg_confidence,
            'predictions_by_class': dict(self.metrics['predictions_by_class'])
        }

    def save_metrics(self):
        """Save metrics to file."""
        summary = self.get_summary()
        with open(self.metrics_file, 'w') as f:
            json.dump(summary, f, indent=2)

    def load_metrics(self):
        """Load metrics from file."""
        if Path(self.metrics_file).exists():
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        return {}


class PerformanceMonitor:
    """Monitor model performance post-deployment."""

    def __init__(self, performance_log='logs/performance.json'):
        self.performance_log = performance_log
        Path(performance_log).parent.mkdir(exist_ok=True)
        self.performance_data = {
            'predictions': [],
            'drift_detected': False
        }

    def log_prediction(self, input_hash: str, predicted_class: str,
                      confidence: float, true_label: str = None):
        """Log a prediction with optional true label for drift detection."""
        entry = {
            'timestamp': time.time(),
            'input_hash': input_hash,
            'predicted_class': predicted_class,
            'confidence': confidence,
            'true_label': true_label
        }
        self.performance_data['predictions'].append(entry)

    def check_performance_drift(self, window_size: int = 100) -> Dict[str, Any]:
        """Check for model performance drift."""
        if len(self.performance_data['predictions']) < window_size:
            return {'drift_detected': False, 'reason': 'insufficient_data'}

        recent = self.performance_data['predictions'][-window_size:]
        predictions_with_labels = [
            p for p in recent if p.get('true_label') is not None
        ]

        if not predictions_with_labels:
            return {'drift_detected': False, 'reason': 'no_true_labels'}

        accuracy = sum(
            1 for p in predictions_with_labels
            if p['predicted_class'] == p['true_label']
        ) / len(predictions_with_labels)

        return {
            'drift_detected': accuracy < 0.85,
            'accuracy': accuracy,
            'sample_size': len(predictions_with_labels)
        }

    def save_performance(self):
        """Save performance logs."""
        with open(self.performance_log, 'w') as f:
            json.dump(self.performance_data, f, indent=2)
