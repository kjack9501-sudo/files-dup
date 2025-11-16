"""
ETL Pipeline - Extract, Transform, Load Process
A production-ready ETL pipeline that extracts data from multiple sources,
transforms it, and loads it into various destinations.

Author: Data Engineering Team
Date: 2024
"""

import pandas as pd
import requests
import sqlite3
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import os
from datetime import datetime
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ETLPipeline:
    """Main ETL Pipeline class that orchestrates the entire process."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize ETL Pipeline with configuration.
        
        Args:
            config: Dictionary containing ETL configuration
        """
        self.config = config or self._default_config()
        self.extracted_data = None
        self.transformed_data = None
        
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            'source': {
                'type': 'csv',  # Options: csv, api, database, file
                'path': 'data/input/sample_data.csv',
                'api_url': 'https://jsonplaceholder.typicode.com/users',
                'db_connection': None
            },
            'transform': {
                'remove_null_threshold': 0.5,  # Remove columns with >50% nulls
                'normalize_text': True,
                'standardize_dates': True,
                'remove_duplicates': True
            },
            'load': {
                'type': 'sqlite',  # Options: sqlite, mysql, postgresql, csv, json, s3
                'destination': 'data/output/etl_output.db',
                'table_name': 'processed_data',
                's3_bucket': None,
                's3_key': None
            }
        }
    
    def extract(self) -> pd.DataFrame:
        """
        Extract data from the configured source.
        
        Returns:
            DataFrame containing extracted data
            
        Raises:
            ValueError: If source type is not supported
            FileNotFoundError: If source file doesn't exist
        """
        logger.info("Starting extraction phase...")
        source_type = self.config['source']['type'].lower()
        
        try:
            if source_type == 'csv':
                data = self._extract_from_csv()
            elif source_type == 'api':
                data = self._extract_from_api()
            elif source_type == 'database':
                data = self._extract_from_database()
            elif source_type == 'file':
                data = self._extract_from_file()
            else:
                raise ValueError(f"Unsupported source type: {source_type}")
            
            logger.info(f"Extraction completed. Retrieved {len(data)} records.")
            self.extracted_data = data
            return data
            
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            raise
    
    def _extract_from_csv(self) -> pd.DataFrame:
        """Extract data from CSV file."""
        file_path = self.config['source']['path']
        
        if not os.path.exists(file_path):
            # Create sample CSV if it doesn't exist
            logger.warning(f"CSV file not found at {file_path}. Creating sample data...")
            self._create_sample_csv(file_path)
        
        logger.info(f"Reading CSV from {file_path}")
        df = pd.read_csv(file_path)
        return df
    
    def _extract_from_api(self) -> pd.DataFrame:
        """Extract data from REST API."""
        api_url = self.config['source']['api_url']
        logger.info(f"Fetching data from API: {api_url}")
        
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Convert JSON to DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            raise ValueError("Unexpected API response format")
        
        return df
    
    def _extract_from_database(self) -> pd.DataFrame:
        """Extract data from database (SQLite example)."""
        db_path = self.config['source'].get('db_path', 'data/input/source.db')
        query = self.config['source'].get('query', 'SELECT * FROM source_table')
        
        logger.info(f"Connecting to database: {db_path}")
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def _extract_from_file(self) -> pd.DataFrame:
        """Extract data from JSON or other file formats."""
        file_path = self.config['source']['path']
        file_ext = Path(file_path).suffix.lower()
        
        logger.info(f"Reading file: {file_path}")
        
        if file_ext == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])
        elif file_ext == '.xlsx':
            df = pd.read_excel(file_path)
        elif file_ext == '.parquet':
            df = pd.read_parquet(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        return df
    
    def _create_sample_csv(self, file_path: str):
        """Create a sample CSV file for testing."""
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        sample_data = {
            'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'name': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown', 'Charlie Wilson', 
                    'Diana Prince', 'Edward Norton', 'Fiona Apple', 'George Clooney', 'Helen Mirren'],
            'email': ['john@example.com', 'jane@example.com', 'bob@example.com', 'alice@example.com',
                     'charlie@example.com', 'diana@example.com', 'edward@example.com',
                     'fiona@example.com', 'george@example.com', 'helen@example.com'],
            'age': [25, 30, None, 35, 28, 32, 45, 29, 38, 42],
            'salary': ['50000', '60000', '55000', '70000', '65000', '80000', '90000', '75000', '85000', '95000'],
            'department': ['IT', 'HR', 'IT', 'Finance', 'IT', 'HR', 'Finance', 'IT', 'Finance', 'HR'],
            'join_date': ['2020-01-15', '2019-03-20', '2021-06-10', '2018-11-05', '2020-09-12',
                         '2019-07-18', '2017-04-22', '2021-02-14', '2018-08-30', '2019-12-01'],
            'status': ['active', 'active', 'inactive', 'active', 'active', 'active', 'active', 'inactive', 'active', 'active']
        }
        
        df = pd.DataFrame(sample_data)
        df.to_csv(file_path, index=False)
        logger.info(f"Sample CSV created at {file_path}")
    
    def transform(self, data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Transform the extracted data.
        
        Args:
            data: DataFrame to transform (uses extracted_data if None)
            
        Returns:
            Transformed DataFrame
        """
        logger.info("Starting transformation phase...")
        
        if data is None:
            if self.extracted_data is None:
                raise ValueError("No data to transform. Run extract() first.")
            data = self.extracted_data.copy()
        
        # Apply transformations
        data = self._remove_null_columns(data)
        data = self._clean_data_types(data)
        data = self._normalize_text(data)
        data = self._standardize_dates(data)
        data = self._remove_duplicates(data)
        data = self._filter_invalid_records(data)
        data = self._create_derived_columns(data)
        data = self._normalize_values(data)
        
        logger.info(f"Transformation completed. {len(data)} records after transformation.")
        self.transformed_data = data
        return data
    
    def _remove_null_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove columns with too many null values."""
        threshold = self.config['transform']['remove_null_threshold']
        null_percentage = df.isnull().sum() / len(df)
        columns_to_drop = null_percentage[null_percentage > threshold].index.tolist()
        
        if columns_to_drop:
            logger.info(f"Removing columns with >{threshold*100}% nulls: {columns_to_drop}")
            df = df.drop(columns=columns_to_drop)
        
        return df
    
    def _clean_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert data types to appropriate formats."""
        logger.info("Cleaning data types...")
        
        # Convert numeric columns
        numeric_columns = df.select_dtypes(include=['object']).columns
        for col in numeric_columns:
            # Try to convert to numeric
            if df[col].dtype == 'object':
                # Check if column contains numeric strings
                try:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except:
                    pass
        
        # Convert boolean columns
        bool_columns = [col for col in df.columns if df[col].dtype == 'object' and 
                       df[col].isin(['True', 'False', 'true', 'false', '1', '0', 'yes', 'no']).any()]
        for col in bool_columns:
            df[col] = df[col].astype(str).str.lower().map({
                'true': True, 'false': False, '1': True, '0': False,
                'yes': True, 'no': False
            })
        
        return df
    
    def _normalize_text(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize text columns (trim whitespace, lowercase, etc.)."""
        if not self.config['transform']['normalize_text']:
            return df
        
        logger.info("Normalizing text data...")
        
        text_columns = df.select_dtypes(include=['object']).columns
        for col in text_columns:
            if df[col].dtype == 'object':
                # Trim whitespace
                df[col] = df[col].astype(str).str.strip()
                # Remove extra spaces
                df[col] = df[col].str.replace(r'\s+', ' ', regex=True)
        
        return df
    
    def _standardize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize date columns to datetime format."""
        if not self.config['transform']['standardize_dates']:
            return df
        
        logger.info("Standardizing date columns...")
        
        # Common date column patterns
        date_patterns = ['date', 'time', 'created', 'updated', 'join', 'start', 'end']
        date_columns = [col for col in df.columns if any(pattern in col.lower() for pattern in date_patterns)]
        
        for col in date_columns:
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce', infer_datetime_format=True)
            except:
                logger.warning(f"Could not convert {col} to datetime")
        
        return df
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate records."""
        if not self.config['transform']['remove_duplicates']:
            return df
        
        initial_count = len(df)
        df = df.drop_duplicates()
        removed = initial_count - len(df)
        
        if removed > 0:
            logger.info(f"Removed {removed} duplicate records")
        
        return df
    
    def _filter_invalid_records(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter out invalid records based on business rules."""
        logger.info("Filtering invalid records...")
        
        initial_count = len(df)
        
        # Example: Remove records with negative ages
        if 'age' in df.columns:
            df = df[df['age'].isna() | (df['age'] >= 0)]
        
        # Example: Remove records with invalid emails
        if 'email' in df.columns:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            df = df[df['email'].isna() | df['email'].astype(str).str.match(email_pattern, na=False)]
        
        # Example: Remove records with empty required fields
        required_fields = ['name']  # Add your required fields here
        for field in required_fields:
            if field in df.columns:
                df = df[df[field].notna() & (df[field].astype(str).str.strip() != '')]
        
        removed = initial_count - len(df)
        if removed > 0:
            logger.info(f"Filtered out {removed} invalid records")
        
        return df
    
    def _create_derived_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create new derived columns from existing data."""
        logger.info("Creating derived columns...")
        
        # Example: Create full_name from first_name and last_name
        if 'first_name' in df.columns and 'last_name' in df.columns:
            df['full_name'] = df['first_name'] + ' ' + df['last_name']
        
        # Example: Create age_group from age
        if 'age' in df.columns:
            df['age_group'] = pd.cut(
                df['age'],
                bins=[0, 25, 35, 45, 100],
                labels=['18-25', '26-35', '36-45', '45+'],
                right=False
            )
        
        # Example: Create salary_category from salary
        if 'salary' in df.columns:
            if df['salary'].dtype in ['int64', 'float64']:
                df['salary_category'] = pd.cut(
                    df['salary'],
                    bins=[0, 50000, 70000, 90000, float('inf')],
                    labels=['Low', 'Medium', 'High', 'Very High'],
                    right=False
                )
        
        # Add processing timestamp
        df['etl_processed_at'] = datetime.now()
        
        return df
    
    def _normalize_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize values (standardize formats, etc.)."""
        logger.info("Normalizing values...")
        
        # Example: Normalize department names
        if 'department' in df.columns:
            df['department'] = df['department'].astype(str).str.upper().str.strip()
        
        # Example: Normalize status values
        if 'status' in df.columns:
            status_mapping = {
                'active': 'ACTIVE',
                'inactive': 'INACTIVE',
                'pending': 'PENDING',
                'suspended': 'SUSPENDED'
            }
            df['status'] = df['status'].astype(str).str.lower().map(
                lambda x: status_mapping.get(x.lower(), x.upper())
            )
        
        return df
    
    def load(self, data: Optional[pd.DataFrame] = None, destination: Optional[str] = None):
        """
        Load transformed data into the configured destination.
        
        Args:
            data: DataFrame to load (uses transformed_data if None)
            destination: Override destination from config
        """
        logger.info("Starting load phase...")
        
        if data is None:
            if self.transformed_data is None:
                raise ValueError("No data to load. Run transform() first.")
            data = self.transformed_data.copy()
        
        load_type = self.config['load']['type'].lower() if not destination else destination.lower()
        
        try:
            if load_type == 'sqlite':
                self._load_to_sqlite(data)
            elif load_type == 'mysql':
                self._load_to_mysql(data)
            elif load_type == 'postgresql':
                self._load_to_postgresql(data)
            elif load_type == 'csv':
                self._load_to_csv(data)
            elif load_type == 'json':
                self._load_to_json(data)
            elif load_type == 's3':
                self._load_to_s3(data)
            else:
                raise ValueError(f"Unsupported load type: {load_type}")
            
            logger.info(f"Load completed successfully. {len(data)} records loaded.")
            
        except Exception as e:
            logger.error(f"Load failed: {str(e)}")
            raise
    
    def _load_to_sqlite(self, df: pd.DataFrame):
        """Load data to SQLite database."""
        db_path = self.config['load']['destination']
        table_name = self.config['load']['table_name']
        
        logger.info(f"Loading data to SQLite: {db_path}, table: {table_name}")
        
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path)
        
        # Replace table if exists, or append
        if_exists = self.config['load'].get('if_exists', 'replace')
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)
        
        conn.close()
        logger.info(f"Data loaded to {table_name} table")
    
    def _load_to_mysql(self, df: pd.DataFrame):
        """Load data to MySQL database."""
        try:
            import pymysql
        except ImportError:
            raise ImportError("pymysql is required for MySQL. Install with: pip install pymysql")
        
        connection_config = self.config['load'].get('connection', {})
        table_name = self.config['load']['table_name']
        
        logger.info(f"Loading data to MySQL table: {table_name}")
        
        conn = pymysql.connect(**connection_config)
        if_exists = self.config['load'].get('if_exists', 'replace')
        
        df.to_sql(table_name, conn, if_exists=if_exists, index=False, method='multi')
        conn.close()
        
        logger.info(f"Data loaded to MySQL {table_name} table")
    
    def _load_to_postgresql(self, df: pd.DataFrame):
        """Load data to PostgreSQL database."""
        try:
            from sqlalchemy import create_engine
        except ImportError:
            raise ImportError("sqlalchemy is required for PostgreSQL. Install with: pip install sqlalchemy psycopg2")
        
        connection_string = self.config['load'].get('connection_string', '')
        table_name = self.config['load']['table_name']
        
        logger.info(f"Loading data to PostgreSQL table: {table_name}")
        
        engine = create_engine(connection_string)
        if_exists = self.config['load'].get('if_exists', 'replace')
        
        df.to_sql(table_name, engine, if_exists=if_exists, index=False, method='multi')
        engine.dispose()
        
        logger.info(f"Data loaded to PostgreSQL {table_name} table")
    
    def _load_to_csv(self, df: pd.DataFrame):
        """Load data to CSV file."""
        file_path = self.config['load']['destination']
        
        logger.info(f"Loading data to CSV: {file_path}")
        
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(file_path, index=False)
        
        logger.info(f"Data saved to {file_path}")
    
    def _load_to_json(self, df: pd.DataFrame):
        """Load data to JSON file."""
        file_path = self.config['load']['destination']
        
        logger.info(f"Loading data to JSON: {file_path}")
        
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Convert DataFrame to JSON
        records = df.to_dict('records')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, default=str)
        
        logger.info(f"Data saved to {file_path}")
    
    def _load_to_s3(self, df: pd.DataFrame):
        """Load data to S3 bucket."""
        try:
            import boto3
        except ImportError:
            raise ImportError("boto3 is required for S3. Install with: pip install boto3")
        
        bucket = self.config['load']['s3_bucket']
        key = self.config['load']['s3_key']
        file_format = self.config['load'].get('s3_format', 'csv')
        
        logger.info(f"Loading data to S3: s3://{bucket}/{key}")
        
        s3_client = boto3.client('s3')
        
        if file_format == 'csv':
            csv_buffer = df.to_csv(index=False)
            s3_client.put_object(Bucket=bucket, Key=key, Body=csv_buffer.encode('utf-8'))
        elif file_format == 'json':
            json_buffer = df.to_json(orient='records', indent=2)
            s3_client.put_object(Bucket=bucket, Key=key, Body=json_buffer.encode('utf-8'))
        elif file_format == 'parquet':
            import io
            parquet_buffer = io.BytesIO()
            df.to_parquet(parquet_buffer, index=False)
            s3_client.put_object(Bucket=bucket, Key=key, Body=parquet_buffer.getvalue())
        
        logger.info(f"Data uploaded to S3: s3://{bucket}/{key}")
    
    def run_etl(self) -> Dict[str, Any]:
        """
        Run the complete ETL process.
        
        Returns:
            Dictionary with ETL execution results
        """
        logger.info("=" * 60)
        logger.info("Starting ETL Pipeline")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        results = {
            'status': 'success',
            'start_time': start_time,
            'extracted_records': 0,
            'transformed_records': 0,
            'loaded_records': 0,
            'errors': []
        }
        
        try:
            # Extract
            extracted = self.extract()
            results['extracted_records'] = len(extracted)
            
            # Transform
            transformed = self.transform()
            results['transformed_records'] = len(transformed)
            
            # Load
            self.load()
            results['loaded_records'] = len(transformed)
            
            end_time = datetime.now()
            results['end_time'] = end_time
            results['duration'] = str(end_time - start_time)
            
            logger.info("=" * 60)
            logger.info("ETL Pipeline completed successfully")
            logger.info(f"Duration: {results['duration']}")
            logger.info(f"Records: {results['extracted_records']} -> {results['transformed_records']} -> {results['loaded_records']}")
            logger.info("=" * 60)
            
        except Exception as e:
            results['status'] = 'failed'
            results['error'] = str(e)
            results['end_time'] = datetime.now()
            logger.error(f"ETL Pipeline failed: {str(e)}")
            raise
        
        return results


# Standalone functions for direct use
def extract(source_type: str = 'csv', **kwargs) -> pd.DataFrame:
    """
    Extract data from a source.
    
    Args:
        source_type: Type of source (csv, api, database, file)
        **kwargs: Source-specific parameters
        
    Returns:
        DataFrame with extracted data
    """
    config = {
        'source': {
            'type': source_type,
            **kwargs
        }
    }
    pipeline = ETLPipeline(config)
    return pipeline.extract()


def transform(data: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """
    Transform data.
    
    Args:
        data: DataFrame to transform
        **kwargs: Transformation options
        
    Returns:
        Transformed DataFrame
    """
    config = {
        'transform': kwargs
    }
    pipeline = ETLPipeline(config)
    return pipeline.transform(data)


def load(data: pd.DataFrame, load_type: str = 'csv', **kwargs):
    """
    Load data to destination.
    
    Args:
        data: DataFrame to load
        load_type: Type of destination (sqlite, mysql, postgresql, csv, json, s3)
        **kwargs: Load-specific parameters
    """
    config = {
        'load': {
            'type': load_type,
            **kwargs
        }
    }
    pipeline = ETLPipeline(config)
    pipeline.load(data)


def run_etl(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run complete ETL process.
    
    Args:
        config: ETL configuration dictionary
        
    Returns:
        Dictionary with execution results
    """
    pipeline = ETLPipeline(config)
    return pipeline.run_etl()


# Example usage
if __name__ == "__main__":
    # Example 1: Simple ETL with default config
    print("Example 1: Running ETL with default configuration")
    pipeline = ETLPipeline()
    results = pipeline.run_etl()
    print(f"\nResults: {results}\n")
    
    # Example 2: Custom ETL configuration
    print("Example 2: Running ETL with custom configuration")
    custom_config = {
        'source': {
            'type': 'csv',
            'path': 'data/input/sample_data.csv'
        },
        'transform': {
            'remove_null_threshold': 0.3,
            'normalize_text': True,
            'standardize_dates': True,
            'remove_duplicates': True
        },
        'load': {
            'type': 'json',
            'destination': 'data/output/transformed_data.json',
            'table_name': 'processed_data'
        }
    }
    
    pipeline2 = ETLPipeline(custom_config)
    results2 = pipeline2.run_etl()
    print(f"\nResults: {results2}\n")
    
    # Example 3: Using standalone functions
    print("Example 3: Using standalone functions")
    data = extract('csv', path='data/input/sample_data.csv')
    transformed = transform(data, remove_duplicates=True, normalize_text=True)
    load(transformed, 'csv', destination='data/output/final_output.csv')
    print("ETL completed using standalone functions")

