import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import anthropic
import pandas as pd
import re

logger = logging.getLogger(__name__)

class ClaudeAPI:
    """Claude API integration for ESG report generation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Claude API client with simplified configuration"""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        
        if not self.api_key:
            logger.error("ANTHROPIC_API_KEY not found in environment variables")
            raise ValueError("ANTHROPIC_API_KEY is required")
        
        self.model = "claude-3-haiku-20240307"
        self.client = None
        
        # Try to initialize the client with error handling
        try:
            import anthropic
            # Use minimal initialization to avoid dependency conflicts
            self.client = anthropic.Anthropic(
                api_key=self.api_key,
                # Remove any problematic kwargs
            )
            logger.info("Claude API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Claude API client: {e}")
            # Don't raise here, allow graceful degradation
            self.client = None
    
    def generate_esg_report(self, daily_data: pd.DataFrame, carbon_data: pd.DataFrame, 
                           monthly_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """Generate comprehensive ESG report using Claude API.
        
        Args:
            daily_data: DataFrame with daily power consumption summaries
            carbon_data: DataFrame with carbon emission calculations
            monthly_data: Optional DataFrame with monthly summaries
            
        Returns:
            Dict containing structured ESG report data
        """
        try:
            # Prepare data for the prompt
            report_data = self._prepare_report_data(daily_data, carbon_data, monthly_data)
            
            # Generate the ESG report
            prompt = self._create_esg_prompt(report_data)
            
            logger.info("Generating ESG report with Claude API...")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.3,
                system="You are an expert environmental analyst specializing in ESG reporting. Generate comprehensive, data-driven environmental impact reports with actionable insights.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse the response
            report_content = response.content[0].text
            structured_report = self._parse_esg_report(report_content, report_data)
            
            logger.info("ESG report generated successfully")
            return structured_report
            
        except Exception as e:
            logger.error(f"Error generating ESG report: {e}")
            raise
    
    def _prepare_report_data(self, daily_data: pd.DataFrame, carbon_data: pd.DataFrame, 
                           monthly_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """Prepare data summary for ESG report generation.
        
        Args:
            daily_data: Daily power consumption data
            carbon_data: Carbon emission data
            monthly_data: Optional monthly data
            
        Returns:
            Dict with prepared data summaries
        """
        # Calculate summary statistics
        data_summary = {
            'analysis_period': {
                'start_date': daily_data['date'].min().strftime('%Y-%m-%d') if not daily_data.empty else None,
                'end_date': daily_data['date'].max().strftime('%Y-%m-%d') if not daily_data.empty else None,
                'total_days': len(daily_data)
            },
            'power_consumption': {
                'total_kwh': float(daily_data['daily_energy_kwh'].sum()) if 'daily_energy_kwh' in daily_data.columns else 0,
                'average_daily_kwh': float(daily_data['daily_energy_kwh'].mean()) if 'daily_energy_kwh' in daily_data.columns else 0,
                'peak_daily_kwh': float(daily_data['daily_energy_kwh'].max()) if 'daily_energy_kwh' in daily_data.columns else 0,
                'min_daily_kwh': float(daily_data['daily_energy_kwh'].min()) if 'daily_energy_kwh' in daily_data.columns else 0
            },
            'carbon_emissions': {
                'total_kg_co2': float(carbon_data['daily_carbon_kg'].sum()) if 'daily_carbon_kg' in carbon_data.columns else 0,
                'average_daily_kg_co2': float(carbon_data['daily_carbon_kg'].mean()) if 'daily_carbon_kg' in carbon_data.columns else 0,
                'peak_daily_kg_co2': float(carbon_data['daily_carbon_kg'].max()) if 'daily_carbon_kg' in carbon_data.columns else 0
            },
            'environmental_factors': {
                'avg_temperature': float(daily_data['avg_temp'].mean()) if 'avg_temp' in daily_data.columns else 0,
                'avg_humidity': float(daily_data['avg_humidity'].mean()) if 'avg_humidity' in daily_data.columns else 0,
                'avg_brightness': float(daily_data['avg_brightness'].mean()) if 'avg_brightness' in daily_data.columns else 0,
                'temp_range': {
                    'min': float(daily_data['min_temp'].min()) if 'min_temp' in daily_data.columns else 0,
                    'max': float(daily_data['max_temp'].max()) if 'max_temp' in daily_data.columns else 0
                }
            }
        }
        
        # Add monthly data if provided
        if monthly_data is not None and not monthly_data.empty:
            data_summary['monthly_trends'] = {
                'months_analyzed': len(monthly_data),
                'monthly_averages': monthly_data[['year_month', 'avg_electric', 'monthly_carbon_kg']].to_dict('records') if 'monthly_carbon_kg' in monthly_data.columns else []
            }
        
        # Add recent trends (last 7 days vs previous 7 days)
        if len(daily_data) >= 14:
            recent_data = daily_data.tail(7)
            previous_data = daily_data.tail(14).head(7)
            
            if 'daily_energy_kwh' in daily_data.columns:
                data_summary['recent_trends'] = {
                    'recent_avg_kwh': float(recent_data['daily_energy_kwh'].mean()),
                    'previous_avg_kwh': float(previous_data['daily_energy_kwh'].mean()),
                    'change_percent': float(((recent_data['daily_energy_kwh'].mean() - previous_data['daily_energy_kwh'].mean()) / previous_data['daily_energy_kwh'].mean()) * 100)
                }
        
        return data_summary
    
    def _create_esg_prompt(self, data_summary: Dict[str, Any]) -> str:
        """Create comprehensive prompt for ESG report generation.
        
        Args:
            data_summary: Prepared data summary
            
        Returns:
            String prompt for Claude API
        """
        prompt = f"""
Generate a comprehensive ESG (Environmental, Social, Governance) report focused on Environmental aspects based on the following power consumption and environmental data:

## Data Summary
Analysis Period: {data_summary['analysis_period']['start_date']} to {data_summary['analysis_period']['end_date']} ({data_summary['analysis_period']['total_days']} days)

### Power Consumption Data:
- Total Energy Consumption: {data_summary['power_consumption']['total_kwh']:.2f} kWh
- Average Daily Consumption: {data_summary['power_consumption']['average_daily_kwh']:.2f} kWh
- Peak Daily Consumption: {data_summary['power_consumption']['peak_daily_kwh']:.2f} kWh
- Minimum Daily Consumption: {data_summary['power_consumption']['min_daily_kwh']:.2f} kWh

### Carbon Emissions (Korea Grid Factor: 0.478 kgCO₂/kWh):
- Total CO₂ Emissions: {data_summary['carbon_emissions']['total_kg_co2']:.2f} kg CO₂
- Average Daily Emissions: {data_summary['carbon_emissions']['average_daily_kg_co2']:.2f} kg CO₂
- Peak Daily Emissions: {data_summary['carbon_emissions']['peak_daily_kg_co2']:.2f} kg CO₂

### Environmental Conditions:
- Average Temperature: {data_summary['environmental_factors']['avg_temperature']:.1f}°C
- Average Humidity: {data_summary['environmental_factors']['avg_humidity']:.1f}%
- Average Brightness: {data_summary['environmental_factors']['avg_brightness']:.0f} lux
- Temperature Range: {data_summary['environmental_factors']['temp_range']['min']:.1f}°C to {data_summary['environmental_factors']['temp_range']['max']:.1f}°C

## Report Requirements

Please generate a structured ESG report with the following sections:

### 1. EXECUTIVE_SUMMARY
A concise overview of environmental performance, key findings, and immediate recommendations (150-200 words).

### 2. ENVIRONMENTAL_IMPACT_ANALYSIS
Detailed analysis including:
- Power consumption patterns and trends
- Carbon footprint assessment
- Environmental factor correlations (temperature, humidity, brightness effects on power usage)
- Benchmarking against industry standards

### 3. SUSTAINABILITY_METRICS
Key performance indicators:
- Energy efficiency metrics
- Carbon intensity calculations
- Environmental performance trends
- Comparative analysis with previous periods

### 4. ACTIONABLE_RECOMMENDATIONS
Specific, measurable recommendations for:
- Energy consumption reduction strategies
- Carbon footprint minimization
- Operational efficiency improvements
- Environmental monitoring enhancements

### 5. DATA_TABLES
Format as JSON objects for easy parsing:
- Monthly energy consumption summary
- Monthly carbon emissions summary
- Environmental factors correlation matrix

### 6. RISK_ASSESSMENT
Environmental risks and mitigation strategies:
- Climate-related risks
- Energy supply risks
- Regulatory compliance risks

Please structure your response with clear section headers (use ### for main sections) and provide actionable, data-driven insights based on the provided information. Focus on practical recommendations that can be implemented to improve environmental performance.
"""
        
        return prompt
    
    def _parse_esg_report(self, report_content: str, data_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Claude's response into structured ESG report format.
        
        Args:
            report_content: Raw text response from Claude
            data_summary: Original data summary for reference
            
        Returns:
            Structured ESG report dictionary
        """
        try:
            # Initialize structured report
            structured_report = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'model_used': self.model,
                    'analysis_period': data_summary['analysis_period'],
                    'data_summary': data_summary
                },
                'report_sections': {}
            }
            
            # Parse sections using regex patterns
            sections = {
                'executive_summary': r'### 1\. EXECUTIVE_SUMMARY\s*(.*?)(?=### 2\.|$)',
                'environmental_impact': r'### 2\. ENVIRONMENTAL_IMPACT_ANALYSIS\s*(.*?)(?=### 3\.|$)',
                'sustainability_metrics': r'### 3\. SUSTAINABILITY_METRICS\s*(.*?)(?=### 4\.|$)',
                'recommendations': r'### 4\. ACTIONABLE_RECOMMENDATIONS\s*(.*?)(?=### 5\.|$)',
                'data_tables': r'### 5\. DATA_TABLES\s*(.*?)(?=### 6\.|$)',
                'risk_assessment': r'### 6\. RISK_ASSESSMENT\s*(.*?)(?=$)'
            }
            
            for section_name, pattern in sections.items():
                match = re.search(pattern, report_content, re.DOTALL | re.IGNORECASE)
                if match:
                    content = match.group(1).strip()
                    structured_report['report_sections'][section_name] = content
                else:
                    logger.warning(f"Section '{section_name}' not found in report")
                    structured_report['report_sections'][section_name] = ""
            
            # Extract JSON tables if present
            structured_report['data_tables'] = self._extract_json_tables(
                structured_report['report_sections'].get('data_tables', '')
            )
            
            # Calculate report metrics
            structured_report['report_metrics'] = {
                'total_sections': len([s for s in structured_report['report_sections'].values() if s]),
                'word_count': len(report_content.split()),
                'recommendations_count': len(self._extract_recommendations(
                    structured_report['report_sections'].get('recommendations', '')
                ))
            }
            
            # Add raw content for fallback
            structured_report['raw_content'] = report_content
            
            logger.info("ESG report parsed successfully")
            return structured_report
            
        except Exception as e:
            logger.error(f"Error parsing ESG report: {e}")
            # Return fallback structure
            return {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'model_used': self.model,
                    'parsing_error': str(e)
                },
                'raw_content': report_content,
                'error': True
            }
    
    def _extract_json_tables(self, tables_content: str) -> Dict[str, Any]:
        """Extract JSON tables from the data tables section.
        
        Args:
            tables_content: Content of the data tables section
            
        Returns:
            Dict containing extracted tables
        """
        tables = {}
        
        # Look for JSON-like structures
        json_pattern = r'\{[^{}]*\}'
        matches = re.findall(json_pattern, tables_content, re.DOTALL)
        
        for i, match in enumerate(matches):
            try:
                parsed_json = json.loads(match)
                tables[f'table_{i+1}'] = parsed_json
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON table: {match[:100]}...")
                continue
        
        return tables
    
    def _extract_recommendations(self, recommendations_content: str) -> list:
        """Extract individual recommendations from the recommendations section.
        
        Args:
            recommendations_content: Content of the recommendations section
            
        Returns:
            List of individual recommendations
        """
        # Split by bullet points, numbered lists, or line breaks
        recommendations = []
        
        # Common patterns for recommendations
        patterns = [
            r'[-*•]\s*(.+)',  # Bullet points
            r'\d+\.\s*(.+)',  # Numbered lists
            r'^(.+)$'         # Line-based fallback
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, recommendations_content, re.MULTILINE)
            if matches:
                recommendations.extend([r.strip() for r in matches if len(r.strip()) > 10])
                break
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def generate_summary_report(self, data_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a simplified summary report without full ESG analysis.
        
        Args:
            data_summary: Prepared data summary
            
        Returns:
            Simplified report structure
        """
        try:
            prompt = f"""
Generate a concise environmental impact summary based on this data:

Power Consumption: {data_summary['power_consumption']['total_kwh']:.2f} kWh over {data_summary['analysis_period']['total_days']} days
Carbon Emissions: {data_summary['carbon_emissions']['total_kg_co2']:.2f} kg CO₂

Provide:
1. A 2-sentence environmental impact summary
2. Top 3 specific recommendations for improvement
3. One key metric to track

Keep response under 200 words.
"""
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                'summary': response.content[0].text,
                'generated_at': datetime.now().isoformat(),
                'data_summary': data_summary
            }
            
        except Exception as e:
            logger.error(f"Error generating summary report: {e}")
            raise
    
    def test_api_connection(self) -> bool:
        """Test Claude API connectivity.
        
        Returns:
            bool: True if API is accessible, False otherwise
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Test"}]
            )
            logger.info("Claude API connection test successful")
            return True
        except Exception as e:
            logger.error(f"Claude API connection test failed: {e}")
            return False 