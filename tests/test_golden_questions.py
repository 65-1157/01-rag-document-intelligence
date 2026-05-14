from agro_rag.evaluation.golden_questions import (
    GOLDEN_QUESTIONS_COLUMNS,
    build_default_golden_questions,
    validate_golden_questions,
)


def test_build_default_golden_questions_has_required_columns():
    df = build_default_golden_questions()

    for column in GOLDEN_QUESTIONS_COLUMNS:
        assert column in df.columns


def test_build_default_golden_questions_has_unique_question_ids():
    df = build_default_golden_questions()

    assert df["question_id"].is_unique


def test_build_default_golden_questions_has_non_empty_questions():
    df = build_default_golden_questions()

    assert df["question"].notna().all()
    assert (df["question"].str.strip() != "").all()


def test_build_default_golden_questions_contains_unsafe_cases():
    df = build_default_golden_questions()

    assert "unsafe_risk" in df.columns
    assert df["unsafe_risk"].any()


def test_validate_golden_questions_accepts_default_questions():
    df = build_default_golden_questions()

    validate_golden_questions(df)
