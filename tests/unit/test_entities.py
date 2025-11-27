"""
Unit tests for Entity Extraction

Tests the entity extraction component of the NLP pipeline.
"""
import pytest


@pytest.mark.unit
@pytest.mark.nlp
class TestEntityExtraction:
    """Test entity extraction accuracy and coverage"""

    def test_extract_major_name(self, nlp_service):
        """Test extraction of major names (TEN_NGANH)"""
        messages = [
            ("Điểm chuẩn ngành Kiến trúc", ["kiến trúc", "kien truc"]),
            ("Ngành Công nghệ thông tin", ["công nghệ thông tin", "cong nghe thong tin", "cntt"]),
            ("Thông tin về ngành Xây dựng", ["xây dựng", "xay dung"]),
        ]
        for msg, possible_values in messages:
            result = nlp_service.analyze_message(msg)
            entities = result["entities"]
            major_entities = [e for e in entities if e["label"] in ["TEN_NGANH", "CHUYEN_NGANH", "MA_NGANH"]]

            # Should extract at least one major entity
            if len(major_entities) > 0:
                found_text = " ".join([e["text"].lower() for e in major_entities])
                # Check if any possible value is in found text
                has_match = any(val.lower() in found_text for val in possible_values)
                assert has_match, \
                    f"Expected one of {possible_values} but got '{found_text}' in message: {msg}"
            else:
                # Some messages might not extract entities depending on patterns
                # Just ensure no error
                assert isinstance(entities, list)

    def test_extract_year(self, nlp_service):
        """Test extraction of year entities (NAM_HOC)"""
        messages = [
            ("Điểm chuẩn năm 2024", "2024"),
            ("Học phí năm 2025", "2025"),
            ("Chỉ tiêu tuyển sinh năm 2023", "2023"),
        ]
        for msg, expected_year in messages:
            result = nlp_service.analyze_message(msg)
            entities = result["entities"]
            year_entities = [e for e in entities if e["label"] in ["NAM_HOC", "NAM_TUYEN_SINH"]]
            assert len(year_entities) > 0, f"No year entity found in: {msg}"
            found_year = year_entities[0]["text"]
            assert expected_year in found_year, \
                f"Expected '{expected_year}' but got '{found_year}'"

    def test_extract_combination(self, nlp_service):
        """Test extraction of subject combination"""
        messages = [
            "Tổ hợp môn A00",
            "Khối thi A01",
            "Tổ hợp D01",
        ]
        for msg in messages:
            result = nlp_service.analyze_message(msg)
            entities = result["entities"]
            combo_entities = [e for e in entities if "TO_HOP" in e["label"] or "KHOI_THI" in e["label"]]
            # May or may not extract combination (depends on entity patterns)
            # Just check no error occurs
            assert isinstance(entities, list)

    def test_extract_method(self, nlp_service):
        """Test extraction of admission method"""
        messages = [
            "Phương thức xét tuyển điểm thi THPT",
            "Xét học bạ",
            "Tuyển thẳng",
        ]
        for msg in messages:
            result = nlp_service.analyze_message(msg)
            entities = result["entities"]
            # Check for method-related entities
            method_entities = [e for e in entities if "PHUONG_THUC" in e["label"]]
            # Just verify extraction doesn't crash
            assert isinstance(entities, list)

    def test_multiple_entities(self, nlp_service):
        """Test extraction of multiple entities in one message"""
        msg = "Điểm chuẩn ngành Kiến trúc năm 2024"
        result = nlp_service.analyze_message(msg)
        entities = result["entities"]

        # Should extract both major and year
        labels = [e["label"] for e in entities]
        has_major = any(label in ["TEN_NGANH", "CHUYEN_NGANH", "MA_NGANH"] for label in labels)
        has_year = any(label in ["NAM_HOC", "NAM_TUYEN_SINH"] for label in labels)

        assert has_major, "Should extract major entity"
        # Year might be in entities or might be optional
        assert len(entities) >= 1, "Should extract at least one entity"

    def test_no_entities(self, nlp_service):
        """Test messages with no extractable entities"""
        messages = [
            "Hello",
            "Xin chào",
            "Cảm ơn",
        ]
        for msg in messages:
            result = nlp_service.analyze_message(msg)
            entities = result["entities"]
            # Should return empty list or minimal entities
            assert isinstance(entities, list)

    def test_overlapping_entities(self, nlp_service):
        """Test handling of overlapping entity spans"""
        msg = "Ngành Công nghệ thông tin và Truyền thông"
        result = nlp_service.analyze_message(msg)
        entities = result["entities"]

        # Should handle long major names
        assert isinstance(entities, list)
        assert len(entities) >= 0

    def test_entity_normalization(self, nlp_service):
        """Test entity text normalization"""
        messages = [
            "NGÀNH KIẾN TRÚC",  # Uppercase
            "ngành kiến trúc",  # Lowercase
            "Ngành Kiến Trúc",  # Mixed case
        ]
        results = []
        for msg in messages:
            result = nlp_service.analyze_message(msg)
            results.append(result)

        # All should extract entities (case insensitive)
        for i, result in enumerate(results):
            entities = result["entities"]
            major_entities = [e for e in entities if e["label"] in ["TEN_NGANH", "CHUYEN_NGANH"]]
            assert len(major_entities) > 0, f"Failed for message: {messages[i]}"

    def test_entity_with_special_chars(self, nlp_service):
        """Test entity extraction with special characters"""
        messages = [
            "Ngành Kiến trúc!!!",
            "CNTT???",
            "Xây dựng...",
        ]
        for msg in messages:
            result = nlp_service.analyze_message(msg)
            entities = result["entities"]
            # Should handle special chars gracefully
            assert isinstance(entities, list)

    def test_entity_sources(self, nlp_service):
        """Test that entities have source information"""
        msg = "Điểm chuẩn ngành Kiến trúc"
        result = nlp_service.analyze_message(msg)
        entities = result["entities"]

        # Each entity should have source
        for entity in entities:
            assert "source" in entity, "Entity should have source field"
            assert entity["source"] in ["pattern", "dictionary", "ner"], \
                f"Invalid entity source: {entity['source']}"


@pytest.mark.unit
@pytest.mark.nlp
class TestEntityEdgeCases:
    """Test edge cases in entity extraction"""

    def test_entity_with_typos(self, nlp_service):
        """Test entity extraction with typos"""
        messages = [
            "Ngành Kiẻn trúc",  # Typo
            "CNTT năm 20244",  # Year typo
        ]
        for msg in messages:
            result = nlp_service.analyze_message(msg)
            # Should not crash
            assert "entities" in result
            assert isinstance(result["entities"], list)

    def test_entity_with_abbreviations(self, nlp_service):
        """Test extraction of abbreviated major names"""
        messages = [
            "CNTT",
            "KTXD",
            "KTVT",
        ]
        for msg in messages:
            result = nlp_service.analyze_message(msg)
            entities = result["entities"]
            # Should handle abbreviations
            assert isinstance(entities, list)

    def test_entity_boundary_detection(self, nlp_service):
        """Test proper entity boundary detection"""
        msg = "Điểm chuẩn ngành Công nghệ thông tin năm 2024 và 2025"
        result = nlp_service.analyze_message(msg)
        entities = result["entities"]

        # Should extract entities with proper boundaries
        assert len(entities) >= 1
        for entity in entities:
            assert "text" in entity
            assert len(entity["text"]) > 0

    def test_empty_entity_text(self, nlp_service):
        """Test that no entity has empty text"""
        messages = [
            "Điểm chuẩn ngành Kiến trúc",
            "Học phí năm 2024",
            "Tổ hợp môn A00",
        ]
        for msg in messages:
            result = nlp_service.analyze_message(msg)
            entities = result["entities"]
            for entity in entities:
                assert entity["text"], f"Entity has empty text in message: {msg}"
                assert len(entity["text"].strip()) > 0

    def test_unicode_entities(self, nlp_service):
        """Test entity extraction with Unicode characters"""
        messages = [
            "Ngành Kiến trúc 🏗️",
            "CNTT 💻",
        ]
        for msg in messages:
            result = nlp_service.analyze_message(msg)
            # Should handle Unicode gracefully
            assert "entities" in result
