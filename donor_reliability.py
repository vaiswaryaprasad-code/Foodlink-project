
def calculate_reliability(total, claimed, expired):

    # Start with a neutral reliability score
    score = 50

    if total > 0:
        # Reward successful food claims
        claim_rate = (claimed / total) * 100
        score += claim_rate * 0.3

        # Penalize expired donations
        expiry_rate = (expired / total) * 100
        score -= expiry_rate * 0.3

    # Keep the score between 0 and 100
    score = max(0, min(100, round(score)))

    return score

