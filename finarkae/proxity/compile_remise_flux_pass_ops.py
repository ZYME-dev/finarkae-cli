import re
from datetime import datetime
from enum import Enum
from pathlib import Path

import chardet
import pandas as pd
import typer
from pydantic import BaseModel, computed_field
from schwifty import IBAN

from . import console

app = typer.Typer(help="module proxity")


class FileFormat(Enum):
    """Enumeration for different CSV file formats."""

    PRELEVEMENTS = "prelevements"  # Format with "Débiteur" and "Echéance le"
    VIREMENTS = "virements"  # Format with "Bénéficiaire" and "Exécution le"


class FileInfo(BaseModel):
    """Model for file information."""

    name: str
    path: str
    size: str
    extension: str
    encoding: str | None = None
    sheet_name: str
    raw_data: list[str] | None = None  # Store raw file content
    file_format: FileFormat | None = None  # Move file_format here


class Operation(BaseModel):
    debiteur: str
    reference: str
    compte: IBAN
    montant: float
    devise: str
    statut: str

    @computed_field
    @property
    def code(self) -> str | None:
        """Extract operation code using regex to find letters between dashes (e.g., -ABC-)."""
        # Use regex to find letters between dashes
        match = re.search(r"-([A-Z]+)-", self.reference)
        if match:
            return match.group(1)
        return None


class Remise(BaseModel):
    file_info: FileInfo
    date_export: datetime
    ref: str
    libelle: str
    compte: IBAN
    type: str
    statut: str
    date_echeance: datetime
    montant_total: float
    nb_operations: int
    operations: list[Operation]


def detect_encoding(file_path: Path) -> str:
    """Detect file encoding, using Windows-1252 by default for French CSV files."""
    # Default to Windows-1252 for CSV files as they are typically French bank exports
    if file_path.suffix.lower() == ".csv":
        return "windows-1252"

    try:
        with open(file_path, "rb") as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result.get("encoding", "utf-8")

            # Fallback to Windows-1252 if detection is uncertain
            if encoding is None or result.get("confidence", 0) < 0.7:
                return "windows-1252"

            return encoding
    except Exception:
        return "windows-1252"


def load_csv_file(file_path: Path) -> pd.DataFrame | None:
    """Load a CSV file with proper encoding detection and flexible parsing."""
    try:
        encoding = detect_encoding(file_path)

        # Read the file content to find the actual data section
        with open(file_path, encoding=encoding) as f:
            lines = f.readlines()

        # Look for the header row (usually contains column names like "Débiteur", "Référence", etc.)
        data_start_idx = None
        for i, line in enumerate(lines):
            # Check if this line looks like a header (contains typical column names)
            if any(
                keyword in line.lower()
                for keyword in [
                    "débiteur",
                    "référence",
                    "compte",
                    "montant",
                    "statut",
                    "bénéficiaire",
                ]
            ):
                data_start_idx = i
                break

        if data_start_idx is None:
            # If no specific header found, try to find the first line with multiple semicolons
            for i, line in enumerate(lines):
                if line.count(";") >= 2:  # At least 3 columns
                    data_start_idx = i
                    break

        if data_start_idx is not None:
            # Extract only the data portion
            data_lines = lines[data_start_idx:]

            # Try different delimiters common in French CSV files
            for delimiter in [";", ",", "\t"]:
                try:
                    # Create a temporary file-like object from the data lines
                    from io import StringIO

                    data_content = "".join(data_lines)
                    df = pd.read_csv(StringIO(data_content), delimiter=delimiter, on_bad_lines="skip")

                    # Check if we got meaningful data (more than just headers)
                    if len(df.columns) > 1 and len(df) > 0:
                        # Clean empty columns and rows
                        df = df.dropna(how="all")  # Remove completely empty rows
                        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]  # Remove unnamed columns
                        if len(df) > 0:
                            return df
                except Exception:
                    continue

        # Fallback: try loading the entire file
        for delimiter in [";", ",", "\t"]:
            try:
                df = pd.read_csv(
                    file_path,
                    encoding=encoding,
                    delimiter=delimiter,
                    on_bad_lines="skip",
                )
                if len(df.columns) > 1 and len(df) > 0:
                    df = df.dropna(how="all")
                    if len(df) > 0:
                        return df
            except Exception:
                continue

        return None
    except Exception as e:
        console.print(f"[red]Error loading CSV {file_path.name}: {e}[/red]")
        return None


def load_excel_file(file_path: Path) -> pd.DataFrame | None:
    """Load the first sheet of an Excel file."""
    try:
        # Read the first sheet (index 0)
        df = pd.read_excel(file_path, sheet_name=0, engine="openpyxl")
        return df
    except Exception as e:
        console.print(f"[red]Error loading Excel {file_path.name}: {e}[/red]")
        return None


def get_file_info(file_path: Path, format_type: FileFormat | None = None) -> FileInfo:
    """Get comprehensive file information including raw data."""
    file_size = file_path.stat().st_size
    file_size_mb = file_size / (1024 * 1024)
    size_str = f"{file_size_mb:.2f} MB" if file_size_mb >= 0.01 else f"{file_size} bytes"

    encoding = None
    sheet_name = "Sheet1"  # Default for Excel files
    raw_data = None

    # Load file to get additional info
    if file_path.suffix.lower() == ".csv":
        encoding = detect_encoding(file_path)
        sheet_name = "CSV"
        # Read raw data for format detection
        try:
            with open(file_path, encoding=encoding) as f:
                raw_data = f.readlines()
        except Exception:
            pass
    elif file_path.suffix.lower() in [".xls", ".xlsx"]:
        sheet_name = "Sheet1"

    file_info = FileInfo(
        name=file_path.name,
        path=str(file_path.absolute()),
        size=size_str,
        extension=file_path.suffix.lower(),
        encoding=encoding,
        sheet_name=sheet_name,
        raw_data=raw_data,
        file_format=format_type,
    )

    # Auto-detect format if not provided
    if not format_type and raw_data:
        file_info.file_format = detect_file_format(file_info)

    return file_info


def detect_file_format(file_info: FileInfo) -> FileFormat:
    """Detect the format of the CSV file based on its content using position-based approach."""
    if not file_info.raw_data:
        return FileFormat.PRELEVEMENTS  # Default fallback

    content = "\n".join(file_info.raw_data).lower()

    # Check for format indicators by looking for key patterns
    # VIREMENTS files typically have "bénéficiaire" in headers and "exécution" in metadata
    # PRELEVEMENTS files typically have "débiteur" in headers and "echéance" in metadata

    virements_indicators = 0
    prelevements_indicators = 0

    # Check for operation table headers
    if "beneficiaire" in content:  # "bénéficiaire" without accent
        virements_indicators += 2
    if "debiteur" in content:  # "débiteur" without accent
        prelevements_indicators += 2

    # Check for date field patterns
    if "execution" in content and "le" in content:
        virements_indicators += 1
    if "echeance" in content and "le" in content:
        prelevements_indicators += 1

    # Check for operation count patterns
    if "virement" in content:
        virements_indicators += 1
    if "prelevement" in content or "prelement" in content:
        prelevements_indicators += 1

    # Return the format with the highest score
    if virements_indicators > prelevements_indicators:
        return FileFormat.VIREMENTS
    else:
        return FileFormat.PRELEVEMENTS


def extract_date_from_metadata(metadata: dict[str, str], format_type: FileFormat) -> datetime | None:
    """Extract date from metadata based on file format using position-based approach."""
    # Look for date fields by checking if the key contains the relevant words (case-insensitive)
    for key, value in metadata.items():
        key_lower = key.lower()

        if format_type == FileFormat.VIREMENTS:
            # Look for execution date fields (contains "execution" and "le")
            if "execution" in key_lower and "le" in key_lower:
                try:
                    return datetime.strptime(value.strip(), "%d/%m/%Y")
                except ValueError:
                    continue
        else:  # PRELEVEMENTS
            # Look for due date fields (contains "echeance" and "le")
            if "echeance" in key_lower and "le" in key_lower:
                try:
                    return datetime.strptime(value.strip(), "%d/%m/%Y")
                except ValueError:
                    continue

    # Fallback: exact key matching for specific known patterns including encoding variations
    date_fields = []
    if format_type == FileFormat.VIREMENTS:
        date_fields = [
            "Exécution le",
            "Exécution le :",
            "Execution le",
            "Execution le :",
            "Exécution le",
            "Exécution le :",  # Encoded variations
        ]
    else:  # PRELEVEMENTS
        date_fields = [
            "Echéance le",
            "Echéance le :",
            "Echeance le",
            "Echeance le :",
            "Echéance le",
            "Echéance le :",
            "Echéance le",
            "Echéance le :",  # Encoded variations
        ]

    for field in date_fields:
        if field in metadata:
            try:
                return datetime.strptime(metadata[field].strip(), "%d/%m/%Y")
            except ValueError:
                continue

    return None


def extract_export_date_from_metadata(metadata: dict[str, str]) -> datetime | None:
    """Extract export date from metadata using position-based approach."""
    # Look for export date fields by checking if the key contains "export"
    for key, value in metadata.items():
        key_lower = key.lower()
        if "export" in key_lower:
            date_str = value.strip()
            if date_str:
                try:
                    return datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S")
                except ValueError:
                    # Try without time if the format is different
                    try:
                        return datetime.strptime(date_str.split()[0], "%d/%m/%Y")
                    except ValueError:
                        continue

    return None


def extract_ref_from_metadata(metadata: dict[str, str]) -> tuple:
    """Extract reference and libelle from metadata using position-based approach."""
    # Look for REF field
    ref_line = metadata.get("REF", "").strip()
    if not ref_line:
        return "", ""

    # Parse "FR59ZZZ86395E-412545;LIBELLE : PRINC. *5264*" or similar
    ref = ""
    libelle = ""

    # The ref_line should now contain everything after "REF : "
    if ";LIBELLE" in ref_line.upper():
        # Find the libelle part (case-insensitive)
        ref_full = ref_line.split(";")[0]
        libelle_part = ref_line.split(";", 1)[1]
        # Remove "LIBELLE :" prefix (case-insensitive)
        if ":" in libelle_part:
            libelle = libelle_part.split(":", 1)[1].strip()
        else:
            libelle = libelle_part.strip()
    else:
        ref_full = ref_line

    # Extract just the main reference (before the dash)
    if "-" in ref_full:
        ref = ref_full.split("-")[0].strip()
    else:
        ref = ref_full.strip()

    return ref, libelle


def extract_operation_count_from_metadata(metadata: dict[str, str], format_type: FileFormat) -> int:
    """Extract operation count from metadata using position-based approach."""
    # Look for count fields by checking if the key contains relevant words
    for key, value in metadata.items():
        key_lower = key.lower()

        if format_type == FileFormat.VIREMENTS:
            # Look for virement count fields
            if "nombre" in key_lower and "virement" in key_lower:
                count_str = value.strip()
                if count_str and count_str.isdigit():
                    return int(count_str)
        else:  # PRELEVEMENTS
            # Look for prélèvement count fields
            if "nombre" in key_lower and ("prelevement" in key_lower or "prelement" in key_lower):
                count_str = value.strip()
                if count_str and count_str.isdigit():
                    return int(count_str)

    # Fallback: exact key matching for specific known patterns
    count_fields = []
    if format_type == FileFormat.VIREMENTS:
        count_fields = [
            "Nombre de virement(s)",
            "Nombre de virement(s) :",
            "Nombre de virements",
        ]
    else:  # PRELEVEMENTS
        count_fields = [
            "Nombre de prélèvement(s)",
            "Nombre de prélèvement(s) :",
            "Nombre de prélèvements",
            "Nombre de prélèvement(s)",
            "Nombre de prélèvement(s) :",  # Encoded variations
        ]

    for field in count_fields:
        if field in metadata:
            count_str = metadata[field].strip()
            if count_str and count_str.isdigit():
                return int(count_str)

    return 0


def parse_remise_prelevements(file_info: FileInfo) -> Remise | None:
    """Parse a CSV file in 'prélèvements' format."""
    return parse_remise_csv_with_format(file_info, FileFormat.PRELEVEMENTS)


def parse_remise_virements(file_info: FileInfo) -> Remise | None:
    """Parse a CSV file in 'virements' format."""
    return parse_remise_csv_with_format(file_info, FileFormat.VIREMENTS)


def parse_remise_csv_with_format(file_info: FileInfo, format_type: FileFormat) -> Remise | None:
    """Parse a CSV file with a specific format."""
    try:
        if not file_info.raw_data:
            console.print(f"[red]No raw data available for {file_info.name}[/red]")
            return None

        # Update file_info with the format if not already set
        if not file_info.file_format:
            file_info.file_format = format_type

        lines = file_info.raw_data

        # Parse metadata from the top of the file
        metadata = {}
        operations_start_idx = None

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Look for metadata fields
            if ":" in line or ";" in line:
                parts = line.split(";") if ";" in line else line.split(":")
                if len(parts) >= 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    metadata[key] = value
                    # Handle special case for REF line which spans multiple parts
                    if key.startswith("REF "):
                        # Get everything after "REF : "
                        ref_content = line[line.find(":") + 1 :].strip()
                        metadata["REF"] = ref_content

            # Find where operations start - look for header row with typical column names
            line_lower = line.lower()
            if format_type == FileFormat.VIREMENTS:
                # Look for virements table header (contains bénéficiaire and reference/paiement)
                if "bénéficiaire" in line_lower and ("référence" in line_lower or "paiement" in line_lower):
                    operations_start_idx = i
                    break
            else:  # PRELEVEMENTS
                # Look for prelevements table header (contains débiteur and référence)
                if "débiteur" in line_lower and "référence" in line_lower:
                    operations_start_idx = i
                    break

        if operations_start_idx is None:
            console.print(f"[yellow]Warning: No operations found in {file_info.name}[/yellow]")
            operations_start_idx = len(lines)  # No operations to parse

        # Parse operations
        operations = []
        for i in range(operations_start_idx + 1, len(lines)):
            line = lines[i].strip()
            if not line or line.count(";") < 5:
                continue

            parts = line.split(";")
            if len(parts) >= 6:
                try:
                    # Clean the IBAN (remove spaces)
                    iban_str = parts[2].strip().replace(" ", "")
                    iban = IBAN(iban_str)

                    # Parse amount (replace comma with dot for French decimal format)
                    montant_str = parts[3].strip().replace(",", ".")
                    montant = float(montant_str)

                    operation = Operation(
                        debiteur=parts[0].strip(),
                        reference=parts[1].strip(),
                        compte=iban,
                        montant=montant,
                        devise=parts[4].strip(),
                        statut=parts[5].strip(),
                    )
                    operations.append(operation)
                except (ValueError, Exception) as e:
                    console.print(f"[dim]Skipping invalid operation: {e}[/dim]")
                    continue

        # Parse metadata into structured format
        try:
            # Extract date export
            date_export = extract_export_date_from_metadata(metadata)
            if not date_export:
                date_export = datetime.now()

            # Extract reference and other info
            ref, libelle = extract_ref_from_metadata(metadata)

            # Extract account info
            compte_line = metadata.get("COMPTE", "")
            compte_str = (
                compte_line.split(";")[0].replace(" ", "") if ";" in compte_line else compte_line.replace(" ", "")
            )
            compte = IBAN(compte_str) if compte_str else IBAN("FR7630004008280001330030876")  # fallback

            type_info = compte_line.split(";TYPE : ")[-1] if ";TYPE : " in compte_line else "Prélèvement standard"

            # Extract échéance/exécution date using format-aware function
            date_echeance = extract_date_from_metadata(metadata, format_type)
            if not date_echeance:
                date_echeance = datetime.now()

            # Extract total amount
            montant_str = metadata.get("Montant total", "")
            if not montant_str:
                montant_str = metadata.get("Montant total ", "")  # Try with space
            if not montant_str:
                montant_str = metadata.get("Montant total :", "")  # Try with colon
            montant_str = montant_str.replace(",", ".").replace(" EUR", "").strip()
            montant_total = float(montant_str) if montant_str else sum(op.montant for op in operations)

            # Extract number of operations using format-aware function
            nb_operations = extract_operation_count_from_metadata(metadata, format_type)
            if nb_operations == 0:
                nb_operations = len(operations)

            remise = Remise(
                file_info=file_info,
                date_export=date_export,
                ref=ref,
                libelle=libelle,
                compte=compte,
                type=type_info,
                statut=metadata.get("STATUT", "A valider"),
                date_echeance=date_echeance,
                montant_total=montant_total,
                nb_operations=nb_operations,
                operations=operations,
            )

            return remise

        except Exception as e:
            console.print(f"[red]Error parsing metadata from {file_info.name}: {e}[/red]")
            return None

    except Exception as e:
        console.print(f"[red]Error parsing {file_info.name}: {e}[/red]")
        return None


def parse_remise_csv(file_path: Path) -> Remise | None:
    """Parse a CSV file into a Remise object with automatic format detection."""
    file_info = get_file_info(file_path)
    format_type = detect_file_format(file_info)

    console.print(f"[dim]Detected format: {format_type.value} for {file_info.name}[/dim]")

    return parse_remise_csv_with_format(file_info, format_type)


def strip_filename_prefix(filename: str) -> str:
    """Strip LISTE_OPERATIONS_ prefix from filename for display."""
    if filename.startswith("LISTE_OPERATIONS_"):
        return filename[17:]  # Remove "LISTE_OPERATIONS_" prefix
    return filename


def export_remises_to_excel(
    remises: list[Remise],
    output_dir: Path,
    filename_prefix: str = "ops",
    timestamp: bool = True,
    date_format: str = "DD/MM/YYYY",
    monetary_format: str = "[$€-40C] #,##0.00",
    **kwargs,
) -> Path:
    """Export remises to Excel with professional formatting and total row, using XlsxWriter only."""
    from datetime import datetime

    import xlsxwriter

    # Generate filename
    if timestamp:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_filename = f"{filename_prefix}_{timestamp_str}.xlsx"
    else:
        excel_filename = f"{filename_prefix}.xlsx"

    excel_path = output_dir / excel_filename

    # Collect all operations for Excel export
    all_operations = []
    for remise in remises:
        for i, operation in enumerate(remise.operations):
            export_row = {
                "File Name": strip_filename_prefix(remise.file_info.name),
                "File Format": (remise.file_info.file_format.value if remise.file_info.file_format else "Unknown"),
                "Date Export": remise.date_export.strftime("%d/%m/%Y"),
                "Date Échéance": remise.date_echeance.strftime("%d/%m/%Y"),
                "Référence Remise": remise.ref,
                "Libellé": remise.libelle,
                "Compte Remise": str(remise.compte),
                "Type Remise": remise.type,
                "Statut Remise": remise.statut,
                "Montant Total": remise.montant_total,
                "Op #": i + 1,
                "Op Débiteur": operation.debiteur,
                "Op Référence": operation.reference,
                "Op Code": operation.code or "",
                "Op Compte": str(operation.compte),
                "Op Montant": operation.montant,
                "Op Statut": operation.statut,
            }
            all_operations.append(export_row)

    if not all_operations:
        raise ValueError("No operations to export")

    columns = list(all_operations[0].keys())
    data = [[row.get(col, "") for col in columns] for row in all_operations]

    workbook = xlsxwriter.Workbook(str(excel_path))
    worksheet = workbook.add_worksheet("OPS")

    # Write headers
    worksheet.write_row(0, 0, columns)

    # Write data rows
    for i, row in enumerate(data, start=1):
        worksheet.write_row(i, 0, row)

    # Set formats
    money_fmt = workbook.add_format({"num_format": monetary_format})
    date_fmt = workbook.add_format({"num_format": date_format})
    int_fmt = workbook.add_format({"num_format": "0"})

    for col_idx, col_name in enumerate(columns):
        if col_name in ["Montant Total", "Op Montant"]:
            worksheet.set_column(col_idx, col_idx, 15, money_fmt)
        elif col_name in ["Date Export", "Date Échéance"]:
            worksheet.set_column(col_idx, col_idx, 12, date_fmt)
        elif col_name == "Op #":
            worksheet.set_column(col_idx, col_idx, 6, int_fmt)
        else:
            worksheet.set_column(col_idx, col_idx, 15)

    # Table range: header + data + total row
    table_first_row = 0
    table_last_row = len(data) + 1  # +1 for total row
    table_first_col = 0
    table_last_col = len(columns) - 1

    # Build columns for table
    table_columns = []
    for col_name in columns:
        if col_name == "File Name":
            table_columns.append({"header": col_name, "total_string": "Total"})
        elif col_name == "File Format":
            table_columns.append({"header": col_name, "total_function": "count"})
        elif col_name in ["Montant Total", "Op Montant"]:
            table_columns.append({"header": col_name, "total_function": "sum"})
        else:
            table_columns.append({"header": col_name})

    worksheet.add_table(
        table_first_row,
        table_first_col,
        table_last_row,
        table_last_col,
        {
            "name": "OPS",
            "columns": table_columns,
            "style": "Table Style Medium 9",
            "total_row": True,
        },
    )

    workbook.close()
    return excel_path
