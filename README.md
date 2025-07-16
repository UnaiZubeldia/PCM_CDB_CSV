# CDB to CSV Converter

A simple Python script to convert PRO CYCLING MANAGER .cdb database files to CSV format using XML as an intermediate format.

## Features

- ✅ Batch processing of all .cdb files in a directory
- ✅ Automatic cleanup of intermediate XML files
- ✅ Progress feedback during conversion
- ✅ Error handling for failed conversions
- ✅ Simple one-command execution

## Requirements

- Python 3.6+
- pandas
- Exporter.exe (must be in the same directory as the script)

## Installation

1. Clone this repository or download the script
2. Install required Python packages:

   ```bash
   pip install pandas
   ```

3. Ensure `Exporter.exe` is in the same directory as `automated_export.py`

## Usage

```bash
python automated_export.py
```

The script will:

1. Find all `.cdb` files in the current directory
2. Convert each file to XML using `Exporter.exe`
3. Parse the XML and convert to CSV format
4. Save the CSV file with the same name as the original .cdb file
5. Clean up intermediate XML files

## Example Output

```text
Found 3 .cdb file(s) to process...
Processing PCM20 WDB20.cdb... ✓ Converted to PCM20 WDB20.csv
Processing PCM21 WDB21.cdb... ✓ Converted to PCM21 WDB21.csv
Processing PCM22 WDB22.cdb... ✓ Converted to PCM22 WDB22.csv
Processing complete!
```

## File Structure

```text
your-directory/
├── automated_export.py
├── Exporter.exe
├── file1.cdb
├── file2.cdb
└── ... (other .cdb files)
```

After running the script:

```text
your-directory/
├── automated_export.py
├── Exporter.exe
├── file1.cdb
├── file1.csv  ← Generated
├── file2.cdb
├── file2.csv  ← Generated
└── ... (other files)
```

## Error Handling

The script includes robust error handling:

- Missing `Exporter.exe` - Script will skip files that can't be exported
- Invalid XML structure - Script will report conversion errors
- File permission issues - Script will continue with other files

## License

This project is open source. Feel free to use, modify, and distribute.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
