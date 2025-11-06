"""
Tests for cross_framework_mapping.py
"""

import pytest
from cross_framework_mapping import (
    EU_TO_NIST_MAPPING,
    NIST_TO_EU_MAPPING,
    build_cross_mapping,
    get_related_nist_subcategories,
    get_related_eu_articles,
    get_all_eu_articles,
    get_all_nist_subcategories
)


class TestMappingConstants:
    """Test the mapping constant dictionaries"""

    def test_eu_to_nist_mapping_exists(self):
        """Test that EU to NIST mapping is defined"""
        assert isinstance(EU_TO_NIST_MAPPING, dict)
        assert len(EU_TO_NIST_MAPPING) > 0

    def test_nist_to_eu_mapping_exists(self):
        """Test that NIST to EU mapping is defined"""
        assert isinstance(NIST_TO_EU_MAPPING, dict)
        assert len(NIST_TO_EU_MAPPING) > 0

    def test_eu_to_nist_structure(self):
        """Test structure of EU to NIST mapping"""
        for eu_article, nist_list in EU_TO_NIST_MAPPING.items():
            assert isinstance(eu_article, str)
            assert eu_article.startswith("Article_")
            assert isinstance(nist_list, list)
            assert len(nist_list) > 0

            for nist_subcat in nist_list:
                assert isinstance(nist_subcat, str)
                # Should match pattern like "GOVERN.1.1"
                assert "." in nist_subcat

    def test_nist_to_eu_structure(self):
        """Test structure of NIST to EU mapping"""
        for nist_subcat, eu_list in NIST_TO_EU_MAPPING.items():
            assert isinstance(nist_subcat, str)
            assert "." in nist_subcat
            assert isinstance(eu_list, list)
            assert len(eu_list) > 0

            for eu_article in eu_list:
                assert isinstance(eu_article, str)
                assert eu_article.startswith("Article_")

    def test_key_mappings_exist(self):
        """Test that key articles/subcategories are mapped"""
        # Key EU articles
        assert "Article_9" in EU_TO_NIST_MAPPING  # Risk management
        assert "Article_14" in EU_TO_NIST_MAPPING  # Human oversight
        assert "Article_15" in EU_TO_NIST_MAPPING  # Accuracy/robustness

        # Key NIST subcategories
        assert "GOVERN.1.1" in NIST_TO_EU_MAPPING
        assert "MAP.3.5" in NIST_TO_EU_MAPPING
        assert "MEASURE.2.4" in NIST_TO_EU_MAPPING

    def test_bidirectional_mapping_consistency(self):
        """Test that mappings are bidirectionally consistent"""
        # If EU Article_9 maps to GOVERN.1.3, then GOVERN.1.3 should map back to Article_9
        for eu_article, nist_list in EU_TO_NIST_MAPPING.items():
            for nist_subcat in nist_list:
                if nist_subcat in NIST_TO_EU_MAPPING:
                    # The reverse mapping should include this EU article
                    assert any(
                        article == eu_article or article in eu_article
                        for article in NIST_TO_EU_MAPPING[nist_subcat]
                    ), f"{nist_subcat} should map back to {eu_article}"


class TestBuildCrossMapping:
    """Test build_cross_mapping function"""

    def test_build_empty_mapping(self):
        """Test building mapping with empty inputs"""
        result = build_cross_mapping([], [])

        assert "eu_to_nist" in result
        assert "nist_to_eu" in result
        assert result["eu_to_nist"] == {}
        assert result["nist_to_eu"] == {}

    def test_build_mapping_single_article(self):
        """Test building mapping with single EU article"""
        eu_articles = [14]
        nist_subcategories = ["GOVERN.3.2", "MAP.3.5", "MANAGE.2.4"]

        result = build_cross_mapping(eu_articles, nist_subcategories)

        assert "Article_14" in result["eu_to_nist"]
        assert len(result["eu_to_nist"]["Article_14"]) > 0

        # All returned NIST subcategories should be in the input list
        for nist in result["eu_to_nist"]["Article_14"]:
            assert nist in nist_subcategories

    def test_build_mapping_multiple_articles(self):
        """Test building mapping with multiple EU articles"""
        eu_articles = [9, 10, 14, 15]
        nist_subcategories = [
            "GOVERN.1.3", "MAP.1.1", "MAP.3.5",
            "MEASURE.2.3", "MEASURE.2.5", "MANAGE.1.2"
        ]

        result = build_cross_mapping(eu_articles, nist_subcategories)

        # Should have mappings for applicable articles
        assert len(result["eu_to_nist"]) > 0
        assert len(result["nist_to_eu"]) > 0

    def test_build_mapping_filters_applicable_only(self):
        """Test that mapping only includes applicable items"""
        eu_articles = [14]  # Only Article 14
        nist_subcategories = ["MAP.3.5", "GOVERN.1.1"]  # MAP.3.5 relates to Article 14

        result = build_cross_mapping(eu_articles, nist_subcategories)

        # Should only include Article_14
        assert "Article_14" in result["eu_to_nist"]
        # Should not include other articles
        assert "Article_9" not in result["eu_to_nist"]

        # Should only include NIST subcategories that map to Article 14
        for nist in result["eu_to_nist"]["Article_14"]:
            assert nist in nist_subcategories

    def test_build_mapping_no_matching_nist(self):
        """Test building mapping when no NIST subcategories match"""
        eu_articles = [14]
        nist_subcategories = ["UNKNOWN.1.1"]  # Non-existent subcategory

        result = build_cross_mapping(eu_articles, nist_subcategories)

        # Should have empty or minimal mappings
        if "Article_14" in result["eu_to_nist"]:
            assert len(result["eu_to_nist"]["Article_14"]) == 0

    def test_build_mapping_comprehensive(self):
        """Test building comprehensive mapping with many items"""
        eu_articles = [5, 6, 9, 10, 11, 12, 13, 14, 15, 26, 27, 50]
        nist_subcategories = [
            "GOVERN.1.1", "GOVERN.1.2", "GOVERN.1.3", "GOVERN.1.6",
            "GOVERN.2.1", "GOVERN.3.2", "GOVERN.4.2",
            "MAP.1.1", "MAP.2.3", "MAP.3.1", "MAP.3.5", "MAP.5.1",
            "MEASURE.2.3", "MEASURE.2.4", "MEASURE.2.5", "MEASURE.2.7",
            "MEASURE.2.8", "MEASURE.2.11", "MEASURE.3.1",
            "MANAGE.1.2", "MANAGE.2.4", "MANAGE.5.1", "MANAGE.5.2"
        ]

        result = build_cross_mapping(eu_articles, nist_subcategories)

        # Should have substantial mappings
        assert len(result["eu_to_nist"]) > 5
        assert len(result["nist_to_eu"]) > 10

    def test_build_mapping_result_structure(self):
        """Test that result has correct structure"""
        eu_articles = [14]
        nist_subcategories = ["MAP.3.5"]

        result = build_cross_mapping(eu_articles, nist_subcategories)

        assert isinstance(result, dict)
        assert "eu_to_nist" in result
        assert "nist_to_eu" in result
        assert isinstance(result["eu_to_nist"], dict)
        assert isinstance(result["nist_to_eu"], dict)


class TestGetRelatedNistSubcategories:
    """Test get_related_nist_subcategories function"""

    def test_get_related_nist_for_article_9(self):
        """Test getting NIST subcategories for Article 9 (Risk Management)"""
        result = get_related_nist_subcategories(9)

        assert isinstance(result, list)
        assert len(result) > 0
        # Article 9 (Risk Management) should map to GOVERN and MAP subcategories
        assert any("GOVERN" in item for item in result)

    def test_get_related_nist_for_article_14(self):
        """Test getting NIST subcategories for Article 14 (Human Oversight)"""
        result = get_related_nist_subcategories(14)

        assert isinstance(result, list)
        assert len(result) > 0
        # Should include MAP.3.5 which relates to human oversight
        assert "MAP.3.5" in result

    def test_get_related_nist_for_nonexistent_article(self):
        """Test getting NIST subcategories for non-existent article"""
        result = get_related_nist_subcategories(999)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_related_nist_returns_list(self):
        """Test that function always returns a list"""
        for article_num in [5, 6, 9, 10, 14, 15]:
            result = get_related_nist_subcategories(article_num)
            assert isinstance(result, list)


class TestGetRelatedEuArticles:
    """Test get_related_eu_articles function"""

    def test_get_related_eu_for_govern_1_1(self):
        """Test getting EU articles for GOVERN.1.1"""
        result = get_related_eu_articles("GOVERN.1.1")

        assert isinstance(result, list)
        assert len(result) > 0
        # GOVERN.1.1 (legal requirements) should map to Articles 5, 6
        assert "Article_5" in result or "Article_6" in result

    def test_get_related_eu_for_map_3_5(self):
        """Test getting EU articles for MAP.3.5 (Human Oversight)"""
        result = get_related_eu_articles("MAP.3.5")

        assert isinstance(result, list)
        assert len(result) > 0
        # Should include Article_14 (Human Oversight)
        assert "Article_14" in result

    def test_get_related_eu_for_nonexistent_subcategory(self):
        """Test getting EU articles for non-existent subcategory"""
        result = get_related_eu_articles("UNKNOWN.99.99")

        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_related_eu_returns_list(self):
        """Test that function always returns a list"""
        subcategories = [
            "GOVERN.1.1", "MAP.3.5", "MEASURE.2.4", "MANAGE.2.4"
        ]

        for subcat in subcategories:
            result = get_related_eu_articles(subcat)
            assert isinstance(result, list)


class TestGetAllEuArticles:
    """Test get_all_eu_articles function"""

    def test_get_all_eu_articles_returns_list(self):
        """Test that function returns a list"""
        result = get_all_eu_articles()

        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_all_eu_articles_format(self):
        """Test that all articles have correct format"""
        result = get_all_eu_articles()

        for article in result:
            assert isinstance(article, str)
            assert article.startswith("Article_")

    def test_get_all_eu_articles_includes_key_articles(self):
        """Test that key articles are included"""
        result = get_all_eu_articles()

        assert "Article_9" in result
        assert "Article_14" in result
        assert "Article_15" in result


class TestGetAllNistSubcategories:
    """Test get_all_nist_subcategories function"""

    def test_get_all_nist_subcategories_returns_list(self):
        """Test that function returns a list"""
        result = get_all_nist_subcategories()

        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_all_nist_subcategories_format(self):
        """Test that all subcategories have correct format"""
        result = get_all_nist_subcategories()

        for subcat in result:
            assert isinstance(subcat, str)
            assert "." in subcat
            # Should start with a function name
            assert any(subcat.startswith(func) for func in ["GOVERN", "MAP", "MEASURE", "MANAGE"])

    def test_get_all_nist_subcategories_includes_key_items(self):
        """Test that key subcategories are included"""
        result = get_all_nist_subcategories()

        assert "GOVERN.1.1" in result
        assert "MAP.3.5" in result
        assert "MEASURE.2.4" in result


class TestMappingIntegration:
    """Integration tests for cross-framework mapping"""

    def test_complete_mapping_workflow(self):
        """Test complete workflow of building and using mappings"""
        # Scenario: High-risk AI system
        eu_articles = [9, 10, 12, 14, 15]
        nist_subcategories = [
            "GOVERN.1.1", "GOVERN.1.3",
            "MAP.1.1", "MAP.3.5",
            "MEASURE.2.4", "MEASURE.2.5",
            "MANAGE.1.2"
        ]

        # Build cross-mapping
        mapping = build_cross_mapping(eu_articles, nist_subcategories)

        # Verify structure
        assert "eu_to_nist" in mapping
        assert "nist_to_eu" in mapping

        # Verify Article 14 (Human Oversight) has mappings
        if "Article_14" in mapping["eu_to_nist"]:
            related_nist = mapping["eu_to_nist"]["Article_14"]
            # Should include MAP.3.5
            assert "MAP.3.5" in related_nist

        # Verify MAP.3.5 maps back to Article 14
        if "MAP.3.5" in mapping["nist_to_eu"]:
            related_eu = mapping["nist_to_eu"]["MAP.3.5"]
            assert "Article_14" in related_eu

    def test_high_risk_system_mapping(self):
        """Test mapping for a typical high-risk AI system"""
        # High-risk system: applicable EU articles
        eu_articles = [8, 9, 10, 11, 12, 13, 14, 15, 26, 27]

        # Comprehensive NIST coverage
        nist_subcategories = [
            "GOVERN.1.1", "GOVERN.1.2", "GOVERN.1.3", "GOVERN.1.6",
            "GOVERN.3.2", "GOVERN.4.2",
            "MAP.1.1", "MAP.2.3", "MAP.3.5", "MAP.5.1",
            "MEASURE.2.3", "MEASURE.2.4", "MEASURE.2.5",
            "MEASURE.2.7", "MEASURE.2.8", "MEASURE.3.1",
            "MANAGE.1.2", "MANAGE.2.4", "MANAGE.5.1"
        ]

        mapping = build_cross_mapping(eu_articles, nist_subcategories)

        # Should have comprehensive mappings
        assert len(mapping["eu_to_nist"]) >= 5
        assert len(mapping["nist_to_eu"]) >= 10

        # Key mappings should exist
        # Article 9 (Risk Management) -> GOVERN/MAP/MEASURE/MANAGE
        if "Article_9" in mapping["eu_to_nist"]:
            assert len(mapping["eu_to_nist"]["Article_9"]) > 0

    def test_minimal_risk_system_mapping(self):
        """Test mapping for a minimal risk AI system"""
        # Minimal risk: fewer applicable articles
        eu_articles = [50]  # Only transparency

        # Basic NIST coverage
        nist_subcategories = [
            "GOVERN.1.1", "GOVERN.4.2",
            "MEASURE.2.8"
        ]

        mapping = build_cross_mapping(eu_articles, nist_subcategories)

        # Should have limited mappings
        assert len(mapping["eu_to_nist"]) <= 2
        assert len(mapping["nist_to_eu"]) <= 3

    def test_verify_mapping_consistency_across_all_articles(self):
        """Test that all mappings are internally consistent"""
        all_eu = get_all_eu_articles()
        all_nist = get_all_nist_subcategories()

        for eu_article in all_eu:
            article_num = int(eu_article.split("_")[1])
            related_nist = get_related_nist_subcategories(article_num)

            # Each related NIST should map back
            for nist_subcat in related_nist:
                if nist_subcat in all_nist:
                    related_eu = get_related_eu_articles(nist_subcat)
                    # Should map back to original article (or related ones)
                    assert any(eu in related_eu for eu in [eu_article])
