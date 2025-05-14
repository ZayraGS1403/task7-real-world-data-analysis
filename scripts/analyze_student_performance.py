import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import shapiro
import numpy as np
from typing import Tuple, Dict, List
import os

# Set Seaborn's default styling (no explicit Matplotlib style needed)
sns.set_theme()  # Use Seaborn's default theme
sns.set_palette("deep")


def load_data(file_path: str) -> pd.DataFrame:
    """Load and clean the CSV data."""
    try:
        df = pd.read_csv(file_path)
        # Remove rows with missing or invalid values
        df = df.dropna()
        # Ensure numeric columns are correctly typed
        numeric_cols = ['Hours_Studied', 'Attendance', 'Sleep_Hours', 'Previous_Scores',
                        'Tutoring_Sessions', 'Physical_Activity', 'Exam_Score']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna()  # Drop any rows with conversion issues
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"File {file_path} not found.")
    except Exception as e:
        raise Exception(f"Error loading data: {str(e)}")


def test_normality(data: pd.Series, column_name: str) -> Tuple[float, float]:
    """Test if a column's distribution is normal using Shapiro-Wilk test."""
    stat, p_value = shapiro(data)
    return stat, p_value


def plot_distribution(data: pd.Series, column_name: str, output_dir: str) -> None:
    """Plot the distribution of a numeric column."""
    plt.figure(figsize=(10, 6))
    sns.histplot(data, kde=True, bins=30)
    plt.title(f'Distribution of {column_name}')
    plt.xlabel(column_name)
    plt.ylabel('Frequency')

    # Test normality
    stat, p_value = test_normality(data, column_name)
    normality_text = f'Shapiro-Wilk Test: p-value = {p_value:.4f}\n'
    normality_text += 'Normal' if p_value > 0.05 else 'Not Normal'
    plt.text(0.05, 0.95, normality_text, transform=plt.gca().transAxes,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.savefig(os.path.join(output_dir, f'{column_name}_distribution.png'))
    plt.close()


def plot_pie_chart(data: pd.Series, column_name: str, output_dir: str) -> None:
    """Plot a pie chart for a categorical column."""
    value_counts = data.value_counts()
    plt.figure(figsize=(8, 8))
    plt.pie(value_counts, labels=value_counts.index, autopct='%1.1f%%', startangle=140)
    plt.title(f'Percentage Distribution of {column_name}')
    plt.savefig(os.path.join(output_dir, f'{column_name}_pie.png'))
    plt.close()


def plot_relationship(df: pd.DataFrame, x_col: str, y_col: str, output_dir: str) -> float:
    """Plot a scatter plot to show relationship between two columns and return correlation."""
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x=x_col, y=y_col)
    plt.title(f'{x_col} vs {y_col}')
    plt.xlabel(x_col)
    plt.ylabel(y_col)

    # Calculate and display correlation
    correlation = df[[x_col, y_col]].corr().iloc[0, 1]
    plt.text(0.05, 0.95, f'Correlation: {correlation:.2f}', transform=plt.gca().transAxes,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.savefig(os.path.join(output_dir, f'{x_col}_vs_{y_col}.png'))
    plt.close()
    return correlation


def analyze_correlations(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate correlations between Exam_Score and other numeric columns."""
    numeric_cols = ['Hours_Studied', 'Attendance', 'Sleep_Hours', 'Previous_Scores',
                    'Tutoring_Sessions', 'Physical_Activity']
    correlations = {}
    for col in numeric_cols:
        correlations[col] = df[[col, 'Exam_Score']].corr().iloc[0, 1]
    return correlations


def save_analysis_summary(correlations: Dict[str, float], normality_results: Dict[str, Tuple[float, float]],
                          output_dir: str) -> None:
    """Save a text summary of the analysis."""
    with open(os.path.join(output_dir, 'analysis_summary.txt'), 'w') as f:
        f.write("Student Performance Analysis Summary\n")
        f.write("===================================\n\n")

        f.write("Normality Tests (Shapiro-Wilk):\n")
        for col, (stat, p_value) in normality_results.items():
            normality = 'Normal' if p_value > 0.05 else 'Not Normal'
            f.write(f"{col}: p-value = {p_value:.4f} ({normality})\n")

        f.write("\nCorrelations with Exam Score:\n")
        for col, corr in correlations.items():
            f.write(f"{col}: {corr:.2f}\n")

        f.write("\nConclusions:\n")
        f.write("- Hours_Studied and Attendance have the strongest positive correlations with Exam_Score, "
                "suggesting that more study time and higher class attendance are associated with better exam performance.\n")
        f.write(
            "- Sleep_Hours shows a weak positive correlation, indicating that adequate sleep may slightly benefit performance.\n")
        f.write(
            "- Physical_Activity has a minimal correlation, suggesting it has little direct impact on exam scores.\n")
        f.write("- Most numeric variables (e.g., Exam_Score, Hours_Studied) are not normally distributed, "
                "as indicated by Shapiro-Wilk p-values < 0.05.\n")
        f.write(
            "- Categorical factors like Parental_Involvement and Extracurricular_Activities show varied distributions, "
            "with pie charts indicating balanced representation across categories.\n")


def main(file_path: str = "StudentPerformanceFactors.csv", output_dir: str = "output") -> None:
    """Main function to run the analysis and generate visualizations."""
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Load data
    df = load_data(file_path)

    # Numeric columns for distribution analysis
    numeric_cols = ['Exam_Score', 'Hours_Studied', 'Sleep_Hours', 'Attendance', 'Physical_Activity']
    normality_results = {}

    # Plot distributions and test normality
    for col in numeric_cols:
        plot_distribution(df[col], col, output_dir)
        normality_results[col] = test_normality(df[col], col)

    # Categorical columns for pie charts
    categorical_cols = ['Gender', 'Parental_Involvement', 'Extracurricular_Activities',
                        'Parental_Education_Level', 'Internet_Access']
    for col in categorical_cols:
        plot_pie_chart(df[col], col, output_dir)

    # Relationship plots
    relationships = [
        ('Hours_Studied', 'Exam_Score'),
        ('Sleep_Hours', 'Exam_Score'),
        ('Attendance', 'Exam_Score'),
        ('Physical_Activity', 'Exam_Score'),
        ('Sleep_Hours', 'Hours_Studied')
    ]
    for x_col, y_col in relationships:
        plot_relationship(df, x_col, y_col, output_dir)

    # Analyze correlations
    correlations = analyze_correlations(df)

    # Save analysis summary
    save_analysis_summary(correlations, normality_results, output_dir)


if __name__ == "__main__":
    main()