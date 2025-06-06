"""Proxity module for Finarkae CLI."""

from pathlib import Path

import typer
from rich.table import Table

from . import console
from .compile_remise_flux_pass_ops import (
    Remise,
    export_remises_to_excel,
    parse_remise_csv,
    strip_filename_prefix,
)

app = typer.Typer(help="commandes relatives à proxity")


@app.command("comp-remises-flux-pass")
def compile_remise_flux_pass_ops(
    directory: str | None = typer.Option(
        None,
        "--dir",
        "-d",
        help="Répertoire à scanner pour les fichiers csv et xls (par défaut: répertoire courant)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Affiche les informations détaillées incluant un aperçu des données",
    ),
):
    """Compile les opérations de remise PASS à partir des fichier bancaires csv. Exporte les résultats dans un fichier excel. Travaille dans le répertoire courant par défaut."""
    # Use current directory if no directory specified
    search_dir = Path(directory) if directory else Path.cwd()

    if not search_dir.exists():
        console.print(f"[red]Error: Directory '{search_dir}' does not exist[/red]")
        raise typer.Exit(1)

    if not search_dir.is_dir():
        console.print(f"[red]Error: '{search_dir}' is not a directory[/red]")
        raise typer.Exit(1)

    # Find all CSV files (focus on CSV for now)
    csv_files = []
    console.print(f"[yellow]Scanning directory: {search_dir}[/yellow]")

    for file_path in search_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() == ".csv":
            csv_files.append(file_path)

    if not csv_files:
        console.print(f"[yellow]No CSV files found in {search_dir}[/yellow]")
        return

    # Parse all remises
    remises: list[Remise] = []
    for file_path in csv_files:
        console.print(f"[dim]Processing: {file_path.name}[/dim]")
        remise = parse_remise_csv(file_path)
        if remise:
            remises.append(remise)

    if not remises:
        console.print("[yellow]No valid remises found[/yellow]")
        return

    # Create and display operations table with grouped filenames
    table = Table(title=f"Operations from {len(remises)} Remises in {search_dir}")
    table.add_column("Rem File", style="cyan", no_wrap=False)
    table.add_column("Rem Export", style="blue")
    table.add_column("Rem Échéance", style="green")
    table.add_column("Rem Montant Total", style="yellow")
    table.add_column("Rem Nb Ops", style="bright_blue")
    table.add_column("Op #", style="blue")
    table.add_column("Op Débiteur", style="magenta")
    table.add_column("Op Réf", style="dim")
    table.add_column("Op Territoire", style="green")
    table.add_column("Op Code", style="cyan")
    table.add_column("Op Montant", style="yellow")
    table.add_column("Op Statut", style="red")

    # Display operations table
    for remise in remises:
        # Validate operation count
        actual_op_count = len(remise.operations)
        expected_op_count = remise.nb_operations

        if actual_op_count != expected_op_count:
            console.print(f"[yellow]⚠️  Warning: File {remise.file_info.name}[/yellow]")
            console.print(
                f"[yellow]   Expected {expected_op_count} operations but found {actual_op_count} operation lines[/yellow]"
            )
            console.print("[yellow]   This might indicate a different file format or parsing issue[/yellow]")

        for i, operation in enumerate(remise.operations):
            # Format status with green checkmark for "Accepté"
            status_display = operation.statut
            if operation.statut == "Accepté":
                status_display = "✅"

            # For table display: show filename only on first row of each file group
            filename_display = strip_filename_prefix(remise.file_info.name) if i == 0 else ""
            export_display = remise.date_export.strftime("%d/%m/%Y") if i == 0 else ""
            echeance_display = remise.date_echeance.strftime("%d/%m/%Y") if i == 0 else ""
            montant_total_display = f"{remise.montant_total:.2f}" if i == 0 else ""
            nb_ops_display = str(remise.nb_operations) if i == 0 else ""

            row_data = [
                filename_display,
                export_display,
                echeance_display,
                montant_total_display,
                nb_ops_display,
                str(i + 1),
                operation.debiteur,
                operation.reference,
                operation.code_territoire or "",
                operation.code or "",
                f"{operation.montant:.2f}",
                status_display,
            ]

            table.add_row(*row_data)

        # Add section separator between files (creates horizontal line)
        if remise != remises[-1]:  # Don't add separator after last remise
            table.add_section()

    console.print(table)

    # Export to Excel using the standalone function
    try:
        excel_path = export_remises_to_excel(
            remises=remises,
            output_dir=search_dir,
            filename_prefix="ops",
            timestamp=True,
        )

        # Count total operations for reporting
        total_operations_exported = sum(len(remise.operations) for remise in remises)

        console.print(f"\n[green]✅ Exported to Excel table: {excel_path}[/green]")
        console.print("[green]   • Table name: 'OPS' with filters, alternating row colors, and total row[/green]")
        console.print(f"[green]   • {total_operations_exported} rows exported with all available fields[/green]")

    except Exception as e:
        console.print(f"[red]Error exporting to Excel: {e}[/red]")

    # Summary statistics
    total_operations = sum(len(remise.operations) for remise in remises)
    total_amount = sum(remise.montant_total for remise in remises)
    accepted_operations = sum(1 for remise in remises for op in remise.operations if op.statut == "Accepté")

    console.print("\n[green]Summary:[/green]")
    console.print(f"  • Total remises: {len(remises)}")
    console.print(f"  • Total operations: {total_operations}")
    console.print(f"  • Accepted operations: {accepted_operations}")
    console.print(f"  • Total amount: {total_amount:.2f} EUR")

    if verbose:
        console.print("\n[cyan]Remises details:[/cyan]")
        for remise in remises:
            console.print(f"  • {remise.file_info.name}: {len(remise.operations)} ops, {remise.montant_total:.2f} EUR")
