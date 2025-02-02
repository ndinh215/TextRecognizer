"""Tests for LinePredictor class."""
import os
from pathlib import Path
import unittest
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.training.line_predictor import LinePredictor

SUPPORT_DIRNAME = Path(__file__).parents[0].resolve() / 'support' / 'emnist'

os.environ["CUDA_VISIBLE_DEVICES"] = ""

class TestLinePredictor(unittest.TestCase):
    def test_filename(self):
        predictor = LinePredictor()

        for filename in SUPPORT_DIRNAME.glob('*.png'):
            pred, conf = predictor.predict(str(filename))
            print ('-'*100)
            print(f'Prediction: {pred} at confidence: {conf} for image with character {filename.stem}')
            print ('-'*100)
            self.assertEqual(pred, filename.stem)
            self.assertGreater(conf, 0.7)

if __name__ == '__main__':
    unittest.main()