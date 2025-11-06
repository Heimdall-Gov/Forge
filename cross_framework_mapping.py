"""
Cross-Framework Mapping between EU AI Act and NIST AI RMF
This implements the mapping table from PRD Section 13.5
"""

from typing import Dict, List

# EU AI Act Article to NIST AI RMF Subcategory Mapping
EU_TO_NIST_MAPPING: Dict[str, List[str]] = {
    "Article_5": ["GOVERN.1.1"],  # Prohibited practices → Legal requirements
    "Article_6": ["GOVERN.1.1", "MAP.1.1"],  # Classification → Legal + context
    "Article_8": ["GOVERN.1.2", "GOVERN.1.3"],  # Compliance with requirements
    "Article_9": ["GOVERN.1.3", "MAP.1.1", "MAP.5.1", "MEASURE.3.1", "MANAGE.1.2"],  # Risk management
    "Article_10": ["MAP.2.3", "MEASURE.2.3", "MEASURE.2.11"],  # Data governance
    "Article_11": ["GOVERN.1.6", "MAP.2.3", "MANAGE.5.1"],  # Technical documentation
    "Article_12": ["GOVERN.1.6", "MEASURE.2.4", "MANAGE.5.1"],  # Record-keeping
    "Article_13": ["GOVERN.4.2", "MEASURE.2.8", "MANAGE.5.2"],  # Transparency
    "Article_14": ["GOVERN.3.2", "MAP.3.5", "MANAGE.2.4"],  # Human oversight
    "Article_15": ["MEASURE.2.5", "MEASURE.2.6", "MEASURE.2.7", "MEASURE.2.9"],  # Accuracy, robustness, security
    "Article_26": ["MANAGE.2.4", "MEASURE.2.4", "GOVERN.2.1"],  # Deployer obligations
    "Article_27": ["MAP.3.5", "GOVERN.3.2", "MAP.3.1"],  # Fundamental rights impact assessment
    "Article_50": ["GOVERN.4.2", "MEASURE.2.8", "MANAGE.5.2"],  # Transparency (limited risk)
}

# NIST AI RMF Subcategory to EU AI Act Article Mapping
NIST_TO_EU_MAPPING: Dict[str, List[str]] = {
    # GOVERN
    "GOVERN.1.1": ["Article_5", "Article_6"],
    "GOVERN.1.2": ["Article_8"],
    "GOVERN.1.3": ["Article_8", "Article_9"],
    "GOVERN.1.6": ["Article_11", "Article_12"],
    "GOVERN.2.1": ["Article_26"],
    "GOVERN.3.2": ["Article_14", "Article_27"],
    "GOVERN.4.2": ["Article_13", "Article_50"],

    # MAP
    "MAP.1.1": ["Article_6", "Article_9"],
    "MAP.2.3": ["Article_10", "Article_11"],
    "MAP.3.1": ["Article_27"],
    "MAP.3.5": ["Article_14", "Article_27"],
    "MAP.5.1": ["Article_9"],

    # MEASURE
    "MEASURE.2.3": ["Article_10"],
    "MEASURE.2.4": ["Article_12", "Article_26"],
    "MEASURE.2.5": ["Article_15"],
    "MEASURE.2.6": ["Article_15"],
    "MEASURE.2.7": ["Article_15"],
    "MEASURE.2.8": ["Article_13", "Article_50"],
    "MEASURE.2.9": ["Article_15"],
    "MEASURE.2.11": ["Article_10"],
    "MEASURE.3.1": ["Article_9"],

    # MANAGE
    "MANAGE.1.2": ["Article_9"],
    "MANAGE.2.4": ["Article_14", "Article_26"],
    "MANAGE.5.1": ["Article_11", "Article_12"],
    "MANAGE.5.2": ["Article_13", "Article_50"],
}


def build_cross_mapping(
    eu_articles: List[int],
    nist_subcategories: List[str]
) -> Dict[str, Dict[str, List[str]]]:
    """
    Build cross-framework mapping based on applicable articles and subcategories.

    Args:
        eu_articles: List of applicable EU AI Act article numbers (e.g., [9, 10, 14])
        nist_subcategories: List of applicable NIST subcategories (e.g., ["GOVERN.1.1", "MAP.3.5"])

    Returns:
        Dictionary with two mappings: eu_to_nist and nist_to_eu
    """
    mapping = {
        "eu_to_nist": {},
        "nist_to_eu": {}
    }

    # Build EU to NIST mapping
    for article_num in eu_articles:
        article_key = f"Article_{article_num}"
        if article_key in EU_TO_NIST_MAPPING:
            # Only include NIST subcategories that are actually applicable
            related_nist = [
                nist for nist in EU_TO_NIST_MAPPING[article_key]
                if nist in nist_subcategories
            ]
            if related_nist:
                mapping["eu_to_nist"][article_key] = related_nist

    # Build NIST to EU mapping
    for nist_subcat in nist_subcategories:
        if nist_subcat in NIST_TO_EU_MAPPING:
            # Only include EU articles that are actually applicable
            related_eu = [
                article for article in NIST_TO_EU_MAPPING[nist_subcat]
                if int(article.split("_")[1]) in eu_articles
            ]
            if related_eu:
                mapping["nist_to_eu"][nist_subcat] = related_eu

    return mapping


def get_related_nist_subcategories(eu_article: int) -> List[str]:
    """
    Get all NIST subcategories related to a specific EU AI Act article.

    Args:
        eu_article: EU AI Act article number

    Returns:
        List of related NIST subcategories
    """
    article_key = f"Article_{eu_article}"
    return EU_TO_NIST_MAPPING.get(article_key, [])


def get_related_eu_articles(nist_subcategory: str) -> List[str]:
    """
    Get all EU AI Act articles related to a specific NIST subcategory.

    Args:
        nist_subcategory: NIST subcategory ID (e.g., "GOVERN.1.1")

    Returns:
        List of related EU AI Act article keys (e.g., ["Article_5", "Article_6"])
    """
    return NIST_TO_EU_MAPPING.get(nist_subcategory, [])


def get_all_eu_articles() -> List[str]:
    """Get all EU AI Act articles that have mappings"""
    return list(EU_TO_NIST_MAPPING.keys())


def get_all_nist_subcategories() -> List[str]:
    """Get all NIST subcategories that have mappings"""
    return list(NIST_TO_EU_MAPPING.keys())


# Example usage
if __name__ == "__main__":
    # Example: Build mapping for a high-risk AI system
    applicable_eu_articles = [9, 10, 12, 14, 15]
    applicable_nist_subcategories = [
        "GOVERN.1.1", "GOVERN.1.2", "GOVERN.3.2",
        "MAP.1.1", "MAP.3.5", "MAP.5.1",
        "MEASURE.2.4", "MEASURE.2.11",
        "MANAGE.1.2", "MANAGE.2.4"
    ]

    mapping = build_cross_mapping(applicable_eu_articles, applicable_nist_subcategories)

    print("EU to NIST Mapping:")
    for eu_article, nist_list in mapping["eu_to_nist"].items():
        print(f"  {eu_article}: {nist_list}")

    print("\nNIST to EU Mapping:")
    for nist_subcat, eu_list in mapping["nist_to_eu"].items():
        print(f"  {nist_subcat}: {eu_list}")
