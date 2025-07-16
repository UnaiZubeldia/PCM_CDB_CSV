#!/usr/bin/env python3
"""
Automated CDB to CSV Converter

This script converts .cdb database files to CSV format using an intermediate XML export.
Requires Exporter.exe to be present in the same directory.

Usage:
    python automated_export.py

The script will process all .cdb files in the current directory and create
corresponding .csv files.
"""

import subprocess
import pandas as pd
import xml.etree.ElementTree as ET
from pathlib import Path

def export_to_xml(input_file, output_file, script_dir):
    """
    Export .cdb file to XML using Exporter.exe.
    
    Args:
        input_file (str): Name of the .cdb file to export
        output_file (str): Name of the output XML file
        script_dir (str): Directory containing Exporter.exe
        
    Returns:
        bool: True if export successful, False otherwise
    """
    command = [r".\Exporter.exe", "-input", input_file, "-output", output_file, "-ToXML"]
    try:
        subprocess.run(command, check=True, cwd=script_dir, capture_output=True, text=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
        
def calculate_age(birthdate):
    """
    Calculate age from birthdate in YYYYMMDD format.
    
    Args:
        birthdate: Birthdate in YYYYMMDD format
        
    Returns:
        int: Age in years, or None if invalid
    """
    if pd.isna(birthdate):
        return None
    try:
        from datetime import datetime
        birth_date = datetime.strptime(str(int(birthdate)), '%Y%m%d')
        today = datetime.now()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except (ValueError, TypeError):
        return None

def xml_to_df(file_path, table_name=None):
    """
    Convert XML file to pandas DataFrame.
    
    Args:
        file_path (str): Path to the XML file
        table_name (str): Specific table name to extract. If None, finds first table with data.
        
    Returns:
        pd.DataFrame: DataFrame containing the table data
        
    Raises:
        ValueError: If no table is found in the XML file
    """
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    if table_name:
        # Find specific table by TableName attribute
        table = root.find(f".//Table[@TableName='{table_name}']")
    else:
        # Find first table with data (NumRows > 0)
        table = None
        for t in root.findall('.//Table'):
            num_rows = t.get('NumRows')
            if num_rows and int(num_rows) > 0:
                table = t
                break
    
    if table is None:
        if table_name:
            raise ValueError(f"Table with TableName='{table_name}' not found in the XML file.")
        else:
            raise ValueError("No table with data found in XML file.")

    # Extract column names and data
    columns = []
    data = []
    
    for col in table.findall('Column'):
        column_name = col.get('ColumnName')
        if column_name:
            columns.append(column_name)
            cells = [cell.text if cell.text is not None else None for cell in col.findall('Cell')]
            data.append(cells)

    # Find the maximum row length
    if data:
        max_length = max(len(col_data) for col_data in data)
        # Pad columns with None to ensure consistent row lengths
        padded_data = [col_data + [None] * (max_length - len(col_data)) for col_data in data]
        # Transpose the data to match DataFrame structure
        transposed_data = list(map(list, zip(*padded_data)))
        return pd.DataFrame(transposed_data, columns=columns)
    
    return pd.DataFrame()

def cyclist_and_team_data(xml_path):
    """
    Extract and merge cyclist and team data similar to old_wdb_to_csv.py.
    
    Args:
        xml_path (str): Path to the XML file
        
    Returns:
        pd.DataFrame: Merged DataFrame with cyclist and team data
    """
    # Get cyclist data
    cyclists_df = xml_to_df(xml_path, 'DYN_cyclist')
    
    # Get team data
    teams_df = xml_to_df(xml_path, 'DYN_team')
    
    # Select relevant team columns (IDteam, gene_sz_shortname, gene_sz_name)
    team_cols = ['IDteam']
    if 'gene_sz_shortname' in teams_df.columns:
        team_cols.append('gene_sz_shortname')
    if 'gene_sz_name' in teams_df.columns:
        team_cols.append('gene_sz_name')
    
    teams_df = teams_df[team_cols]
    
    # Merge cyclist and team data
    full_db = cyclists_df.merge(teams_df, left_on='fkIDteam', right_on='IDteam', how='left')
    
    # Convert birthdate to age if birthdate column exists
    if 'gene_i_birthdate' in full_db.columns:
        full_db['age'] = full_db['gene_i_birthdate'].apply(calculate_age)
    
    # Return all columns (no filtering)
    return full_db
    """
    Convert XML file to pandas DataFrame.
    
    Args:
        file_path (str): Path to the XML file
        table_name (str): Specific table name to extract. If None, finds first table with data.
        
    Returns:
        pd.DataFrame: DataFrame containing the table data
        
    Raises:
        ValueError: If no table is found in the XML file
    """
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    if table_name:
        # Find specific table by TableName attribute
        table = root.find(f".//Table[@TableName='{table_name}']")
    else:
        # Find first table with data (NumRows > 0)
        table = None
        for t in root.findall('.//Table'):
            num_rows = t.get('NumRows')
            if num_rows and int(num_rows) > 0:
                table = t
                break
    
    if table is None:
        if table_name:
            raise ValueError(f"Table with TableName='{table_name}' not found in the XML file.")
        else:
            raise ValueError("No table with data found in XML file.")

    # Extract column names and data
    columns = []
    data = []
    
    for col in table.findall('Column'):
        column_name = col.get('ColumnName')
        if column_name:
            columns.append(column_name)
            cells = [cell.text if cell.text is not None else None for cell in col.findall('Cell')]
            data.append(cells)

    # Find the maximum row length
    if data:
        max_length = max(len(col_data) for col_data in data)
        # Pad columns with None to ensure consistent row lengths
        padded_data = [col_data + [None] * (max_length - len(col_data)) for col_data in data]
        # Transpose the data to match DataFrame structure
        transposed_data = list(map(list, zip(*padded_data)))
        return pd.DataFrame(transposed_data, columns=columns)
    
    return pd.DataFrame()
        
def main():
    """
    Convert all .cdb files to CSV in the current directory.
    
    Processes each .cdb file found in the script's directory:
    1. Exports to XML using Exporter.exe
    2. Converts XML to pandas DataFrame
    3. Saves as CSV file
    4. Cleans up intermediate XML file
    """
    script_dir = Path(__file__).parent
    cdb_files = list(script_dir.glob('*.cdb'))
    
    if not cdb_files:
        print("No .cdb files found in the current directory.")
        return
    
    print(f"Found {len(cdb_files)} .cdb file(s) to process...")
    
    for cdb_path in cdb_files:
        xml_path = cdb_path.with_suffix('.xml')
        csv_path = cdb_path.with_suffix('.csv')
        
        print(f"Processing {cdb_path.name}...", end=" ")
        
        if export_to_xml(cdb_path.name, xml_path.name, str(script_dir)):
            try:
                # Use cyclist_and_team_data function for cyclist-specific extraction
                df = cyclist_and_team_data(str(xml_path))
                df.to_csv(str(csv_path), index=False)
                xml_path.unlink()  # Clean up intermediate XML
                print(f"✓ Converted to {csv_path.name} ({len(df)} cyclists)")
            except Exception as e:
                print(f"✗ Failed to convert: {e}")
                if xml_path.exists():
                    xml_path.unlink()  # Clean up failed XML
        else:
            print("✗ Failed to export to XML")
    
    print("Processing complete!")

if __name__ == '__main__':
    main()