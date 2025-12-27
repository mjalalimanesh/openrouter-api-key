import numpy as np

def calculate_new_limit_increment(usage_list):
    """
    Calculates the average usage from the last 7 days excluding outliers via IQR.
    Returns (average, days_count).
    """
    if not usage_list:
        return 0.0, 0
    
    if len(usage_list) < 4:
        # Not enough data for meaningful IQR, just return simple average
        return float(np.mean(usage_list)), len(usage_list)

    data = np.array(usage_list)
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    
    lower_bound = q1 - 1.0 * iqr
    upper_bound = q3 + 1.0 * iqr
    
    filtered_data = data[(data >= lower_bound) & (data <= upper_bound)]
    
    if len(filtered_data) == 0:
        return float(np.mean(usage_list)), len(usage_list)
        
    return float(np.mean(filtered_data)), len(filtered_data)

