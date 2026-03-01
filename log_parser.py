"""
Log parser for MLBevo Door Module Test Reports
Parses CSV-like log files with metadata and test results
"""
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class TestMetadata:
    """Metadata extracted from the first line of the log file"""
    serial_number: str
    test_result: str


@dataclass
class TestRow:
    """Single test result row"""
    external_id: str
    text: str
    lower_limit: str
    value: str
    upper_limit: str
    unit: str
    result: str
    status_text: str


@dataclass
class ParsedLog:
    """Complete parsed log with metadata and rows"""
    metadata: TestMetadata
    rows: List[TestRow]


def strip_quotes(value: str) -> str:
    """Remove surrounding quotes from a string"""
    trimmed = value.strip()
    if trimmed.startswith('"') and trimmed.endswith('"'):
        return trimmed[1:-1]
    return trimmed


def parse_metadata_line(line: str) -> TestMetadata:
    """Parse the first line containing metadata"""
    # Remove BOM if present
    clean = line.replace('\ufeff', '').strip()
    
    # Extract serial number
    serial_number = 'Unknown'
    if 'Serialnumber:' in clean:
        parts = clean.split('Serialnumber:', 1)
        if len(parts) > 1:
            serial_part = parts[1].split(',')[0].strip()
            serial_number = serial_part
    
    # Extract test result
    test_result = 'Unknown'
    if 'Testresult:' in clean:
        parts = clean.split('Testresult:', 1)
        if len(parts) > 1:
            test_result = parts[1].strip()
    
    return TestMetadata(serial_number=serial_number, test_result=test_result)


def parse_log_file(content: str) -> ParsedLog:
    """Parse the entire log file content"""
    lines = content.split('\n')
    
    # Remove carriage returns
    lines = [line.replace('\r', '') for line in lines]
    
    if len(lines) < 2:
        return ParsedLog(
            metadata=TestMetadata(serial_number='Unknown', test_result='Unknown'),
            rows=[]
        )
    
    # Parse metadata from first line
    metadata = parse_metadata_line(lines[0])
    
    # Parse headers from second line
    header_line = lines[1]
    headers = [strip_quotes(h) for h in header_line.split(';')]
    
    # Get column indices
    def col_index(name: str) -> int:
        try:
            return headers.index(name)
        except ValueError:
            return -1
    
    i_external_id = col_index('ExternalId')
    i_text = col_index('Text')
    i_lower_limit = col_index('LowerLimit')
    i_value = col_index('Value')
    i_upper_limit = col_index('UpperLimit')
    i_unit = col_index('Unit')
    i_result = col_index('Result')
    i_status_text = col_index('StatusText')
    
    # Parse data rows
    rows: List[TestRow] = []
    
    for i in range(2, len(lines)):
        line = lines[i].strip()
        if not line:
            continue
        
        cols = [strip_quotes(c) for c in line.split(';')]
        
        # Get values safely
        def get_col(idx: int) -> str:
            return cols[idx] if 0 <= idx < len(cols) else ''
        
        external_id = get_col(i_external_id)
        lower_limit = get_col(i_lower_limit)
        upper_limit = get_col(i_upper_limit)
        
        # Filter: must have all three
        if not external_id or not lower_limit or not upper_limit:
            continue
        
        rows.append(TestRow(
            external_id=external_id,
            text=get_col(i_text),
            lower_limit=lower_limit,
            value=get_col(i_value),
            upper_limit=upper_limit,
            unit=get_col(i_unit),
            result=get_col(i_result),
            status_text=get_col(i_status_text)
        ))
    
    return ParsedLog(metadata=metadata, rows=rows)


def get_result_variant(result: str) -> str:
    """Determine the visual variant for a result (pass/fail/warn)"""
    lower = result.lower()
    if lower in ['true', 'pass', 'successful']:
        return 'pass'
    elif lower in ['false', 'fail', 'failed', 'nok']:
        return 'fail'
    else:
        return 'warn'
