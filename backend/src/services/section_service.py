#!/usr/bin/env python3
"""
Section service for Personal Finance Management Application.
Provides business logic for section operations.
"""

from typing import List, Optional, Dict, Any
import sys
from pathlib import Path

# Add the backend/src directory to Python path for absolute imports
backend_src_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_src_path))

from models.section import Section


class SectionService:
    """Service class for section business logic."""

    @staticmethod
    def create_section(data: Dict[str, Any]) -> Section:
        """Create a new section."""
        card_id = data.get('card_id')
        name = data.get('name')
        initial_balance = data.get('initial_balance', 0.00)

        # Create section instance
        section = Section(
            card_id=card_id,
            name=name,
            initial_balance=initial_balance
        )

        # Validate and save
        return section.save()

    @staticmethod
    def get_section_by_id(section_id: int) -> Optional[Section]:
        """Get a section by ID."""
        try:
            section_id = int(section_id)
        except (ValueError, TypeError):
            raise ValueError("Invalid section ID format")

        return Section.find_by_id(section_id)

    @staticmethod
    def get_sections_by_card_id(card_id: int) -> List[Section]:
        """Get all sections for a specific card."""
        try:
            card_id = int(card_id)
        except (ValueError, TypeError):
            raise ValueError("Invalid card ID format")

        return Section.find_by_card_id(card_id)

    @staticmethod
    def get_all_sections() -> List[Section]:
        """Get all sections."""
        return Section.find_all()

    @staticmethod
    def update_section(section_id: int, data: Dict[str, Any]) -> Section:
        """Update an existing section."""
        try:
            section_id = int(section_id)
        except (ValueError, TypeError):
            raise ValueError("Invalid section ID format")

        # Find existing section
        section = Section.find_by_id(section_id)
        if not section:
            raise ValueError(f"Section with ID {section_id} not found")

        # Update allowed fields
        if 'name' in data:
            section.name = data['name']
        if 'initial_balance' in data:
            section.initial_balance = data['initial_balance']

        # Save updated section
        return section.save()

    @staticmethod
    def delete_section(section_id: int) -> bool:
        """Delete a section."""
        try:
            section_id = int(section_id)
        except (ValueError, TypeError):
            raise ValueError("Invalid section ID format")

        # Find existing section
        section = Section.find_by_id(section_id)
        if not section:
            raise ValueError(f"Section with ID {section_id} not found")

        section.delete()
        return True

    @staticmethod
    def validate_section_data(data: Dict[str, Any], is_update: bool = False) -> List[str]:
        """Validate section data and return list of errors."""
        errors = []

        if not is_update:
            # Required fields for creation
            if not data.get('name'):
                errors.append("Section name is required")
            if not data.get('card_id'):
                errors.append("Card ID is required")

        # Validate numeric fields
        if 'initial_balance' in data:
            try:
                float(data['initial_balance'])
            except (ValueError, TypeError):
                errors.append("Initial balance must be a number")

        return errors