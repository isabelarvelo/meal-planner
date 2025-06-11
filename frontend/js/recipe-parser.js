/**
 * Smart Recipe Parser - Automatically detects format and parses ingredients/instructions
 */
const smartRecipeParser = {
    
    /**
     * Parse ingredients with automatic format detection
     * @param {string} text - Raw ingredient text
     * @returns {Array} - Array of parsed ingredients
     */
    parseIngredients(text) {
        if (!text || typeof text !== 'string') return [];
        
        const cleanText = text.trim();
        if (!cleanText) return [];
        
        // Detect the format first
        const format = this.detectIngredientsFormat(cleanText);
        
        switch (format) {
            case 'numbered':
                return this.parseNumberedIngredients(cleanText);
            case 'bulleted':
                return this.parseBulletedIngredients(cleanText);
            case 'paragraph':
                return this.parseParagraphIngredients(cleanText);
            case 'lines':
            default:
                return this.parseLineIngredients(cleanText);
        }
    },
    
    /**
     * Parse instructions with automatic format detection
     * @param {string} text - Raw instruction text
     * @returns {Array} - Array of parsed instructions
     */
    parseInstructions(text) {
        if (!text || typeof text !== 'string') return [];
        
        const cleanText = text.trim();
        if (!cleanText) return [];
        
        // Detect the format first
        const format = this.detectInstructionsFormat(cleanText);
        
        switch (format) {
            case 'numbered':
                return this.parseNumberedInstructions(cleanText);
            case 'bulleted':
                return this.parseBulletedInstructions(cleanText);
            case 'paragraph':
                return this.parseParagraphInstructions(cleanText);
            case 'lines':
            default:
                return this.parseLineInstructions(cleanText);
        }
    },
    
    /**
     * Detect ingredient format
     * @param {string} text - Text to analyze
     * @returns {string} - Format type: 'numbered', 'bulleted', 'paragraph', 'lines'
     */
    detectIngredientsFormat(text) {
        const lines = text.split('\n').map(line => line.trim()).filter(line => line);
        
        if (lines.length <= 1) {
            // Single line - check if it's a paragraph with delimiters
            if (this.isParagraphFormat(text)) {
                return 'paragraph';
            }
            return 'lines';
        }
        
        // Check for numbered format (including various number formats)
        const numberedCount = lines.filter(line => 
            /^\d+[\.\)\-\:]?\s/.test(line) || /^\(\d+\)\s/.test(line)
        ).length;
        if (numberedCount >= Math.ceil(lines.length * 0.7)) {
            return 'numbered';
        }
        
        // Check for bulleted format (including more bullet types)
        const bulletedCount = lines.filter(line => 
            /^[•\-\*\+►▪▫◦‣⁃]\s/.test(line) || /^\s*[\-\*\+]\s/.test(line)
        ).length;
        if (bulletedCount >= Math.ceil(lines.length * 0.7)) {
            return 'bulleted';
        }
        
        // Default to lines
        return 'lines';
    },
    
    /**
     * Detect instruction format
     * @param {string} text - Text to analyze
     * @returns {string} - Format type
     */
    detectInstructionsFormat(text) {
        const lines = text.split('\n').map(line => line.trim()).filter(line => line);
        
        if (lines.length <= 1) {
            // Single line or block - check if it's paragraph format
            if (this.isParagraphFormat(text)) {
                return 'paragraph';
            }
            return 'lines';
        }
        
        // Check for numbered format (more common in instructions)
        const numberedCount = lines.filter(line => /^\d+[\.\)]\s/.test(line)).length;
        if (numberedCount >= Math.ceil(lines.length * 0.6)) {
            return 'numbered';
        }
        
        // Check for bulleted format
        const bulletedCount = lines.filter(line => /^[•\-\*\+]\s/.test(line)).length;
        if (bulletedCount >= Math.ceil(lines.length * 0.6)) {
            return 'bulleted';
        }
        
        // Check if it looks like paragraph format
        if (lines.length <= 3 && this.isParagraphFormat(text)) {
            return 'paragraph';
        }
        
        // Default to lines
        return 'lines';
    },
    
    /**
     * Check if text appears to be in paragraph format
     * @param {string} text - Text to check
     * @returns {boolean}
     */
    isParagraphFormat(text) {
        // Look for multiple delimiter types that suggest paragraph format
        const delimiters = [',', ';', '|', '\t'];
        const hasMultipleDelimiters = delimiters.some(delimiter => 
            text.split(delimiter).length > 2
        );
        
        if (hasMultipleDelimiters) return true;
        
        // Look for "and" connections
        if (/\sand\s/.test(text) && text.split(/\sand\s/).length > 2) {
            return true;
        }
        
        // Look for sentence-ending punctuation followed by capital letters (for instructions)
        if (/\.\s+[A-Z]/.test(text)) {
            return true;
        }
        
        // Look for multiple sentences in a block
        const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 10);
        return sentences.length > 2;
    },
    
    /**
     * Parse numbered ingredients (1. flour, 2. eggs, etc.)
     */
    parseNumberedIngredients(text) {
        const lines = text.split('\n').map(line => line.trim()).filter(line => line);
        return lines.map(line => {
            // Remove various number prefixes: 1. 1) 1- 1: (1) 
            line = line.replace(/^\d+[\.\)\-\:]\s*/, '').trim();
            line = line.replace(/^\(\d+\)\s*/, '').trim();
            return line;
        }).filter(line => line && line.length > 1);
    },
    
    /**
     * Parse bulleted ingredients (• flour, - eggs, etc.)
     */
    parseBulletedIngredients(text) {
        const lines = text.split('\n').map(line => line.trim()).filter(line => line);
        return lines.map(line => {
            // Remove various bullet formats including unicode bullets, dashes, asterisks, plus signs
            line = line.replace(/^[•\-\*\+►▪▫◦‣⁃]\s*/, '').trim();
            // Also handle spaced bullets and tabs
            line = line.replace(/^\s*[\-\*\+]\s*/, '').trim();
            return line;
        }).filter(line => line && line.length > 1);
    },
    
    /**
     * Parse paragraph ingredients (flour, eggs, milk, etc.)
     */
    parseParagraphIngredients(text) {
        // Split on multiple delimiters: commas, semicolons, pipes, tabs, and "and"
        let ingredients = text.split(/[,;|\t]+|(?:\s+and\s+)/)
            .map(item => item.trim())
            .filter(item => item && item.length > 1);
        
        // Handle special cases like "1 cup flour and 2 eggs"
        const processedIngredients = [];
        
        for (let ingredient of ingredients) {
            // Remove common prefixes that might remain
            ingredient = ingredient.replace(/^(and|or|plus|\+)\s+/i, '').trim();
            
            // Skip empty or very short items
            if (ingredient && ingredient.length > 1) {
                processedIngredients.push(ingredient);
            }
        }
        
        return processedIngredients;
    },
    
    /**
     * Parse line-by-line ingredients
     */
    parseLineIngredients(text) {
        return text.split('\n')
            .map(line => line.trim())
            .filter(line => line && line.length > 1);
    },
    
    /**
     * Parse numbered instructions (1. Preheat oven, 2. Mix ingredients, etc.)
     */
    parseNumberedInstructions(text) {
        const lines = text.split('\n').map(line => line.trim()).filter(line => line);
        return lines.map(line => {
            // Remove various number prefixes: 1. 1) 1- 1: (1)
            line = line.replace(/^\d+[\.\)\-\:]\s*/, '').trim();
            line = line.replace(/^\(\d+\)\s*/, '').trim();
            
            // Ensure it ends with punctuation
            if (line && !/[.!?]$/.test(line)) {
                line += '.';
            }
            return line;
        }).filter(line => line && line.length > 1);
    },
    
    /**
     * Parse bulleted instructions (• Preheat oven, - Mix ingredients, etc.)
     */
    parseBulletedInstructions(text) {
        const lines = text.split('\n').map(line => line.trim()).filter(line => line);
        return lines.map(line => {
            // Remove various bullet formats including unicode bullets
            line = line.replace(/^[•\-\*\+►▪▫◦‣⁃]\s*/, '').trim();
            // Also handle spaced bullets and tabs
            line = line.replace(/^\s*[\-\*\+]\s*/, '').trim();
            
            // Ensure it ends with punctuation
            if (line && !/[.!?]$/.test(line)) {
                line += '.';
            }
            return line;
        }).filter(line => line && line.length > 1);
    },
    
    /**
     * Parse paragraph instructions (Preheat oven. Mix ingredients. Bake for 30 minutes.)
     */
    parseParagraphInstructions(text) {
        let instructions = [];
        
        // First try splitting on periods followed by space and capital letter
        let sentences = text.split(/\.\s+(?=[A-Z])/)
            .map(sentence => sentence.trim())
            .filter(sentence => sentence.length > 5);
        
        // Try other delimiters if period splitting doesn't work well
        if (sentences.length < 2) {
            // Try semicolons, pipes, or tabs as step separators
            sentences = text.split(/[;|\t]+/)
                .map(sentence => sentence.trim())
                .filter(sentence => sentence.length > 5);
        }
        
        // If still not working, try other punctuation
        if (sentences.length < 2) {
            sentences = text.split(/[.!?]+/)
                .map(sentence => sentence.trim())
                .filter(sentence => sentence.length > 5);
        }
        
        // Try splitting on "Then", "Next", "After" indicators
        if (sentences.length < 2) {
            sentences = text.split(/\.\s*(?:Then|Next|After|Finally|Meanwhile)\s+/i)
                .map(sentence => sentence.trim())
                .filter(sentence => sentence.length > 5);
        }
        
        return sentences.map(sentence => {
            // Clean up common prefixes
            sentence = sentence.replace(/^(then|next|after|finally|meanwhile)\s+/i, '').trim();
            
            // Ensure it ends with punctuation
            if (!/[.!?]$/.test(sentence)) {
                sentence += '.';
            }
            return sentence;
        }).filter(sentence => sentence && sentence.length > 1);
    },
    
    /**
     * Parse line-by-line instructions
     */
    parseLineInstructions(text) {
        return text.split('\n')
            .map(line => {
                let instruction = line.trim();
                // Ensure it ends with punctuation
                if (instruction && !/[.!?]$/.test(instruction)) {
                    instruction += '.';
                }
                return instruction;
            })
            .filter(line => line && line.length > 1);
    },
    
    /**
     * Extract cooking verbs from instructions for appliance detection
     * @param {Array|string} instructions - Instructions array or string
     * @returns {Array} - Array of cooking verbs found
     */
    extractCookingVerbs(instructions) {
        const instructionText = Array.isArray(instructions) 
            ? instructions.join(' ').toLowerCase()
            : instructions.toLowerCase();
        
        const cookingVerbs = [
            'bake', 'baking', 'roast', 'roasting', 'broil', 'broiling',
            'saute', 'sauté', 'sear', 'fry', 'frying', 'simmer', 'boil', 'boiling',
            'blend', 'blending', 'puree', 'pureeing', 'mix', 'mixing', 'beat', 'beating',
            'whip', 'whipping', 'grill', 'grilling', 'steam', 'steaming',
            'toast', 'toasting', 'microwave', 'process', 'processing', 'chop', 'chopping'
        ];
        
        const foundVerbs = [];
        cookingVerbs.forEach(verb => {
            if (instructionText.includes(verb)) {
                foundVerbs.push(verb);
            }
        });
        
        return [...new Set(foundVerbs)]; // Remove duplicates
    },
    
    /**
     * Preview parsing results for user feedback
     * @param {string} text - Text to parse
     * @param {string} type - 'ingredients' or 'instructions'
     * @returns {Object} - Parsing results with metadata
     */
    previewParsing(text, type) {
        const parseMethod = type === 'ingredients' ? 'parseIngredients' : 'parseInstructions';
        const detectMethod = type === 'ingredients' ? 'detectIngredientsFormat' : 'detectInstructionsFormat';
        
        const detectedFormat = this[detectMethod](text);
        const parsed = this[parseMethod](text);
        
        return {
            format: detectedFormat,
            items: parsed,
            count: parsed.length,
            confidence: this.calculateParsingConfidence(text, parsed, type)
        };
    },
    
    /**
     * Calculate confidence in parsing results
     * @param {string} originalText - Original text
     * @param {Array} parsed - Parsed results
     * @param {string} type - 'ingredients' or 'instructions'
     * @returns {number} - Confidence score 0-1
     */
    calculateParsingConfidence(originalText, parsed, type) {
        if (!parsed || parsed.length === 0) return 0;
        
        const originalLines = originalText.split('\n').filter(line => line.trim());
        const expectedCount = originalLines.length;
        
        // Base confidence on how close the parsed count is to expected
        let confidence = Math.min(parsed.length / expectedCount, 1);
        
        // Boost confidence if format was clearly detected
        if (type === 'ingredients') {
            const format = this.detectIngredientsFormat(originalText);
            if (format === 'numbered' || format === 'bulleted') {
                confidence = Math.min(confidence + 0.2, 1);
            }
        }
        
        return Math.round(confidence * 100) / 100; // Round to 2 decimal places
    }
};

/**
 * Real-time parsing preview component
 */
const parsingPreview = {
    /**
     * Initialize parsing preview for textareas
     */
    init() {
        this.setupIngredientsPreview();
        this.setupInstructionsPreview();
    },
    
    setupIngredientsPreview() {
        const textarea = document.getElementById('recipe-ingredients');
        if (!textarea) return;
        
        // Create preview container if it doesn't exist
        this.createPreviewContainer(textarea, 'ingredients');
        
        // Add real-time parsing
        textarea.addEventListener('input', () => {
            this.updatePreview('ingredients');
        });
    },
    
    setupInstructionsPreview() {
        const textarea = document.getElementById('recipe-instructions');
        if (!textarea) return;
        
        // Create preview container if it doesn't exist
        this.createPreviewContainer(textarea, 'instructions');
        
        // Add real-time parsing
        textarea.addEventListener('input', () => {
            this.updatePreview('instructions');
        });
    },
    
    createPreviewContainer(textarea, type) {
        const existingPreview = document.getElementById(`${type}-preview`);
        if (existingPreview) return;
        
        const preview = document.createElement('div');
        preview.id = `${type}-preview`;
        preview.className = 'parsing-preview';
        preview.style.display = 'none';
        
        textarea.parentNode.appendChild(preview);
    },
    
    updatePreview(type) {
        const textarea = document.getElementById(`recipe-${type}`);
        const preview = document.getElementById(`${type}-preview`);
        
        if (!textarea || !preview) return;
        
        const text = textarea.value.trim();
        if (!text) {
            preview.style.display = 'none';
            return;
        }
        
        const results = smartRecipeParser.previewParsing(text, type);
        
        if (results.items.length > 0) {
            this.renderPreview(preview, results, type);
            preview.style.display = 'block';
        } else {
            preview.style.display = 'none';
        }
    },
    
    renderPreview(container, results, type) {
        const listTag = type === 'instructions' ? 'ol' : 'ul';
        const formatLabel = this.getFormatLabel(results.format);
        const confidenceColor = results.confidence > 0.8 ? '#28a745' : results.confidence > 0.5 ? '#ffc107' : '#dc3545';
        
        container.innerHTML = `
            <div class="parsing-header">
                <strong style="color: ${confidenceColor};">
                    Detected: ${formatLabel} (${results.count} ${type})
                </strong>
                <span class="confidence-badge" style="background-color: ${confidenceColor};">
                    ${Math.round(results.confidence * 100)}% confidence
                </span>
            </div>
            <${listTag} class="parsing-list">
                ${results.items.map(item => `<li>${item}</li>`).join('')}
            </${listTag}>
        `;
    },
    
    getFormatLabel(format) {
        const labels = {
            'numbered': 'Numbered List',
            'bulleted': 'Bullet Points',
            'paragraph': 'Paragraph',
            'lines': 'Line by Line'
        };
        return labels[format] || 'Unknown Format';
    }
};

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    parsingPreview.init();
});