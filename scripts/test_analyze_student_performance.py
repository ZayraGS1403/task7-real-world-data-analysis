import unittest
import pandas as pd
import numpy as np
import os
from unittest.mock import patch, MagicMock
from analyze_student_performance import (
    load_data, test_normality, analyze_correlations, save_analysis_summary,
    plot_relationship, plot_distribution, plot_pie_chart
)


class TestAnalyzeStudentPerformance(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({
            'Hours_Studied': [5, 6, 7],
            'Attendance': [90, 85, 95],
            'Sleep_Hours': [7, 8, 6],
            'Previous_Scores': [80, 85, 90],
            'Tutoring_Sessions': [2, 3, 1],
            'Physical_Activity': [3, 2, 4],
            'Exam_Score': [88, 90, 95],
            'Gender': ['Male', 'Female', 'Male'],
            'Parental_Involvement': ['High', 'Low', 'Medium'],
            'Extracurricular_Activities': ['Yes', 'No', 'Yes'],
            'Parental_Education_Level': ['College', 'High School', 'PhD'],
            'Internet_Access': ['Yes', 'No', 'Yes']
        })
        self.temp_output = "test_output"
        os.makedirs(self.temp_output, exist_ok=True)

    def tearDown(self):
        for file in os.listdir(self.temp_output):
            os.remove(os.path.join(self.temp_output, file))
        os.rmdir(self.temp_output)

    def test_load_data_valid(self):
        path = os.path.join(self.temp_output, "mock.csv")
        self.df.to_csv(path, index=False)
        loaded_df = load_data(path)
        self.assertEqual(len(loaded_df), 3)
        self.assertTrue("Exam_Score" in loaded_df.columns)

    def test_load_data_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            load_data("nonexistent.csv")

    def test_test_normality_returns_stat_and_pvalue(self):
        stat, p = test_normality(self.df['Exam_Score'], 'Exam_Score')
        self.assertTrue(0 <= p <= 1)
        self.assertIsInstance(stat, float)

    def test_analyze_correlations(self):
        correlations = analyze_correlations(self.df)
        self.assertIn('Hours_Studied', correlations)
        self.assertIsInstance(correlations['Hours_Studied'], float)

    def test_save_analysis_summary_creates_file(self):
        normality = {
            'Exam_Score': (0.95, 0.08)
        }
        correlations = {
            'Hours_Studied': 0.8
        }
        save_analysis_summary(correlations, normality, self.temp_output)
        summary_path = os.path.join(self.temp_output, 'analysis_summary.txt')
        self.assertTrue(os.path.exists(summary_path))

    @patch("matplotlib.pyplot.savefig")
    def test_plot_distribution_runs(self, mock_save):
        plot_distribution(self.df['Exam_Score'], 'Exam_Score', self.temp_output)
        mock_save.assert_called_once()

    @patch("matplotlib.pyplot.savefig")
    def test_plot_pie_chart_runs(self, mock_save):
        plot_pie_chart(self.df['Gender'], 'Gender', self.temp_output)
        mock_save.assert_called_once()

    @patch("matplotlib.pyplot.savefig")
    def test_plot_relationship_runs_and_returns_correlation(self, mock_save):
        correlation = plot_relationship(self.df, 'Hours_Studied', 'Exam_Score', self.temp_output)
        self.assertIsInstance(correlation, float)
        mock_save.assert_called_once()

    def test_correlation_values_range(self):
        corr = analyze_correlations(self.df)
        for val in corr.values():
            self.assertTrue(-1 <= val <= 1)

    def test_plot_distribution_with_nan(self):
        data = pd.Series([1, 2, np.nan, 4, 5])
        with patch("matplotlib.pyplot.savefig") as mock_save:
            plot_distribution(data.dropna(), 'with_nan', self.temp_output)
            mock_save.assert_called_once()

    def test_plot_relationship_invalid_columns(self):
        df = pd.DataFrame({'A': [1, 2], 'B': ['x', 'y']})
        with self.assertRaises(Exception):
            plot_relationship(df, 'A', 'B', self.temp_output)

    def test_summary_file_content(self):
        correlations = {"Hours_Studied": 0.88}
        normality = {"Exam_Score": (0.9, 0.06)}
        save_analysis_summary(correlations, normality, self.temp_output)
        with open(os.path.join(self.temp_output, 'analysis_summary.txt')) as f:
            content = f.read()
        self.assertIn("Hours_Studied", content)
        self.assertIn("Exam_Score", content)


if __name__ == '__main__':
    unittest.main()
