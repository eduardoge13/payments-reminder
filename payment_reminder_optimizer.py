# Payment reminder - DS Challenge - Eduardo Gaitan Escalante - 2025

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from scipy import stats
from sklearn.feature_selection import RFE

# Create sample data

def create_sample_data():
    # Creating sample data for the model
    np.random.seed(42)
    n_customers = 1000
    
    # Customer transaction data
    customer_data = pd.DataFrame({
        'customer_id': [f'CUST_{i:04d}' for i in range(n_customers)],
        'days_since_last_payment': np.random.exponential(15, n_customers).clip(1, 90),
        'payment_frequency': np.random.gamma(2, 2, n_customers).clip(0.1, 20),
        'avg_payment_amount': np.random.lognormal(5, 0.8, n_customers).clip(50, 5000),
        'late_payment_rate': np.random.beta(2, 8, n_customers),
        'customer_satisfaction': np.random.normal(3.5, 0.8, n_customers).clip(1, 5),
        'current_reminder_freq': np.random.choice([1, 2, 3, 4, 5], n_customers),
        'payment_response_rate': np.random.beta(3, 7, n_customers),
        'complaint_rate': np.random.beta(1, 20, n_customers),
        'months_of_history': np.random.randint(6, 36, n_customers)
    })
    
    # Channel interaction data
    interaction_data = pd.DataFrame({
        'customer_id': customer_data['customer_id'],
        'age': np.random.normal(40, 15, n_customers).clip(18, 80),
        'income_bracket': np.random.choice([1, 2, 3, 4, 5], n_customers),
        'app_usage_score': np.random.beta(2, 3, n_customers),
        'email_engagement': np.random.beta(3, 4, n_customers),
        'whatsapp_response_hist': np.random.beta(4, 3, n_customers),
        'best_channel': np.random.choice(['whatsapp', 'email', 'push', 'phone'], n_customers, 
                                       p=[0.5, 0.3, 0.15, 0.05])
    })
    
    return customer_data, interaction_data



class PaymentReminderOptimizer:
    
    def __init__(self):
        self.customer_segments = None
        self.channel_model = None
        self.segment_strategies = {}
        
    def segment_customers_rfm(self, customer_data):
        #RFM --> Divides the customers into 5 segments based on how recent was their last payment, how often they pay  and how much they pay in average

        print("Segmenting customers...")
        # Recency
        customer_data['R_Score'] = pd.qcut(customer_data['days_since_last_payment'], 5, labels=[5,4,3,2,1]) 
        # Frequency
        customer_data['F_Score'] = pd.qcut(customer_data['payment_frequency'], 5, labels=[1,2,3,4,5])
        # Monetary
        customer_data['M_Score'] = pd.qcut(customer_data['avg_payment_amount'], 5, labels=[1,2,3,4,5])
        # Parse to integer
        customer_data['R_Score'] = customer_data['R_Score'].astype(int)
        customer_data['F_Score'] = customer_data['F_Score'].astype(int)
        customer_data['M_Score'] = customer_data['M_Score'].astype(int)
        
        def assign_segment(row):
            r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
            
            if r >= 4 and f >= 4 and m >= 4:
                return 'A. Loyal'
            elif r >= 3 and f >= 3 and m >= 3:
                return 'B. Promising'  
            elif r >= 3 and f <= 2 and m >= 3:
                return 'C. Potential High Value'  
            elif r >= 3 and f <= 2 and m < 3:
                return 'D. Potential Low Value' 
            elif r <= 2 and f >= 3 and m >= 3:
                return 'E. Likely to Default (High Value)'  
            elif r <= 2 and f >= 3 and m < 3:
                return 'F. Likely to Default (Low Value)'  
            elif m >= 4:
                return 'G. High Value - Needs Attention'
            else:
                return 'H. Requires Attention'
        
        # get the segment
        customer_data['Segment'] = customer_data.apply(assign_segment, axis=1)
        
        # segment statistics
        segment_stats = customer_data.groupby('Segment').agg({
            'late_payment_rate': 'mean',
            'avg_payment_amount': 'mean',
            'customer_satisfaction': 'mean'
        }).round(3)
        
        print("Segment Statistics:")
        print(segment_stats)
        
        self.customer_segments = customer_data
        return customer_data
    
    def optimize_channel_selection(self, interaction_data):
        print("Channel Selection...")
        
        # Prepare features
        # Use all variables except the target
        features = [col for col in interaction_data.columns if col not in ['customer_id', 'best_channel']]
        X = interaction_data[features]
        y = interaction_data['best_channel']
        
        # Select top 10 features
        rfe = RFE(estimator=RandomForestClassifier(), n_features_to_select=10)
        X_selected = rfe.fit_transform(X, y)
        # Get selected feature names
        selected_features = X.columns[rfe.support_].tolist()
        
        # Train model
        X_train, X_test, y_train, y_test = train_test_split(X_selected, y, test_size=0.3, random_state=42)
        
        self.channel_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.channel_model.fit(X_train, y_train)
        
        # Validation
        y_pred = self.channel_model.predict(X_test)
        accuracy = (y_pred == y_test).mean()
        
        print(f"Channel Prediction Accuracy: {accuracy:.2%}")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': selected_features,
            'importance': self.channel_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("Feature importance:")
        print(feature_importance)
        
        return self.channel_model
    
    def calculate_optimal_frequency(self, segment_data):
        
        frequency_analysis = {}
        
        for segment in segment_data['Segment'].unique():
            segment_customers = segment_data[segment_data['Segment'] == segment]
            
            # Frequency response 
            freq_response = segment_customers.groupby('current_reminder_freq').agg({
                'payment_response_rate': 'mean', # proportion of customers that paid after the reminder
                'customer_satisfaction': 'mean', # average satisfaction score
                'complaint_rate': 'mean' # proportion of customers that complained before or after the reminder
            })
            
            # Find optimal frequency
            freq_response['optimization_score'] = (
                freq_response['payment_response_rate'] * 0.6 +
                freq_response['customer_satisfaction'] * 0.3 -
                freq_response['complaint_rate'] * 0.1
            ) # The logic here is that payment response rate is the most important factor, then customer satisfaction and complaint rate
              # The weights are chosen for the Challenge

            
            optimal_freq = freq_response['optimization_score'].idxmax()

            
            frequency_analysis[segment] = {
                'optimal_frequency': optimal_freq,
                'expected_response_rate': freq_response.loc[optimal_freq, 'payment_response_rate'],
                'expected_satisfaction': freq_response.loc[optimal_freq, 'customer_satisfaction']
            }
        
        print("Optimal Frequencies by Segment:")
        for segment, analysis in frequency_analysis.items():
            print(f"  {segment}: {analysis['optimal_frequency']} reminders "
                  f"(Response: {analysis['expected_response_rate']:.1%})")
        
        self.segment_strategies = frequency_analysis
        return frequency_analysis
    
    def generate_personalized_strategy(self, customer_id, customer_data):
        """generates personalized strategy for a customer"""
        customer = customer_data[customer_data['customer_id'] == customer_id].iloc[0]
        segment = customer['Segment']
        
        # predict optimal channel if model is available
        if self.channel_model is not None:
            customer_features = [[
                customer['age'],
                customer['income_bracket'],
                customer['app_usage_score'],
                customer['email_engagement'],
                customer['whatsapp_response_hist']
            ]]
            optimal_channel = self.channel_model.predict(customer_features)[0]
        else:
            optimal_channel = 'whatsapp'  # default to whatsapp
        
        optimal_frequency = self.segment_strategies[segment]['optimal_frequency']
        
        strategy = {
            'customer_id': customer_id,
            'segment': segment,
            'optimal_channel': optimal_channel,
            'reminder_frequency': optimal_frequency,
            'expected_response_rate': self.segment_strategies[segment]['expected_response_rate'],
            'personalization_confidence': self._calculate_confidence(customer, segment)
        }
        
        return strategy
    
    def _calculate_confidence(self, customer, segment):
        
        base_confidence = 0.7
        
        if customer['Segment'] == segment:
            base_confidence += 0.2
        
        if customer['months_of_history'] > 12:
            base_confidence += 0.1
        
        return min(1.0, base_confidence)
    
    def run_ab_test(self, test_data, control_strategy, new_strategy):
        
        print("Running A/B Test...")
        
        # split customers into control and test groups
        np.random.seed(42)
        test_data['group'] = np.random.choice(['control', 'test'], len(test_data), p=[0.5, 0.5])
        
        # simulate results
        results = []
        
        for _, customer in test_data.iterrows():
            if customer['group'] == 'control':
                response_rate = 0.25
                satisfaction = 3.2
            else:
                segment = customer['Segment']
                response_rate = self.segment_strategies[segment]['expected_response_rate']
                satisfaction = self.segment_strategies[segment]['expected_satisfaction']
            
            # add noise to increase the realism of synthetic data
            actual_response = np.random.binomial(1, response_rate)
            actual_satisfaction = np.random.normal(satisfaction, 0.3)
            
            results.append({
                'customer_id': customer['customer_id'],
                'group': customer['group'],
                'responded': actual_response,
                'satisfaction': actual_satisfaction,
                'segment': customer['Segment']
            })
        
        results_df = pd.DataFrame(results)
        
        # Statistical analysis
        control_response = results_df[results_df['group'] == 'control']['responded'].mean()
        test_response = results_df[results_df['group'] == 'test']['responded'].mean()
        
        control_satisfaction = results_df[results_df['group'] == 'control']['satisfaction'].mean()
        test_satisfaction = results_df[results_df['group'] == 'test']['satisfaction'].mean()
        
        # Statistical significance testing
        response_contingency = [
            [results_df[(results_df['group'] == 'control') & (results_df['responded'] == 1)].shape[0],
             results_df[(results_df['group'] == 'control') & (results_df['responded'] == 0)].shape[0]],
            [results_df[(results_df['group'] == 'test') & (results_df['responded'] == 1)].shape[0],
             results_df[(results_df['group'] == 'test') & (results_df['responded'] == 0)].shape[0]]
        ]
        
        response_stat, response_p, _, _ = stats.chi2_contingency(response_contingency)
        
        satisfaction_stat, satisfaction_p = stats.ttest_ind(
            results_df[results_df['group'] == 'control']['satisfaction'],
            results_df[results_df['group'] == 'test']['satisfaction']
        )
        
        print("A/B Test Results:")
        print(f"  Response Rate - Control: {control_response:.2%}, Test: {test_response:.2%}")
        print(f"  Improvement: {((test_response - control_response) / control_response * 100):+.1f}%")
        print(f"  Statistical Significance: {'Yes' if response_p < 0.05 else 'No'} (p={response_p:.4f})")
        
        print(f"  Satisfaction - Control: {control_satisfaction:.2f}, Test: {test_satisfaction:.2f}")
        print(f"  Improvement: {(test_satisfaction - control_satisfaction):+.2f} points")
        print(f"  Statistical Significance: {'Yes' if satisfaction_p < 0.05 else 'No'} (p={satisfaction_p:.4f})")
        
        return {
            'response_improvement': (test_response - control_response) / control_response,
            'satisfaction_improvement': test_satisfaction - control_satisfaction,
            'response_significant': response_p < 0.05,
            'satisfaction_significant': satisfaction_p < 0.05,
            'results_data': results_df
        }


def main():

    
    print("Payment Reminder Optimization")
    print("=" * 40)
    
    # Create sample data
    print("Generating sample data...")
    customer_data, interaction_data = create_sample_data()
    print(f"Created data for {len(customer_data)} customers")
    
    # Initialize optimizer class
    optimizer = PaymentReminderOptimizer()
    
    # 
    print("\nRunning Optimization Process...")
    
    # Customer segmentation
    segmented_data = optimizer.segment_customers_rfm(customer_data)
    
    # Channel optimization
    channel_model = optimizer.optimize_channel_selection(interaction_data)
    
    # Frequency optimization
    frequency_analysis = optimizer.calculate_optimal_frequency(segmented_data)
    
    # Generate sample strategies
    print("\nSample Personalized Strategies:")
    sample_customers = customer_data.sample(5)['customer_id']
    
    for customer_id in sample_customers:
        strategy = optimizer.generate_personalized_strategy(customer_id, segmented_data)
        print(f"  {customer_id}: {strategy['segment']} → "
              f"{strategy['optimal_channel']} → "
              f"{strategy['reminder_frequency']} reminders "
              f"(Confidence: {strategy['personalization_confidence']:.1%})")
    
    # A/B Test validation
    test_results = optimizer.run_ab_test(customer_data.sample(200), 'control', 'personalized')
    
    # Business impact summary
    print("\nExpected Business Impact:")
    if test_results['response_significant']:
        response_lift = test_results['response_improvement'] * 100
        print(f"  • Response Rate Improvement: +{response_lift:.1f}%")
        print(f"  • Estimated Delinquency Reduction: {response_lift * 0.4:.1f}%")
    
    if test_results['satisfaction_significant']:
        sat_improvement = test_results['satisfaction_improvement']
        print(f"  • Customer Satisfaction Increase: +{sat_improvement:.2f} points")
    
    print("\nOptimization Complete!")
    
    return optimizer, test_results


if __name__ == "__main__":
    optimizer, results = main() 