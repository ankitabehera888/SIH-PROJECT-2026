from src.profiling.quality_score import calculate_quality_scores, WEIGHTS

def test_weights_sum_to_one():
    """Assert that the 5 quality dimension weights sum exactly to 1.0 (100%)."""
    total_weight = sum(WEIGHTS.values())
    assert round(total_weight, 4) == 1.0

def test_quality_scorecard_generation():
    """Assert that quality scores are calculated for all core clinical tables."""
    result = calculate_quality_scores()
    assert "platform_score" in result
    assert "table_scores_df" in result
    
    df_scores = result["table_scores_df"]
    assert not df_scores.empty
    assert len(df_scores) >= 10
    
    # Assert score bounds
    platform_score = result["platform_score"]
    assert 0.0 <= platform_score <= 100.0
    assert platform_score >= 80.0, f"Quality score {platform_score} is below acceptable baseline"

def test_dimension_scores_bounded():
    """Assert that all component dimension scores are within [0, 100]."""
    result = calculate_quality_scores()
    df_scores = result["table_scores_df"]
    
    for col in ["Completeness_Score", "Consistency_Score", "Validity_Score", "Integrity_Score", "Timeliness_Score", "Overall_Score"]:
        assert (df_scores[col] >= 0.0).all()
        assert (df_scores[col] <= 100.0).all()
