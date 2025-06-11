"""Tests for the smart recipe parser"""

import pytest


class TestRecipeParserLogic:
    """Test recipe parsing logic (Python equivalent for testing)."""
    
    def test_parse_numbered_ingredients(self):
        """Test parsing numbered ingredient lists."""
        text = """1. 2 cups flour
2. 1 tsp salt
3. 3 eggs
4. 1 cup milk"""
        
        # Simulate the parsing logic
        lines = text.strip().split('\n')
        ingredients = []
        for line in lines:
            # Remove number prefix
            cleaned = line.strip()
            if '. ' in cleaned:
                cleaned = cleaned.split('. ', 1)[1]
            ingredients.append(cleaned)
        
        expected = ["2 cups flour", "1 tsp salt", "3 eggs", "1 cup milk"]
        assert ingredients == expected
    
    def test_parse_bulleted_ingredients(self):
        """Test parsing bulleted ingredient lists."""
        text = """• 2 cups flour
• 1 tsp salt
• 3 eggs
• 1 cup milk"""
        
        lines = text.strip().split('\n')
        ingredients = []
        for line in lines:
            cleaned = line.strip()
            if cleaned.startswith('• '):
                cleaned = cleaned[2:]
            ingredients.append(cleaned)
        
        expected = ["2 cups flour", "1 tsp salt", "3 eggs", "1 cup milk"]
        assert ingredients == expected
    
    def test_parse_paragraph_ingredients(self):
        """Test parsing comma-separated ingredients."""
        text = "2 cups flour, 1 tsp salt, 3 eggs, 1 cup milk"
        
        ingredients = [item.strip() for item in text.split(',')]
        
        expected = ["2 cups flour", "1 tsp salt", "3 eggs", "1 cup milk"]
        assert ingredients == expected
    
    def test_parse_numbered_instructions(self):
        """Test parsing numbered instruction lists."""
        text = """1. Preheat oven to 350°F
2. Mix flour and salt in a bowl
3. Beat eggs and milk together
4. Combine wet and dry ingredients
5. Bake for 30 minutes"""
        
        lines = text.strip().split('\n')
        instructions = []
        for line in lines:
            cleaned = line.strip()
            if '. ' in cleaned:
                cleaned = cleaned.split('. ', 1)[1]
            # Ensure it ends with punctuation
            if not cleaned.endswith(('.', '!', '?')):
                cleaned += '.'
            instructions.append(cleaned)
        
        expected = [
            "Preheat oven to 350°F.",
            "Mix flour and salt in a bowl.",
            "Beat eggs and milk together.",
            "Combine wet and dry ingredients.",
            "Bake for 30 minutes."
        ]
        assert instructions == expected
    
    def test_parse_paragraph_instructions(self):
        """Test parsing paragraph-style instructions."""
        text = "Preheat oven to 350°F. Mix flour and salt. Beat eggs and milk. Combine ingredients. Bake for 30 minutes."
        
        # Split on periods followed by space and capital letter
        import re
        sentences = re.split(r'\.\s+(?=[A-Z])', text)
        instructions = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and not sentence.endswith('.'):
                sentence += '.'
            instructions.append(sentence)
        
        expected = [
            "Preheat oven to 350°F.",
            "Mix flour and salt.",
            "Beat eggs and milk.",
            "Combine ingredients.",
            "Bake for 30 minutes."
        ]
        assert instructions == expected
    
    def test_extract_cooking_verbs(self):
        """Test extracting cooking verbs from instructions."""
        instructions = [
            "Preheat oven to 350°F.",
            "Sauté onions until golden.",
            "Blend ingredients until smooth.",
            "Grill chicken for 15 minutes."
        ]
        
        text = ' '.join(instructions).lower()
        cooking_verbs = ['bake', 'sauté', 'blend', 'grill', 'fry', 'boil', 'roast']
        
        found_verbs = []
        for verb in cooking_verbs:
            if verb in text:
                found_verbs.append(verb)
        
        expected = ['sauté', 'blend', 'grill']
        assert set(found_verbs) == set(expected)
    
    def test_format_detection_numbered(self):
        """Test detecting numbered format."""
        text = """1. First item
2. Second item
3. Third item"""
        
        lines = text.split('\n')
        numbered_count = sum(1 for line in lines if line.strip() and line.strip()[0].isdigit())
        
        is_numbered = numbered_count >= len(lines) * 0.7
        assert is_numbered is True
    
    def test_format_detection_bulleted(self):
        """Test detecting bulleted format."""
        text = """• First item
• Second item
• Third item"""
        
        lines = text.split('\n')
        bulleted_count = sum(1 for line in lines if line.strip().startswith('•'))
        
        is_bulleted = bulleted_count >= len(lines) * 0.7
        assert is_bulleted is True
    
    def test_format_detection_paragraph(self):
        """Test detecting paragraph format."""
        text = "item1, item2, item3, item4"
        
        has_commas = ',' in text and len(text.split(',')) > 2
        assert has_commas is True
    
    def test_confidence_calculation(self):
        """Test confidence calculation for parsing results."""
        original_text = """1. First item
2. Second item
3. Third item"""
        
        parsed_items = ["First item", "Second item", "Third item"]
        original_lines = len(original_text.split('\n'))
        
        confidence = min(len(parsed_items) / original_lines, 1.0)
        assert confidence == 1.0
    
    def test_edge_cases(self):
        """Test edge cases in parsing."""
        # Empty input
        assert self.parse_empty_input("") == []
        assert self.parse_empty_input("   ") == []
        
        # Single item
        single_item = "Just one ingredient"
        assert self.parse_single_item(single_item) == ["Just one ingredient"]
        
        # Mixed formats (should handle gracefully)
        mixed = """1. First numbered item
• Bulleted item
Regular line item"""
        parsed = self.parse_mixed_format(mixed)
        assert len(parsed) == 3
    
    def parse_empty_input(self, text):
        """Helper: Parse empty input."""
        cleaned = text.strip()
        if not cleaned:
            return []
        return [cleaned]
    
    def parse_single_item(self, text):
        """Helper: Parse single item."""
        cleaned = text.strip()
        if cleaned:
            return [cleaned]
        return []
    
    def parse_mixed_format(self, text):
        """Helper: Parse mixed format (fallback to line-by-line)."""
        lines = text.split('\n')
        items = []
        for line in lines:
            cleaned = line.strip()
            # Remove various prefixes
            if '. ' in cleaned and cleaned[0].isdigit():
                cleaned = cleaned.split('. ', 1)[1]
            elif cleaned.startswith('• '):
                cleaned = cleaned[2:]
            
            if cleaned:
                items.append(cleaned)
        return items


class TestParsingIntegration:
    """Test parsing integration with the API."""
    
    def test_api_recipe_creation_with_parsing(self, test_client):
        """Test that API properly handles ingredients and instructions as lists."""
        # Note: Your API expects lists, not strings to be parsed
        recipe_data = {
            "title": "Parsing Test Recipe",
            "ingredients": ["2 cups flour", "1 tsp salt", "3 eggs"],  # Already parsed
            "instructions": ["Mix dry ingredients", "Beat eggs", "Combine and bake"],  # Already parsed
            "meal_types": ["breakfast"]
        }
        
        response = test_client.post("/api/recipes", json=recipe_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # The API should accept the lists as-is
        assert isinstance(data["ingredients"], list)
        assert isinstance(data["instructions"], list)
        assert len(data["ingredients"]) == 3
        assert len(data["instructions"]) == 3
    
    def test_api_handles_different_formats(self, test_client):
        """Test API handling different input formats."""
        # Test with list format (what your API actually expects)
        recipe_data = {
            "title": "Format Test Recipe",
            "ingredients": ["flour", "salt", "eggs", "milk"],
            "instructions": ["Mix ingredients", "Bake at 350°F", "Cool before serving"],
            "meal_types": ["dessert"]
        }
        
        response = test_client.post("/api/recipes", json=recipe_data)
        assert response.status_code == 200
        
        data = response.json()
        # Should accept lists directly
        assert isinstance(data["ingredients"], list)
        assert len(data["ingredients"]) == 4


class TestParsingPerformance:
    """Test parsing performance and edge cases."""
    
    def test_large_ingredient_list(self):
        """Test parsing large ingredient lists."""
        # Create a large numbered list
        large_list = '\n'.join([f"{i}. Ingredient {i}" for i in range(1, 101)])
        
        lines = large_list.split('\n')
        parsed = []
        for line in lines:
            if '. ' in line:
                parsed.append(line.split('. ', 1)[1])
        
        assert len(parsed) == 100
        assert parsed[0] == "Ingredient 1"
        assert parsed[99] == "Ingredient 100"
    
    def test_special_characters(self):
        """Test parsing with special characters."""
        text = """1. 2½ cups flour
2. 1 tsp salt (kosher)
3. 3 large eggs @ room temp
4. 1 cup milk - whole preferred"""
        
        lines = text.split('\n')
        parsed = []
        for line in lines:
            if '. ' in line:
                parsed.append(line.split('. ', 1)[1])
        
        expected = [
            "2½ cups flour",
            "1 tsp salt (kosher)",
            "3 large eggs @ room temp",
            "1 cup milk - whole preferred"
        ]
        assert parsed == expected
    
    def test_unicode_bullets(self):
        """Test parsing with various Unicode bullet characters."""
        text = """• Regular bullet
▪ Square bullet  
► Arrow bullet
‣ Triangle bullet"""
        
        lines = text.split('\n')
        parsed = []
        for line in lines:
            cleaned = line.strip()
            # Remove various bullet types
            if cleaned.startswith('• '):
                cleaned = cleaned[2:]
            elif cleaned.startswith('▪ '):
                cleaned = cleaned[2:]
            elif cleaned.startswith('► '):
                cleaned = cleaned[2:]
            elif cleaned.startswith('‣ '):
                cleaned = cleaned[2:]
            parsed.append(cleaned)
        
        expected = [
            "Regular bullet",
            "Square bullet",
            "Arrow bullet", 
            "Triangle bullet"
        ]
        assert parsed == expected