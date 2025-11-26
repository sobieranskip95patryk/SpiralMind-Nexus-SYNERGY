import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
"""
Tests for quantum_core module
"""

import pytest
from spiral.core.quantum_core import (
    fib, shannon_entropy, text_complexity, 
    apply_formula_S, quantum_score
)


class TestFibonacci:
    """Test Fibonacci function"""
    
    def test_fib_base_cases(self):
        assert fib(0) == 0
        assert fib(1) == 1
    
    def test_fib_sequence(self):
        expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
        for i, expected_val in enumerate(expected):
            assert fib(i) == expected_val
    
    def test_fib_negative_raises_error(self):
        with pytest.raises(ValueError, match="n must be >= 0"):
            fib(-1)


class TestShannonEntropy:
    """Test Shannon entropy calculation"""
    
    def test_empty_string(self):
        assert shannon_entropy("") == 0.0
    
    def test_single_character(self):
        assert shannon_entropy("a") == 0.0
        assert shannon_entropy("aaaa") == 0.0
    
    def test_two_characters_equal(self):
        # Equal distribution should give high entropy
        entropy = shannon_entropy("ab")
        assert entropy == 1.0  # log2(2) = 1
    
    def test_entropy_increases_with_diversity(self):
        low_diversity = shannon_entropy("aaab")
        high_diversity = shannon_entropy("abcd")
        assert high_diversity > low_diversity


class TestTextComplexity:
    """Test text complexity analysis"""
    
    def test_empty_text(self):
        result = text_complexity("")
        expected = {
            "len_chars": 0, "len_words": 0, "vocab": 0, 
            "entropy": 0.0, "avg_word_len": 0.0, "complexity_score": 0.0
        }
        assert result == expected
    
    def test_simple_text(self):
        result = text_complexity("hello world")
        assert result["len_chars"] == 11
        assert result["len_words"] == 2
        assert result["vocab"] == 2
        assert result["avg_word_len"] == 5.0
        assert 0.0 <= result["complexity_score"] <= 1.0
    
    def test_complex_text_has_higher_score(self):
        simple = text_complexity("hello hello hello")
        complex_text = text_complexity("Sophisticated vocabulary demonstrates extraordinary comprehension capabilities")
        
        assert complex_text["complexity_score"] > simple["complexity_score"]


class TestApplyFormulaS:
    """Test GOKAI S formula"""
    
    def test_basic_calculation(self):
        params = {"W": 7, "M": 6, "D": 4, "C": 5, "A": 8, "E": 6, "T": 3}
        result = apply_formula_S(5, params)
        
        assert "S9" in result
        assert "S_pi" in result
        assert "Fn" in result
        assert "WYNIK" in result
        
        # S9 should be sum of params reduced to 1-9
        # expected: 39 % 9 = 3, but we use 9 for 0
        assert result["S9"] == 3
        
        # Fn should be fib(5) = 5
        assert result["Fn"] == 5
    
    def test_different_params(self):
        params1 = {"A": 1, "B": 2}  # sum = 3, S9 = 3
        params2 = {"A": 9, "B": 9}  # sum = 18, S9 = 9
        
        result1 = apply_formula_S(1, params1)
        result2 = apply_formula_S(1, params2)
        
        assert result1["S9"] == 3
        assert result2["S9"] == 9
        assert result2["WYNIK"] > result1["WYNIK"]


class TestQuantumScore:
    """Test quantum scoring function"""
    
    def test_empty_text(self):
        result = quantum_score("")
        assert result["quantum_score"] == 0.0
        assert result["text_complexity"] == 0.0
    
    def test_simple_text(self):
        result = quantum_score("hello world")
        assert 0.0 <= result["quantum_score"] <= 1.0
        assert "entropy" in result
        assert "s_formula_result" in result
        assert "fibonacci_component" in result
    
    def test_complex_text_higher_score(self):
        simple = quantum_score("test")
        complex_text = quantum_score("This sophisticated analysis demonstrates quantum computational complexity")
        
        # Complex text should generally score higher
        assert complex_text["text_complexity"] >= simple["text_complexity"]