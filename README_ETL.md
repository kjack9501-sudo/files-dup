# ETL Pipeline Documentation

A production-ready ETL (Extract, Transform, Load) pipeline implemented in Python.

## Features

### Extract Phase
- **CSV files**: Read data from CSV files
- **REST APIs**: Fetch data from REST API endpoints
- **Databases**: Extract from SQLite, MySQL, PostgreSQL
- **Files**: Support for JSON, Excel, Parquet formats

### Transform Phase
- Remove columns with excessive null values
- Clean and convert data types
- Normalize text data (trim, standardize)
- Standardize date formats
- Remove duplicate records
- Filter invalid records (business rules)
- Create derived columns
- Normalize values (standardize formats)

### Load Phase
- **SQLite**: Load to SQLite database
- **MySQL**: Load to MySQL database
- **PostgreSQL**: Load to PostgreSQL database
- **CSV**: Export to CSV file
- **JSON**: Export to JSON file
- **S3**: Upload to AWS S3 bucket

## Installation

```bash
pip install -r requirements_etl.txt
```

## Quick Start

### Basic Usage

```python
from etl_pipeline import ETLPipeline

# Create pipeline with default config
pipeline = ETLPipeline()
results = pipeline.run_etl()
```

### Custom Configuration

```python
config = {
    'source': {
        'type': 'csv',
        'path': 'data/input/data.csv'
    },
    'transform': {
        'remove_null_threshold': 0.5,
        'normalize_text': True,
        'standardize_dates': True,
        'remove_duplicates': True
    },
    'load': {
        'type': 'sqlite',
        'destination': 'data/output/output.db',
        'table_name': 'processed_data'
    }
}

pipeline = ETLPipeline(config)
results = pipeline.run_etl()
```

### Using Standalone Functions

```python
from etl_pipeline import extract, transform, load

# Extract
data = extract('csv', path='data/input/data.csv')

# Transform
transformed = transform(data, remove_duplicates=True)

# Load
load(transformed, 'csv', destination='data/output/output.csv')
```

## Configuration Options

### Source Configuration

#### CSV
```python
'source': {
    'type': 'csv',
    'path': 'path/to/file.csv'
}
```

#### API
```python
'source': {
    'type': 'api',
    'api_url': 'https://api.example.com/data'
}
```

#### Database
```python
'source': {
    'type': 'database',
    'db_path': 'data/input/source.db',
    'query': 'SELECT * FROM table_name'
}
```

#### File
```python
'source': {
    'type': 'file',
    'path': 'path/to/file.json'  # or .xlsx, .parquet
}
```

### Transform Configuration

```python
'transform': {
    'remove_null_threshold': 0.5,  # Remove columns with >50% nulls
    'normalize_text': True,          # Normalize text columns
    'standardize_dates': True,       # Convert dates to datetime
    'remove_duplicates': True        # Remove duplicate rows
}
```

### Load Configuration

#### SQLite
```python
'load': {
    'type': 'sqlite',
    'destination': 'data/output/output.db',
    'table_name': 'processed_data',
    'if_exists': 'replace'  # or 'append', 'fail'
}
```

#### MySQL
```python
'load': {
    'type': 'mysql',
    'connection': {
        'host': 'localhost',
        'user': 'username',
        'password': 'password',
        'database': 'dbname'
    },
    'table_name': 'processed_data'
}
```

#### PostgreSQL
```python
'load': {
    'type': 'postgresql',
    'connection_string': 'postgresql://user:password@localhost/dbname',
    'table_name': 'processed_data'
}
```

#### CSV
```python
'load': {
    'type': 'csv',
    'destination': 'data/output/output.csv'
}
```

#### JSON
```python
'load': {
    'type': 'json',
    'destination': 'data/output/output.json'
}
```

#### S3
```python
'load': {
    'type': 's3',
    's3_bucket': 'my-bucket',
    's3_key': 'path/to/file.csv',
    's3_format': 'csv'  # or 'json', 'parquet'
}
```

## Examples

### Example 1: CSV to SQLite
```python
config = {
    'source': {'type': 'csv', 'path': 'input.csv'},
    'transform': {'remove_duplicates': True},
    'load': {
        'type': 'sqlite',
        'destination': 'output.db',
        'table_name': 'data'
    }
}
pipeline = ETLPipeline(config)
pipeline.run_etl()
```

### Example 2: API to JSON
```python
config = {
    'source': {
        'type': 'api',
        'api_url': 'https://jsonplaceholder.typicode.com/users'
    },
    'transform': {'normalize_text': True},
    'load': {
        'type': 'json',
        'destination': 'users.json'
    }
}
pipeline = ETLPipeline(config)
pipeline.run_etl()
```

### Example 3: Database to CSV
```python
config = {
    'source': {
        'type': 'database',
        'db_path': 'source.db',
        'query': 'SELECT * FROM users WHERE active = 1'
    },
    'transform': {'remove_null_threshold': 0.3},
    'load': {
        'type': 'csv',
        'destination': 'active_users.csv'
    }
}
pipeline = ETLPipeline(config)
pipeline.run_etl()
```

## Logging

The pipeline logs all operations to:
- Console (stdout)
- File: `etl_pipeline.log`

Log levels:
- INFO: Normal operations
- WARNING: Non-critical issues
- ERROR: Failures

## Error Handling

The pipeline includes comprehensive error handling:
- File not found errors
- API connection errors
- Database connection errors
- Data validation errors
- Transformation errors

All errors are logged and raised with descriptive messages.

## Extending the Pipeline

### Adding Custom Transformations

```python
class CustomETLPipeline(ETLPipeline):
    def transform(self, data=None):
        data = super().transform(data)
        # Add custom transformations
        data['custom_column'] = data['col1'] * data['col2']
        return data
```

### Adding New Source Types

```python
class CustomETLPipeline(ETLPipeline):
    def _extract_from_custom(self):
        # Implement custom extraction
        return pd.DataFrame(...)
    
    def extract(self):
        if self.config['source']['type'] == 'custom':
            return self._extract_from_custom()
        return super().extract()
```

## Best Practices

1. **Always validate configuration** before running ETL
2. **Use logging** to track ETL execution
3. **Handle errors gracefully** with try-except blocks
4. **Test transformations** on sample data first
5. **Monitor data quality** after transformations
6. **Use transactions** for database loads when possible
7. **Implement data validation** rules
8. **Document custom transformations**

## Performance Tips

1. Use chunking for large datasets
2. Optimize database queries
3. Use appropriate data types
4. Remove unnecessary columns early
5. Use parallel processing for independent operations
6. Cache intermediate results when possible

## License

This ETL pipeline is provided as-is for educational and production use.

