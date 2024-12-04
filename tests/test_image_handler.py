import pytest
from InStoreGPTs.services.image_handler import ImageHandler
from unittest.mock import patch, MagicMock

# Mock ImageHandler instance
@pytest.fixture
def image_handler():
    return ImageHandler(csv_file="example_data/adidas/adidas_products.csv", upload_folder="uploads")

# Test reverse_image_search
def test_reverse_image_search(image_handler):
    # Test input caption
    test_caption = "Black sneakers for running"

    # Perform reverse image search
    results, error = image_handler.reverse_image_search(test_caption, top_n=2)

    # Assertions
    assert error is None, f"Unexpected error: {error}"
    assert results is not None, "Results should not be None"
    assert len(results) == 2, "Should return the top 2 results"

    # Check that the top result matches the most similar caption
    top_result = results.iloc[0]
    expected_keywords = ["black", "running", "shoes"]

    # Assert all keywords are present in the IMAGE_CAPTION
    for keyword in expected_keywords:
        assert keyword in top_result["IMAGE_CAPTION"].lower(), f"Keyword '{keyword}' should be in the top result caption"


    # Check that the product name and details are correctly retrieved
    assert (
        top_result["PRODUCT_NAME"] == "Pureboost 21 Shoes"
    ), "Product name should match the most similar caption"


# Test caption generation
def test_generate_caption(image_handler):
    # Simulate an image path
    image_path = "uploads/black_running_shoes.jpg"

    # Call generate_caption
    caption, error = image_handler.generate_caption(image_path)

    # Assertions
    assert error is None, f"Unexpected error: {error}"
    assert caption is not None, "Caption should not be None"

    # Check for expected keywords in the caption
    expected_keywords = ["black", "running", "shoes"]
    for keyword in expected_keywords:
        assert keyword in caption.lower(), f"Keyword '{keyword}' should be in the caption"


