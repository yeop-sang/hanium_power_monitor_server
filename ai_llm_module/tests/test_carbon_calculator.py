import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.carbon_calculator import CarbonCalculator, calculate_carbon_emissions, get_available_emission_factors

class TestCarbonCalculator:
    """Test cases for CarbonCalculator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = CarbonCalculator()
        
        # Create sample data
        self.sample_data = pd.DataFrame({
            'electric': [100, 150, 200, 120, 180],  # mA values
            'timestamp': [
                datetime.now() - timedelta(hours=i) for i in range(4, -1, -1)
            ]
        })
        
        self.daily_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=5),
            'total_electric': [1000, 1200, 800, 1500, 900],  # mA totals
            'avg_temp': [20.5, 22.1, 18.3, 25.0, 21.2],
            'avg_humidity': [45, 50, 48, 52, 46],
            'avg_brightness': [300, 350, 280, 400, 320]
        })
    
    def test_initialization_default(self):
        """Test default initialization with Korea grid factor."""
        calc = CarbonCalculator()
        assert calc.emission_factor == 0.478
        assert calc.factor_source == 'korea_grid'
    
    def test_initialization_custom_string(self):
        """Test initialization with custom string factor."""
        calc = CarbonCalculator('renewable')
        assert calc.emission_factor == 0.048
        assert calc.factor_source == 'renewable'
    
    def test_initialization_custom_numeric(self):
        """Test initialization with custom numeric factor."""
        calc = CarbonCalculator(0.5)
        assert calc.emission_factor == 0.5
        assert calc.factor_source == 'custom'
    
    def test_initialization_invalid_factor(self):
        """Test initialization with invalid factor raises error."""
        with pytest.raises(ValueError):
            CarbonCalculator('invalid_factor')
    
    def test_calculate_carbon_emissions_basic(self):
        """Test basic carbon emission calculation."""
        result = self.calculator.calculate_carbon_emissions(self.sample_data)
        
        # Check that required columns are added
        assert 'power_watts' in result.columns
        assert 'energy_kwh' in result.columns
        assert 'carbon_emissions_kg' in result.columns
        assert 'carbon_emissions_g' in result.columns
        assert 'carbon_factor_used' in result.columns
        
        # Check that values are positive
        assert all(result['power_watts'] >= 0)
        assert all(result['energy_kwh'] >= 0)
        assert all(result['carbon_emissions_kg'] >= 0)
        
        # Check factor is correctly applied
        assert all(result['carbon_factor_used'] == 0.478)
    
    def test_calculate_carbon_emissions_empty_data(self):
        """Test calculation with empty DataFrame."""
        empty_df = pd.DataFrame()
        result = self.calculator.calculate_carbon_emissions(empty_df)
        assert result.empty
    
    def test_calculate_carbon_emissions_missing_column(self):
        """Test calculation with missing electric column."""
        invalid_data = pd.DataFrame({'temperature': [20, 21, 22]})
        with pytest.raises(ValueError):
            self.calculator.calculate_carbon_emissions(invalid_data)
    
    def test_calculate_daily_emissions(self):
        """Test daily carbon emission calculation."""
        result = self.calculator.calculate_daily_emissions(self.daily_data)
        
        # Check that daily carbon columns are added
        assert 'avg_power_watts' in result.columns
        assert 'daily_energy_kwh' in result.columns
        assert 'daily_carbon_kg' in result.columns
        assert 'daily_carbon_g' in result.columns
        
        # Check calculations are reasonable
        assert all(result['daily_carbon_kg'] > 0)
        assert all(result['daily_carbon_g'] == result['daily_carbon_kg'] * 1000)
    
    def test_calculate_monthly_emissions(self):
        """Test monthly carbon emission calculation."""
        monthly_data = pd.DataFrame({
            'year_month': ['2024-01', '2024-02'],
            'total_electric': [30000, 35000],
            'reading_count': [4320, 4032]  # Approximate readings per month
        })
        
        result = self.calculator.calculate_monthly_emissions(monthly_data)
        
        # Check that monthly carbon columns are added
        assert 'avg_power_watts' in result.columns
        assert 'monthly_energy_kwh' in result.columns
        assert 'monthly_carbon_kg' in result.columns
        assert 'monthly_carbon_g' in result.columns
        
        # Check calculations are reasonable
        assert all(result['monthly_carbon_kg'] > 0)
    
    def test_get_emission_factor_info(self):
        """Test emission factor information retrieval."""
        info = self.calculator.get_emission_factor_info()
        
        assert 'factor_value' in info
        assert 'factor_source' in info
        assert 'unit' in info
        assert 'available_factors' in info
        
        assert info['factor_value'] == 0.478
        assert info['unit'] == 'kgCO2/kWh'
    
    def test_calculate_carbon_trends(self):
        """Test carbon trend calculation."""
        # First calculate emissions
        carbon_data = self.calculator.calculate_daily_emissions(self.daily_data)
        
        # Then calculate trends
        trends = self.calculator.calculate_carbon_trends(carbon_data, 'daily')
        
        # Check that trend statistics are present
        assert 'total_emissions_kg' in trends
        assert 'average_emissions_kg' in trends
        assert 'min_emissions_kg' in trends
        assert 'max_emissions_kg' in trends
        assert 'data_points' in trends
        assert 'emission_factor_used' in trends
        
        # Check values are reasonable
        assert trends['total_emissions_kg'] > 0
        assert trends['data_points'] == len(carbon_data)
        assert trends['emission_factor_used'] == 0.478
    
    def test_calculate_carbon_trends_empty_data(self):
        """Test trend calculation with empty data."""
        empty_df = pd.DataFrame()
        trends = self.calculator.calculate_carbon_trends(empty_df)
        assert trends == {}
    
    def test_power_conversion_calculation(self):
        """Test power conversion from mA to watts."""
        test_data = pd.DataFrame({
            'electric': [1000],  # 1000 mA
            'timestamp': [datetime.now()]
        })
        
        result = self.calculator.calculate_carbon_emissions(test_data)
        
        # Expected: 1000 mA * 5V / 1000 = 5 watts
        expected_watts = 5.0
        assert abs(result['power_watts'].iloc[0] - expected_watts) < 0.01


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_calculate_carbon_emissions_function(self):
        """Test convenience function."""
        test_data = pd.DataFrame({
            'electric': [100, 200, 150],
            'timestamp': pd.date_range('2024-01-01', periods=3, freq='H')
        })
        
        result = calculate_carbon_emissions(test_data)
        
        assert 'carbon_emissions_kg' in result.columns
        assert len(result) == 3
    
    def test_get_available_emission_factors(self):
        """Test getting available emission factors."""
        factors = get_available_emission_factors()
        
        assert isinstance(factors, dict)
        assert 'korea_grid' in factors
        assert 'renewable' in factors
        assert factors['korea_grid'] == 0.478


if __name__ == '__main__':
    pytest.main([__file__]) 