import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import os
from datetime import datetime

class SimulationAnalyzer:
    def __init__(self, excel_path):
        """
        Initialize the analyzer with the path to the simulation results Excel file.
        
        Args:
            excel_path: Path to the Excel file containing simulation results
        """
        self.excel_path = excel_path
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = "analysis_output2"
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        # Load data from Excel file
        self.load_data()
        
    def load_data(self):
        """Load all sheets from the Excel file into DataFrames."""
        # Read all sheets
        print(f"Loading data from {self.excel_path}...")
        
        # Load simulation statistics
        self.simulation_stats = pd.read_excel(self.excel_path, sheet_name='Simulation_Stats')
        
        # Load strategies
        self.strategies_df = pd.read_excel(self.excel_path, sheet_name='Strategies')
        
        # Load raw results
        self.raw_results = pd.read_excel(self.excel_path, sheet_name='Raw_Results')
        
        # Load average scores
        self.avg_scores = pd.read_excel(self.excel_path, sheet_name='Average_Scores')
        
        # Load best configurations per strategy
        self.best_configs = pd.read_excel(self.excel_path, sheet_name='Best_Configs_Per_Strategy')
        
        print("Data loaded successfully!")
    
    def analyze_overall_best_configurations(self, top_n=10):
        """
        Find the overall best configurations based on average score and standard deviation.
        
        Args:
            top_n: Number of top configurations to return
        
        Returns:
            DataFrame with top configurations
        """
        # Get all score columns
        score_cols = [col for col in self.avg_scores.columns if col.startswith('score_strategy_')]
        
        # Calculate average score and standard deviation across all strategies
        self.avg_scores['overall_avg_score'] = self.avg_scores[score_cols].mean(axis=1)
        self.avg_scores['overall_std_score'] = self.avg_scores[score_cols].std(axis=1)
        
        # Calculate a composite metric: higher average and lower std is better
        self.avg_scores['composite_score'] = self.avg_scores['overall_avg_score'] / (1 + self.avg_scores['overall_std_score'])
        
        # Sort by composite score in descending order
        sorted_configs = self.avg_scores.sort_values('composite_score', ascending=False)
        
        return sorted_configs[['configuration_id', 'overall_avg_score', 'overall_std_score', 'composite_score']].head(top_n)
    
    def analyze_strategy_performance(self):
        """
        Analyze which strategies perform best across configurations.
        
        Returns:
            DataFrame with strategy performance metrics
        """
        # Get all score columns
        score_cols = [col for col in self.avg_scores.columns if col.startswith('score_strategy_')]
        
        # Calculate average, min, max, and std for each strategy across all configurations
        strategy_performance = pd.DataFrame({
            'strategy_id': range(len(score_cols)),
            'avg_score': [self.avg_scores[col].mean() for col in score_cols],
            'min_score': [self.avg_scores[col].min() for col in score_cols],
            'max_score': [self.avg_scores[col].max() for col in score_cols],
            'std_score': [self.avg_scores[col].std() for col in score_cols]
        })
        
        # Merge with strategy weights
        strategy_performance = pd.merge(
            strategy_performance, 
            self.strategies_df[['intensive_weight', 'intermediate_weight', 'distance_weight']],
            left_on='strategy_id', right_index=True
        )
        
        return strategy_performance.sort_values('avg_score', ascending=False)
    
    def find_robust_configurations(self, top_n=10):
        """
        Find configurations that perform consistently well across all strategies.
        
        Args:
            top_n: Number of top configurations to return
            
        Returns:
            DataFrame with robust configurations
        """
        # Get all score columns
        score_cols = [col for col in self.avg_scores.columns if col.startswith('score_strategy_')]
        
        # Calculate the minimum score for each configuration across all strategies
        self.avg_scores['min_strategy_score'] = self.avg_scores[score_cols].min(axis=1)
        
        # Sort by minimum score (highest min score is most robust)
        robust_configs = self.avg_scores.sort_values('min_strategy_score', ascending=False)
        
        return robust_configs[['configuration_id', 'min_strategy_score'] + score_cols].head(top_n)
    
    def create_strategy_weight_comparison_chart(self, output_path=None):
        """
        Create a chart comparing strategy weights and their performance.
        
        Args:
            output_path: Path to save the chart, if None, a default path is used
            
        Returns:
            Path to the saved chart
        """
        if output_path is None:
            output_path = f"{self.output_dir}/strategy_weight_comparison_{self.timestamp}.pdf"
        
        # Get strategy performance
        strategy_perf = self.analyze_strategy_performance()
        
        with PdfPages(output_path) as pdf:
            # Plot weight distribution vs average score
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Create scatter plot with size based on avg_score
            scatter = ax.scatter(
                strategy_perf['distance_weight'], 
                strategy_perf['intensive_weight'],
                s=strategy_perf['avg_score'] * 500,  # Scale point size
                c=strategy_perf['avg_score'],  # Color by average score
                cmap='viridis',
                alpha=0.7
            )
            
            # Add colorbar
            cbar = plt.colorbar(scatter)
            cbar.set_label('Average Score', fontsize=12)
            
            # Add text annotation for intermediate weight (which is 1 - intensive - distance)
            for i, row in strategy_perf.iterrows():
                ax.annotate(
                    f"{row['intermediate_weight']:.1f}",
                    (row['distance_weight'], row['intensive_weight']),
                    fontsize=9
                )
            
            # Set labels and title
            ax.set_xlabel('Distance Weight', fontsize=14)
            ax.set_ylabel('Intensive Weight', fontsize=14)
            ax.set_title('Strategy Weight Distribution vs Performance', fontsize=16)
            
            # Add legend for point size
            sizes = [0.3, 0.4, 0.5, 0.6]
            labels = [f"{s:.1f}" for s in sizes]
            legend_points = [plt.Line2D([0], [0], marker='o', color='w', 
                             markerfacecolor='gray', markersize=np.sqrt(s*500)/2) 
                             for s in sizes]
            ax.legend(legend_points, labels, title="Score", loc='upper right', title_fontsize=12)
            
            pdf.savefig(fig)
            plt.close()
            
            # Create a second chart - strategies ranked by performance
            top_strategies = strategy_perf.head(10)
            
            fig, ax = plt.subplots(figsize=(12, 8))
            bars = ax.bar(
                range(len(top_strategies)),
                top_strategies['avg_score'],
                yerr=top_strategies['std_score'],
                capsize=5
            )
            
            # Add weight labels to each bar
            for i, (_, row) in enumerate(top_strategies.iterrows()):
                ax.text(
                    i, row['avg_score'] + 0.01,
                    f"I:{row['intensive_weight']:.1f}, M:{row['intermediate_weight']:.1f}, D:{row['distance_weight']:.1f}",
                    ha='center', va='bottom', rotation=90, fontsize=9
                )
            
            # Set labels and title
            ax.set_xlabel('Strategy ID', fontsize=14)
            ax.set_ylabel('Average Score', fontsize=14)
            ax.set_title('Top 10 Strategies by Average Performance', fontsize=16)
            ax.set_xticks(range(len(top_strategies)))
            ax.set_xticklabels(top_strategies['strategy_id'])
            
            pdf.savefig(fig)
            plt.close()
            
        return output_path
    
    def create_configuration_performance_report(self, output_path=None):
        """
        Create a report showing performance of top configurations.
        
        Args:
            output_path: Path to save the report, if None, a default path is used
            
        Returns:
            Path to the saved report
        """
        if output_path is None:
            output_path = f"{self.output_dir}/configuration_performance_{self.timestamp}.pdf"
        
        best_overall = self.analyze_overall_best_configurations(top_n=10)
        best_robust = self.find_robust_configurations(top_n=10)
        
        with PdfPages(output_path) as pdf:
            # Plot top configurations by composite score
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Adjust y-axis to start from 0.85 (or minimum score - 0.05) to better show differences
            min_score = min(best_overall['overall_avg_score']) - 0.05
            max_score = max(best_overall['overall_avg_score']) + 0.05
            
            bars = ax.bar(
                range(len(best_overall)),
                best_overall['overall_avg_score'],
                yerr=best_overall['overall_std_score'],
                capsize=5
            )
            
            # Add configuration IDs inside the bars
            for i, (_, row) in enumerate(best_overall.iterrows()):
                # Center the text in the bar
                ax.text(
                    i, (min_score + row['overall_avg_score']) / 2,
                    f"Config\n{int(row['configuration_id'])}",
                    ha='center', va='center', 
                    color='white', 
                    fontweight='bold', 
                    fontsize=10
                )
                # Add score value above the bar
                ax.text(
                    i, row['overall_avg_score'] + 0.01,
                    f"{row['overall_avg_score']:.3f}",
                    ha='center', va='bottom',
                    color='black',
                    fontsize=9
                )
            
            ax.set_ylim(min_score, max_score)
            ax.set_xlabel('Rank', fontsize=14)
            ax.set_ylabel('Average Score Across All Strategies', fontsize=14)
            ax.set_title('Top 10 Configurations by Overall Performance', fontsize=16)
            
            # Add note about composite score
            ax.text(
                0.5, -0.15,
                "Note: Configurations ranked by composite score (average ÷ (1 + std.dev))",
                ha='center', va='center', transform=ax.transAxes, fontsize=10, style='italic'
            )
            
            pdf.savefig(fig)
            plt.close()
            
            # Plot most robust configurations with similar improvements
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Adjust y-axis for robust configurations
            min_score = min(best_robust['min_strategy_score']) - 0.05
            max_score = max(best_robust['min_strategy_score']) + 0.05
            
            bars = ax.bar(
                range(len(best_robust)),
                best_robust['min_strategy_score']
            )
            
            # Add configuration IDs and scores
            for i, (_, row) in enumerate(best_robust.iterrows()):
                # Center the text in the bar
                ax.text(
                    i, (min_score + row['min_strategy_score']) / 2,
                    f"Config\n{int(row['configuration_id'])}",
                    ha='center', va='center',
                    color='white',
                    fontweight='bold',
                    fontsize=10
                )
                # Add score value above the bar
                ax.text(
                    i, row['min_strategy_score'] + 0.01,
                    f"{row['min_strategy_score']:.3f}",
                    ha='center', va='bottom',
                    color='black',
                    fontsize=9
                )
            
            ax.set_ylim(min_score, max_score)
            ax.set_xlabel('Rank', fontsize=14)
            ax.set_ylabel('Minimum Score Across All Strategies', fontsize=14)
            ax.set_title('Top 10 Most Robust Configurations', fontsize=16)
            
            # Add note about robustness
            ax.text(
                0.5, -0.15,
                "Note: Robustness measures how well a configuration performs across all assignment strategies",
                ha='center', va='center', transform=ax.transAxes, fontsize=10, style='italic'
            )
            
            pdf.savefig(fig)
            plt.close()
        
        return output_path
    
    def create_strategy_configuration_heatmap(self, output_path=None):
        """
        Create a heatmap showing how strategies perform across different configurations.
        
        Args:
            output_path: Path to save the heatmap, if None, a default path is used
            
        Returns:
            Path to the saved heatmap
        """
        if output_path is None:
            output_path = f"{self.output_dir}/strategy_configuration_heatmap_{self.timestamp}.pdf"
        
        score_cols = [col for col in self.avg_scores.columns if col.startswith('score_strategy_')]
        top_configs = self.analyze_overall_best_configurations(top_n=20)
        filtered_scores = self.avg_scores[self.avg_scores['configuration_id'].isin(top_configs['configuration_id'])]
        heatmap_data = filtered_scores[score_cols].values
        
        with PdfPages(output_path) as pdf:
            fig, ax = plt.subplots(figsize=(14, 10))
            
            # Create the heatmap with improved visibility
            sns.heatmap(
                heatmap_data,
                annot=True,
                fmt=".3f",
                cmap="YlGnBu",
                xticklabels=[f"S{i}" for i in range(len(score_cols))],
                yticklabels=[f"Config {int(cid)}" for cid in filtered_scores['configuration_id']],
                ax=ax,
                annot_kws={'size': 8},  # Adjust annotation size
                cbar_kws={'label': 'Score'}  # Add colorbar label
            )
            
            # Rotate x-axis labels for better readability
            plt.xticks(rotation=0)
            # Rotate y-axis labels for better readability
            plt.yticks(rotation=0)
            
            # Make the axis labels more visible
            ax.set_xlabel('Strategy ID', fontsize=14, labelpad=10)
            ax.set_ylabel('Configuration ID', fontsize=14, labelpad=10)
            ax.set_title('Performance Heatmap: Top Configurations vs. Strategies', fontsize=16, pad=20)
            
            # Adjust layout to prevent label cutoff
            plt.tight_layout()
            
            pdf.savefig(fig)
            plt.close()
        
        return output_path
    
    def export_summary_report(self, output_path=None):
        """
        Export a comprehensive Excel report with all analyses.
        
        Args:
            output_path: Path to save the report, if None, a default path is used
            
        Returns:
            Path to the saved report
        """
        if output_path is None:
            output_path = f"{self.output_dir}/summary_report_{self.timestamp}.xlsx"
        
        # Gather all analysis results - without rounding
        best_overall = self.analyze_overall_best_configurations(top_n=20)
        best_robust = self.find_robust_configurations(top_n=20)
        strategy_performance = self.analyze_strategy_performance()
        
        # Get detailed information about the top 5 configurations
        top_5_configs = best_overall['configuration_id'].head(5).tolist()
        top_config_details = self.raw_results[self.raw_results['configuration_id'].isin(top_5_configs)]
        
        # Export to Excel with float_format=None to preserve full precision
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Write overall statistics
            self.simulation_stats.to_excel(writer, sheet_name='Simulation_Summary', index=False)
            
            # Write best configurations without rounding
            best_overall.to_excel(writer, sheet_name='Best_Overall_Configs', index=False)
            best_robust.to_excel(writer, sheet_name='Most_Robust_Configs', index=False)
            
            # Write strategy performance without rounding
            strategy_performance.to_excel(writer, sheet_name='Strategy_Performance', index=False)
            
            # Write top config details without rounding
            for config_id in top_5_configs:
                config_data = top_config_details[top_config_details['configuration_id'] == config_id]
                config_data.to_excel(writer, sheet_name=f'Config_{int(config_id)}_Details', index=False)
            
            # Write recommendations
            recommendations = pd.DataFrame({
                'Category': [
                    'Overall Best Configuration',
                    'Most Robust Configuration',
                    'Best Strategy',
                    'Balanced Strategy',
                    'Notes'
                ],
                'Recommendation': [
                    f"Configuration {int(best_overall['configuration_id'].iloc[0])}",
                    f"Configuration {int(best_robust['configuration_id'].iloc[0])}",
                    f"Strategy {strategy_performance['strategy_id'].iloc[0]} (I:{strategy_performance['intensive_weight'].iloc[0]}, M:{strategy_performance['intermediate_weight'].iloc[0]}, D:{strategy_performance['distance_weight'].iloc[0]})",
                    "For balanced performance, consider using a robust configuration with a strategy that balances distance and occupancy weights",
                    "The top 5 configurations have been detailed in separate sheets for in-depth review"
                ]
            })
            recommendations.to_excel(writer, sheet_name='Recommendations', index=False)
        
        return output_path
    
    def analyze_capacity_impact(self):
        """
        Analyze how different capacity configurations impact performance.
        
        Returns:
            DataFrame with capacity impact analysis
        """
        # Extract capacity parameters from configuration details
        # This assumes capacity parameters are available in the raw_results
        capacity_cols = [col for col in self.raw_results.columns if 'capacity' in col.lower()]
        
        if not capacity_cols:
            print("Warning: No capacity columns found in the data")
            return pd.DataFrame()
        
        # Group by capacity parameters and calculate average scores
        capacity_impact = self.raw_results.groupby(capacity_cols).agg({
            'score': ['mean', 'std', 'min', 'max', 'count']
        }).reset_index()
        
        # Flatten the multi-index columns
        capacity_impact.columns = ['_'.join(col).strip('_') for col in capacity_impact.columns.values]
        
        # Sort by mean score (descending)
        capacity_impact = capacity_impact.sort_values('score_mean', ascending=False)
        
        return capacity_impact

    def create_capacity_impact_report(self, output_path=None):
        """
        Create a report showing how capacity configurations impact performance.
        
        Args:
            output_path: Path to save the report, if None, a default path is used
            
        Returns:
            Path to the saved report
        """
        if output_path is None:
            output_path = f"{self.output_dir}/capacity_impact_{self.timestamp}.pdf"
        
        capacity_impact = self.analyze_capacity_impact()
        
        if capacity_impact.empty:
            print("Cannot create capacity impact report: No capacity data available")
            return None
        
        with PdfPages(output_path) as pdf:
            # Get capacity columns (excluding statistics columns)
            capacity_cols = [col for col in capacity_impact.columns if not any(x in col for x in ['mean', 'std', 'min', 'max', 'count'])]
            
            # For each capacity parameter, create a plot showing its impact on score
            for cap_col in capacity_cols:
                fig, ax = plt.subplots(figsize=(12, 8))
                
                # Group by this capacity parameter
                grouped = capacity_impact.groupby(cap_col)['score_mean'].mean().reset_index()
                grouped_std = capacity_impact.groupby(cap_col)['score_std'].mean().reset_index()
                
                # Create bar chart
                bars = ax.bar(
                    grouped[cap_col].astype(str),
                    grouped['score_mean'],
                    yerr=grouped_std['score_std'],
                    capsize=5
                )
                
                # Add value labels
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    ax.text(
                        bar.get_x() + bar.get_width()/2., height + 0.01,
                        f"{height:.3f}",
                        ha='center', va='bottom', fontsize=9
                    )
                
                # Set labels and title
                ax.set_xlabel(cap_col.replace('_', ' ').title(), fontsize=14)
                ax.set_ylabel('Average Score', fontsize=14)
                ax.set_title(f'Impact of {cap_col.replace("_", " ").title()} on Performance', fontsize=16)
                
                # Adjust y-axis to better show differences
                min_score = max(0, min(grouped['score_mean']) - 0.1)
                max_score = min(1, max(grouped['score_mean']) + 0.1)
                ax.set_ylim(min_score, max_score)
                
                pdf.savefig(fig)
                plt.close()
            
            # Create a correlation heatmap for capacity parameters
            if len(capacity_cols) > 1:
                fig, ax = plt.subplots(figsize=(12, 10))
                
                # Calculate correlation between capacity parameters and score
                corr_data = self.raw_results[capacity_cols + ['score']].corr()
                
                # Create heatmap
                sns.heatmap(
                    corr_data,
                    annot=True,
                    fmt=".2f",
                    cmap="coolwarm",
                    ax=ax,
                    vmin=-1, vmax=1
                )
                
                ax.set_title('Correlation Between Capacity Parameters and Score', fontsize=16)
                plt.tight_layout()
                
                pdf.savefig(fig)
                plt.close()
        
        return output_path

    def create_interactive_dashboard(self, output_path=None):
        """
        Create an interactive HTML dashboard for client presentations.
        
        Args:
            output_path: Path to save the dashboard, if None, a default path is used
            
        Returns:
            Path to the saved dashboard
        """
        try:
            import plotly.express as px
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            import plotly.io as pio
        except ImportError:
            print("Warning: plotly package not found. Cannot create interactive dashboard.")
            return None
        
        if output_path is None:
            output_path = f"{self.output_dir}/interactive_dashboard_{self.timestamp}.html"
        
        # Get analysis results
        best_overall = self.analyze_overall_best_configurations(top_n=20)
        best_robust = self.find_robust_configurations(top_n=20)
        strategy_performance = self.analyze_strategy_performance()
        capacity_impact = self.analyze_capacity_impact()
        
        # Create a dashboard with multiple tabs/sections
        dashboard = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Top Configurations by Overall Performance",
                "Strategy Performance Comparison",
                "Most Robust Configurations",
                "Capacity Impact on Performance"
            )
        )
        
        # Add top configurations bar chart
        dashboard.add_trace(
            go.Bar(
                x=[f"Config {int(cid)}" for cid in best_overall['configuration_id'][:10]],
                y=best_overall['overall_avg_score'][:10],
                error_y=dict(
                    type='data',
                    array=best_overall['overall_std_score'][:10],
                    visible=True
                ),
                name="Top Configurations",
                hovertemplate="Config ID: %{x}<br>Avg Score: %{y:.3f}<br>Std Dev: %{error_y.array:.3f}"
            ),
            row=1, col=1
        )
        
        # Add strategy performance chart
        dashboard.add_trace(
            go.Bar(
                x=[f"S{i}" for i in strategy_performance['strategy_id'][:10]],
                y=strategy_performance['avg_score'][:10],
                name="Strategy Performance",
                hovertemplate="Strategy: %{x}<br>Avg Score: %{y:.3f}"
            ),
            row=1, col=2
        )
        
        # Add robust configurations chart
        dashboard.add_trace(
            go.Bar(
                x=[f"Config {int(cid)}" for cid in best_robust['configuration_id'][:10]],
                y=best_robust['min_strategy_score'][:10],
                name="Robust Configurations",
                hovertemplate="Config ID: %{x}<br>Min Score: %{y:.3f}"
            ),
            row=2, col=1
        )
        
        # Add capacity impact chart if available
        if not capacity_impact.empty:
            # Get first capacity parameter for demonstration
            cap_col = [col for col in capacity_impact.columns if not any(x in col for x in ['mean', 'std', 'min', 'max', 'count'])][0]
            grouped = capacity_impact.groupby(cap_col)['score_mean'].mean().reset_index()
            
            dashboard.add_trace(
                go.Bar(
                    x=grouped[cap_col].astype(str),
                    y=grouped['score_mean'],
                    name="Capacity Impact",
                    hovertemplate=f"{cap_col}: %{{x}}<br>Avg Score: %{{y:.3f}}"
                ),
                row=2, col=2
            )
        
        # Update layout
        dashboard.update_layout(
            title_text="Simulation Results Dashboard",
            height=900,
            width=1200,
            showlegend=False,
            template="plotly_white"
        )
        
        # Save to HTML file
        pio.write_html(dashboard, file=output_path)
        
        return output_path

    def generate_detailed_config_report(self, config_id, output_path=None):
        """
        Generate a detailed report for a specific configuration.
        
        Args:
            config_id: The configuration ID to analyze
            output_path: Path to save the report, if None, a default path is used
            
        Returns:
            Path to the saved report
        """
        if output_path is None:
            output_path = f"{self.output_dir}/config_{config_id}_detailed_report_{self.timestamp}.pdf"
        
        # Get data for this configuration
        config_data = self.raw_results[self.raw_results['configuration_id'] == config_id]
        
        if config_data.empty:
            print(f"Warning: No data found for configuration {config_id}")
            return None
        
        with PdfPages(output_path) as pdf:
            # Create a summary page
            fig, ax = plt.subplots(figsize=(12, 8))
            plt.axis('off')
            
            # Add title
            plt.text(0.5, 0.95, f"Detailed Report for Configuration {config_id}", 
                     ha='center', va='top', fontsize=20, fontweight='bold')
            
            # Add summary statistics
            summary_text = (
                f"Average Score: {config_data['score'].mean():.3f}\n"
                f"Standard Deviation: {config_data['score'].std():.3f}\n"
                f"Minimum Score: {config_data['score'].min():.3f}\n"
                f"Maximum Score: {config_data['score'].max():.3f}\n"
                f"Number of Runs: {len(config_data)}\n\n"
            )
            
            # Add configuration parameters
            param_cols = [col for col in config_data.columns if col not in ['configuration_id', 'score', 'run_id']]
            param_text = "Configuration Parameters:\n"
            for col in param_cols:
                # Get unique value for this parameter (should be the same for all runs)
                value = config_data[col].iloc[0]
                param_text += f"- {col}: {value}\n"
            
            plt.text(0.1, 0.8, summary_text + param_text, va='top', fontsize=12)
            
            pdf.savefig(fig)
            plt.close()
            
            # Create performance across strategies chart
            if 'strategy_id' in config_data.columns:
                fig, ax = plt.subplots(figsize=(12, 8))
                
                # Group by strategy
                strategy_perf = config_data.groupby('strategy_id')['score'].mean().reset_index()
                strategy_std = config_data.groupby('strategy_id')['score'].std().reset_index()
                
                # Create bar chart
                bars = ax.bar(
                    strategy_perf['strategy_id'],
                    strategy_perf['score'],
                    yerr=strategy_std['score'],
                    capsize=5
                )
                
                # Add value labels
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    ax.text(
                        bar.get_x() + bar.get_width()/2., height + 0.01,
                        f"{height:.3f}",
                        ha='center', va='bottom', fontsize=9
                    )
                
                # Set labels and title
                ax.set_xlabel('Strategy ID', fontsize=14)
                ax.set_ylabel('Average Score', fontsize=14)
                ax.set_title(f'Performance of Configuration {config_id} Across Strategies', fontsize=16)
                
                # Adjust y-axis to better show differences
                min_score = max(0, min(strategy_perf['score']) - 0.1)
                max_score = min(1, max(strategy_perf['score']) + 0.1)
                ax.set_ylim(min_score, max_score)
                
                pdf.savefig(fig)
                plt.close()
            
            # Add more visualizations as needed for detailed analysis
            
        return output_path

    def generate_all_reports(self):
        """
        Generate all reports and return paths to them.
        
        Returns:
            Dictionary with paths to all generated reports
        """
        print("Generating reports...")
        
        report_paths = {
            'strategy_weight_comparison': self.create_strategy_weight_comparison_chart(),
            'configuration_performance': self.create_configuration_performance_report(),
            'strategy_configuration_heatmap': self.create_strategy_configuration_heatmap(),
            'summary_report': self.export_summary_report(),
            'capacity_impact': self.create_capacity_impact_report()
        }
        
        # Try to create interactive dashboard if plotly is available
        try:
            dashboard_path = self.create_interactive_dashboard()
            if dashboard_path:
                report_paths['interactive_dashboard'] = dashboard_path
        except Exception as e:
            print(f"Warning: Could not create interactive dashboard: {e}")
        
        print("All reports generated successfully!")
        for name, path in report_paths.items():
            if path:  # Only print if path is not None
                print(f"- {name}: {path}")
            
        return report_paths


if __name__ == "__main__":
    # Replace with the path to your simulation results Excel file
    excel_path = "output/simulation_analysis_iteration_1.xlsx"
    
    # Create the analyzer
    analyzer = SimulationAnalyzer(excel_path)
    
    # Generate all reports
    report_paths = analyzer.generate_all_reports()
    
    print("\nAnalysis complete!")
    print("The following reports have been generated:")
    for name, path in report_paths.items():
        print(f"- {name.replace('_', ' ').title()}: {path}")
    
    print("\nRecommendations:")
    best_overall = analyzer.analyze_overall_best_configurations(top_n=1)
    best_robust = analyzer.find_robust_configurations(top_n=1)
    strategy_perf = analyzer.analyze_strategy_performance()
    
    print(f"- Overall Best Configuration: {int(best_overall['configuration_id'].iloc[0])}")
    print(f"- Most Robust Configuration: {int(best_robust['configuration_id'].iloc[0])}")
    print(f"- Best Strategy: Strategy {strategy_perf['strategy_id'].iloc[0]}")
    print("  (Intensive: {:.1f}, Intermediate: {:.1f}, Distance: {:.1f})".format(
        strategy_perf['intensive_weight'].iloc[0],
        strategy_perf['intermediate_weight'].iloc[0],
        strategy_perf['distance_weight'].iloc[0]
    )) 