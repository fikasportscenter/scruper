import math

def poisson_probability(k, lambda_val):
    """Calculate Poisson probability P(X=k)"""
    return (lambda_val ** k) * math.exp(-lambda_val) / math.factorial(k)

def predict_scoreline(home_stats, away_stats):
    """
    Predicts scoreline using Poisson distribution based on average goals.
    """
    if not home_stats or not away_stats:
        return None

    # Attack Strength vs Defense Strength simplification
    # Home Attack Strength = Home Avg Goals Scored
    # Away Defense Strength = Away Avg Goals Conceded
    # We'll use a simplified approach: 
    # Expected Goals Home = (Home Avg Scored + Away Avg Conceded) / 2
    # Expected Goals Away = (Away Avg Scored + Home Avg Conceded) / 2
    
    lambda_home = (home_stats['avg_goals_scored'] + away_stats['avg_goals_conceded']) / 2
    lambda_away = (away_stats['avg_goals_scored'] + home_stats['avg_goals_conceded']) / 2
    
    # Calculate probabilities for scores 0-5
    prob_matrix = []
    max_goals = 5
    for i in range(max_goals + 1):
        row = []
        for j in range(max_goals + 1):
            p_home = poisson_probability(i, lambda_home)
            p_away = poisson_probability(j, lambda_away)
            row.append(p_home * p_away)
        prob_matrix.append(row)
    
    # Find most likely scoreline
    best_score = None
    max_prob = 0
    
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            if prob_matrix[i][j] > max_prob:
                max_prob = prob_matrix[i][j]
                best_score = (i, j)
                
    confidence = round(max_prob * 100, 1)
    
    return {
        'predicted_score': f"{best_score[0]}-{best_score[1]}",
        'confidence': f"{confidence}%",
        'expected_goals_home': round(lambda_home, 2),
        'expected_goals_away': round(lambda_away, 2)
    }