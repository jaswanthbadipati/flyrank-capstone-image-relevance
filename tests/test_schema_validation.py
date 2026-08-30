"""Tests for Pydantic Schema Validation and Vision Structured Outputs."""
import pytest
from pydantic import ValidationError
from app.models.schemas import VisionOutput

def test_valid_vision_output_schema():
    """Test valid structured vision output passes schema validation."""
    valid_data = {
        "subject": "red fox",
        "category": "animal",
        "attributes": ["orange fur", "wildlife", "forest"],
        "caption": "A red fox standing in a temperate forest",
        "confidence": 0.94
    }
    obj = VisionOutput.model_validate(valid_data)
    assert obj.subject == "red fox"
    assert obj.category == "animal"
    assert len(obj.attributes) == 3
    assert obj.confidence == 0.94

def test_invalid_confidence_range():
    """Test out-of-range confidence scores raise validation error."""
    invalid_data = {
        "subject": "red fox",
        "category": "animal",
        "attributes": ["orange fur"],
        "caption": "A red fox in a forest",
        "confidence": 1.45  # Must be <= 1.0
    }
    with pytest.raises(ValidationError):
        VisionOutput.model_validate(invalid_data)

    invalid_negative = {
        "subject": "red fox",
        "category": "animal",
        "attributes": ["orange fur"],
        "caption": "A red fox in a forest",
        "confidence": -0.1  # Must be >= 0.0
    }
    with pytest.raises(ValidationError):
        VisionOutput.model_validate(invalid_negative)

def test_missing_required_fields():
    """Test missing required schema fields fail validation."""
    incomplete_data = {
        "subject": "red fox",
        # category is missing
        "attributes": ["orange fur"],
        "confidence": 0.90
    }
    with pytest.raises(ValidationError):
        VisionOutput.model_validate(incomplete_data)

def test_empty_string_validation():
    """Test empty or whitespace strings fail validation."""
    empty_subject = {
        "subject": "   ",
        "category": "animal",
        "attributes": [],
        "caption": "A caption",
        "confidence": 0.90
    }
    with pytest.raises(ValidationError):
        VisionOutput.model_validate(empty_subject)
