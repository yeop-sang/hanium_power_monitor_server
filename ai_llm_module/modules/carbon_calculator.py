import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Carbon emission factors (kgCO2/kWh)
# Source: Korea Energy Economics Institute (KEEI) 2023 data
CARBON_FACTORS = {
    'korea_grid': 0.478,  # Korea's average grid emission factor
    'coal': 0.82,         # Coal power plant
    'natural_gas': 0.35,  # Natural gas power plant
    'nuclear': 0.012,     # Nuclear power plant
    'renewable': 0.048,   # Renewable energy average
    'global_average': 0.475  # Global average grid emission factor
}

class CarbonCalculator:
    """Carbon emission calculator for power consumption data."""
    
    def __init__(self, emission_factor='korea_grid'):
        """Initialize carbon calculator with emission factor.
        
        Args:
            emission_factor: Carbon emission factor key or custom value (kgCO2/kWh)
        """
        if isinstance(emission_factor, str):
            if emission_factor in CARBON_FACTORS:
                self.emission_factor = CARBON_FACTORS[emission_factor]
                self.factor_source = emission_factor
            else:
                raise ValueError(f"Unknown emission factor: {emission_factor}")
        else:
            self.emission_factor = float(emission_factor)
            self.factor_source = 'custom'
        
        logger.info(f"Initialized carbon calculator with factor: {self.emission_factor} kgCO2/kWh ({self.factor_source})")
    
    def calculate_carbon_emissions(self, power_data):
        """Calculate carbon emissions from power consumption data.
        
        Args:
            power_data: DataFrame with power consumption data
                       Must contain 'electric' column (in Watts or mA)
                       
        Returns:
            DataFrame: Original data with added carbon emission columns
        """
        if power_data.empty:
            logger.warning("Empty power data provided for carbon calculation")
            return power_data
        
        result = power_data.copy()
        
        # Convert electric values to kWh based on data type
        if 'electric' not in result.columns:
            raise ValueError("Power data must contain 'electric' column")
        
        # Assume electric values are in mA (milliamperes) based on database schema
        # Convert mA to Watts assuming 5V voltage: P(W) = V(V) * I(A) = 5V * (mA/1000)
        # Then convert to kWh: kWh = W * hours / 1000
        voltage = 5.0  # Assumed voltage for IoT sensors
        
        # Calculate power in Watts
        result['power_watts'] = (result['electric'] / 1000.0) * voltage
        
        # For hourly data, calculate kWh directly
        # For more frequent data, we need to estimate duration
        if 'timestamp' in result.columns:
            result = self._calculate_energy_consumption(result)
        else:
            # Assume 1 hour duration if no timestamp
            result['energy_kwh'] = result['power_watts'] / 1000.0
        
        # Calculate carbon emissions
        result['carbon_emissions_kg'] = result['energy_kwh'] * self.emission_factor
        
        # Add additional carbon metrics
        result['carbon_emissions_g'] = result['carbon_emissions_kg'] * 1000
        result['carbon_factor_used'] = self.emission_factor
        
        logger.info(f"Calculated carbon emissions for {len(result)} records")
        return result
    
    def _calculate_energy_consumption(self, data):
        """Calculate energy consumption based on power and time intervals.
        
        Args:
            data: DataFrame with 'power_watts' and 'timestamp' columns
            
        Returns:
            DataFrame: Data with 'energy_kwh' column added
        """
        if len(data) < 2:
            # Single data point, assume 1 hour duration
            data['energy_kwh'] = data['power_watts'] / 1000.0
            return data
        
        # Sort by timestamp
        data = data.sort_values('timestamp')
        
        # Calculate time intervals between readings
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data['time_diff_hours'] = data['timestamp'].diff().dt.total_seconds() / 3600.0
        
        # For the first reading, use the interval to the next reading
        data.loc[data.index[0], 'time_diff_hours'] = data.loc[data.index[1], 'time_diff_hours']
        
        # Handle any missing or zero intervals (use 1 hour default)
        data['time_diff_hours'] = data['time_diff_hours'].fillna(1.0)
        data.loc[data['time_diff_hours'] <= 0, 'time_diff_hours'] = 1.0
        
        # Calculate energy consumption: Energy = Power * Time
        data['energy_kwh'] = (data['power_watts'] * data['time_diff_hours']) / 1000.0
        
        return data
    
    def calculate_daily_emissions(self, daily_data):
        """Calculate daily carbon emissions from aggregated daily data.
        
        Args:
            daily_data: DataFrame with daily summaries including 'total_electric'
            
        Returns:
            DataFrame: Daily data with carbon emissions
        """
        if daily_data.empty:
            logger.warning("Empty daily data provided for carbon calculation")
            return daily_data
        
        result = daily_data.copy()
        
        if 'total_electric' not in result.columns:
            raise ValueError("Daily data must contain 'total_electric' column")
        
        # Convert total electric (assumed to be in mA*readings) to kWh
        # Estimate based on average reading frequency (e.g., every 10 minutes = 144 readings/day)
        voltage = 5.0
        estimated_readings_per_day = 144  # Assuming 10-minute intervals
        
        # Calculate average power and daily energy
        result['avg_power_watts'] = (result['total_electric'] / estimated_readings_per_day / 1000.0) * voltage
        result['daily_energy_kwh'] = result['avg_power_watts'] * 24 / 1000.0
        
        # Calculate carbon emissions
        result['daily_carbon_kg'] = result['daily_energy_kwh'] * self.emission_factor
        result['daily_carbon_g'] = result['daily_carbon_kg'] * 1000
        
        logger.info(f"Calculated daily carbon emissions for {len(result)} days")
        return result
    
    def calculate_monthly_emissions(self, monthly_data):
        """Calculate monthly carbon emissions from aggregated monthly data.
        
        Args:
            monthly_data: DataFrame with monthly summaries
            
        Returns:
            DataFrame: Monthly data with carbon emissions
        """
        if monthly_data.empty:
            logger.warning("Empty monthly data provided for carbon calculation")
            return monthly_data
        
        result = monthly_data.copy()
        
        if 'total_electric' not in result.columns:
            raise ValueError("Monthly data must contain 'total_electric' column")
        
        # Similar calculation as daily, but for monthly totals
        voltage = 5.0
        
        # Use reading_count if available, otherwise estimate
        if 'reading_count' in result.columns:
            result['avg_power_watts'] = (result['total_electric'] / result['reading_count'] / 1000.0) * voltage
            result['total_hours'] = result['reading_count'] / 6  # Assuming 10-minute intervals
        else:
            # Estimate based on days in month
            days_in_month = 30  # Average
            estimated_readings_per_month = days_in_month * 144
            result['avg_power_watts'] = (result['total_electric'] / estimated_readings_per_month / 1000.0) * voltage
            result['total_hours'] = days_in_month * 24
        
        result['monthly_energy_kwh'] = result['avg_power_watts'] * result['total_hours'] / 1000.0
        result['monthly_carbon_kg'] = result['monthly_energy_kwh'] * self.emission_factor
        result['monthly_carbon_g'] = result['monthly_carbon_kg'] * 1000
        
        logger.info(f"Calculated monthly carbon emissions for {len(result)} months")
        return result
    
    def get_emission_factor_info(self):
        """Get information about the current emission factor.
        
        Returns:
            dict: Emission factor information
        """
        return {
            'factor_value': self.emission_factor,
            'factor_source': self.factor_source,
            'unit': 'kgCO2/kWh',
            'available_factors': CARBON_FACTORS
        }
    
    def calculate_carbon_trends(self, data_with_emissions, period='daily'):
        """Calculate carbon emission trends and statistics.
        
        Args:
            data_with_emissions: DataFrame with calculated carbon emissions
            period: Aggregation period ('daily', 'weekly', 'monthly')
            
        Returns:
            dict: Trend analysis results
        """
        if data_with_emissions.empty:
            return {}
        
        # Determine carbon column to analyze
        carbon_col = None
        if 'carbon_emissions_kg' in data_with_emissions.columns:
            carbon_col = 'carbon_emissions_kg'
        elif 'daily_carbon_kg' in data_with_emissions.columns:
            carbon_col = 'daily_carbon_kg'
        elif 'monthly_carbon_kg' in data_with_emissions.columns:
            carbon_col = 'monthly_carbon_kg'
        
        if carbon_col is None:
            logger.warning("No carbon emissions column found for trend analysis")
            return {}
        
        carbon_data = data_with_emissions[carbon_col].dropna()
        
        if carbon_data.empty:
            return {}
        
        # Calculate basic statistics
        stats = {
            'total_emissions_kg': float(carbon_data.sum()),
            'average_emissions_kg': float(carbon_data.mean()),
            'min_emissions_kg': float(carbon_data.min()),
            'max_emissions_kg': float(carbon_data.max()),
            'std_emissions_kg': float(carbon_data.std()),
            'median_emissions_kg': float(carbon_data.median()),
            'percentile_25': float(carbon_data.quantile(0.25)),
            'percentile_75': float(carbon_data.quantile(0.75)),
            'data_points': len(carbon_data),
            'period': period,
            'emission_factor_used': self.emission_factor
        }
        
        # Calculate trend (linear regression slope)
        if len(carbon_data) > 1:
            x = np.arange(len(carbon_data))
            slope, intercept = np.polyfit(x, carbon_data.values, 1)
            stats['trend_slope'] = float(slope)
            stats['trend_direction'] = 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable'
        
        logger.info(f"Calculated carbon emission trends for {len(carbon_data)} data points")
        return stats

def calculate_carbon_emissions(electric_data, emission_factor='korea_grid'):
    """Convenience function for carbon emission calculation.
    
    Args:
        electric_data: DataFrame with power consumption data
        emission_factor: Carbon emission factor to use
        
    Returns:
        DataFrame: Data with carbon emissions calculated
    """
    calculator = CarbonCalculator(emission_factor)
    return calculator.calculate_carbon_emissions(electric_data)

def get_available_emission_factors():
    """Get list of available carbon emission factors.
    
    Returns:
        dict: Available emission factors with descriptions
    """
    return CARBON_FACTORS.copy() 