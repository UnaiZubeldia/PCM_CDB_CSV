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
        
def xml_to_df(file_path):
    """
    Convert XML file to pandas DataFrame.
    
    Args:
        file_path (str): Path to the XML file
        
    Returns:
        pd.DataFrame: DataFrame containing the table data
        
    Raises:
        ValueError: If no table is found in the XML file
    """
    tree = ET.parse(file_path)
    table = tree.find('.//Table')
    if table is None:
        raise ValueError("No table found in XML file.")

    # Extract column names and data more efficiently
    columns = []
    data = []
    
    for col in table.findall('Column'):
        column_name = col.get('ColumnName')
        if column_name:
            columns.append(column_name)
            data.append([cell.text for cell in col.findall('Cell')])

    # Ensure all columns have the same length
    if data:
        max_length = max(len(col_data) for col_data in data)
        data = [col_data + [None] * (max_length - len(col_data)) for col_data in data]
        return pd.DataFrame(dict(zip(columns, data)))
    
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
                df = xml_to_df(str(xml_path))
                df.to_csv(str(csv_path), index=False)
                xml_path.unlink()  # Clean up intermediate XML
                print(f"✓ Converted to {csv_path.name}")
            except Exception as e:
                print(f"✗ Failed to convert: {e}")
                if xml_path.exists():
                    xml_path.unlink()  # Clean up failed XML
        else:
            print("✗ Failed to export to XML")
    
    print("Processing complete!")

if __name__ == '__main__':
    main()