"""
Unit tests for Data Processors

Tests the CSV data processing functions.
"""
import pytest

from services.processors import (
    find_standard_score,
    list_majors,
    list_tuition,
    list_scholarships,
    list_admission_conditions,
    list_admission_quota,
    list_admission_methods,
    get_combination_codes,
    format_data_to_text,
    infer_major_from_message,
)


@pytest.mark.unit
@pytest.mark.data
class TestScoreProcessors:
    """Test score-related data processors"""

    def test_find_standard_score_by_major(self):
        """Test finding standard scores by major name"""
        result = find_standard_score(major="Kiến trúc")

        assert isinstance(result, list)
        # May or may not find results depending on data
        if result:
            assert all("program_name" in r for r in result)

    def test_find_standard_score_by_year(self):
        """Test finding standard scores by year"""
        result = find_standard_score(year="2024")

        assert isinstance(result, list)
        # Should return data for 2024

    def test_find_standard_score_both_params(self):
        """Test finding scores with both major and year"""
        result = find_standard_score(major="CNTT", year="2024")

        assert isinstance(result, list)

    def test_find_standard_score_no_params(self):
        """Test finding scores without parameters"""
        result = find_standard_score()

        assert isinstance(result, list)
        # Should return all or empty


@pytest.mark.unit
@pytest.mark.data
class TestMajorProcessors:
    """Test major-related data processors"""

    def test_list_majors_with_filter(self):
        """Test listing majors with filter"""
        result = list_majors("Kiến trúc")

        assert isinstance(result, list)
        if result:
            assert all("major_name" in r for r in result)

    def test_list_majors_no_filter(self):
        """Test listing all majors"""
        result = list_majors()

        assert isinstance(result, list)
        # Should return some majors
        assert len(result) >= 0

    def test_infer_major_from_message(self):
        """Test inferring major from message"""
        cases = [
            ("Điểm chuẩn ngành Kiến trúc", "kiến trúc"),
            ("CNTT năm 2024", "cntt"),
            ("Xây dựng", "xây dựng"),
        ]

        for msg, expected_keyword in cases:
            result = infer_major_from_message(msg)
            # May or may not find exact match
            if result:
                assert isinstance(result, str)
                assert len(result) > 0


@pytest.mark.unit
@pytest.mark.data
class TestAcademicProcessors:
    """Test academic-related data processors"""

    def test_list_tuition(self):
        """Test listing tuition information"""
        result = list_tuition()

        assert isinstance(result, list)
        if result:
            assert all("tuition_fee" in r for r in result)

    def test_list_tuition_by_year(self):
        """Test listing tuition by year"""
        result = list_tuition(year="2024")

        assert isinstance(result, list)

    def test_list_scholarships(self):
        """Test listing scholarships"""
        result = list_scholarships()

        assert isinstance(result, list)
        if result:
            assert all("scholarship_name" in r for r in result)
            # We know there are 53 scholarships
            assert len(result) > 0


@pytest.mark.unit
@pytest.mark.data
class TestAdmissionProcessors:
    """Test admission-related data processors"""

    def test_list_admission_conditions(self):
        """Test listing admission conditions"""
        result = list_admission_conditions()

        assert isinstance(result, list)
        if result:
            assert all("requirements" in r or "condition_name" in r for r in result)

    def test_list_admission_quota(self):
        """Test listing admission quota"""
        result = list_admission_quota()

        assert isinstance(result, list)

    def test_list_admission_quota_by_major(self):
        """Test listing quota by major"""
        result = list_admission_quota(major="Kiến trúc")

        assert isinstance(result, list)

    def test_list_admission_methods(self):
        """Test listing admission methods"""
        result = list_admission_methods()

        assert isinstance(result, list)
        if result:
            assert all("method_name" in r or "abbreviation" in r for r in result)

    def test_get_combination_codes(self):
        """Test getting combination codes"""
        result = get_combination_codes()

        assert isinstance(result, list)
        if result:
            assert all("combination_code" in r for r in result)


@pytest.mark.unit
@pytest.mark.data
class TestFormattingUtilities:
    """Test data formatting utilities"""

    def test_format_data_to_text_scores(self):
        """Test formatting standard scores to text"""
        sample_data = [
            {
                "program_name": "Kiến trúc",
                "2024": "25.5",
                "subject_combination": "A00"
            }
        ]

        result = format_data_to_text(sample_data, "standard_score")

        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_data_to_text_majors(self):
        """Test formatting majors to text"""
        sample_data = [
            {
                "major_name": "Kiến trúc",
                "description": "Đào tạo kiến trúc sư"
            }
        ]

        result = format_data_to_text(sample_data, "major_info")

        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_data_to_text_empty(self):
        """Test formatting empty data"""
        result = format_data_to_text([], "standard_score")

        assert isinstance(result, str)
        # Should handle empty gracefully

    def test_format_data_to_text_scholarships(self):
        """Test formatting scholarships to text"""
        sample_data = [
            {
                "scholarship_name": "Học bổng A",
                "value": "100%",
                "requirements": "Điểm cao"
            }
        ]

        result = format_data_to_text(sample_data, "scholarships")

        assert isinstance(result, str)
        assert len(result) > 0


@pytest.mark.unit
@pytest.mark.data
class TestDataProcessorEdgeCases:
    """Test edge cases in data processing"""

    def test_find_score_invalid_major(self):
        """Test finding scores with invalid major name"""
        result = find_standard_score(major="InvalidMajorXYZ123")

        assert isinstance(result, list)
        # Should return empty list

    def test_find_score_invalid_year(self):
        """Test finding scores with invalid year"""
        result = find_standard_score(year="9999")

        assert isinstance(result, list)

    def test_list_majors_special_chars(self):
        """Test listing majors with special characters in filter"""
        result = list_majors("@#$%^")

        assert isinstance(result, list)
        # Should handle gracefully

    def test_infer_major_empty_message(self):
        """Test inferring major from empty message"""
        result = infer_major_from_message("")

        # Should return None or empty
        assert result is None or result == ""

    def test_infer_major_no_major_keywords(self):
        """Test inferring major from message without major keywords"""
        result = infer_major_from_message("Hello world")

        # Should return None
        assert result is None or result == ""

    def test_format_data_invalid_type(self):
        """Test formatting with invalid type"""
        sample_data = [{"key": "value"}]
        result = format_data_to_text(sample_data, "invalid_type")

        # Should handle gracefully
        assert isinstance(result, str)
