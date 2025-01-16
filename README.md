# Little Orphan Annie's AstroGraph (anniegraph)

!anniegraph.webp

Anniegraph is a tool for generating graphs from astronomy data using either static (matplotlib) or interactive (Plotly) visualizations. The configuration can be provided via command-line arguments or a YAML configuration file.

## Features

- Generate static or interactive graphs
- Customize graph appearance with colors, shapes, and styles
- Include uncertainties in the graph
- Specify x-axis and y-axis titles
- Export configuration to a YAML file

## Requirements

- Python 3.6+
- pandas
- matplotlib
- plotly
- pyyaml

## Installation

Install the required Python packages using pip:

```bash
pip install pandas matplotlib plotly pyyaml
```

Clone the repository:


```bash
git clone https://github.com/sashakarcz/annigraph.git
```

```bash
cd annigraph
```

Create the necessary directories and symlinks:

```bash
sudo mkdir -p /usr/local/lib/annigraph
sudo ln -s $(pwd)/annigraph.py /usr/local/lib/annigraph/annigraph.py
sudo tee /usr/local/bin/annigraph <<EOF
#!/usr/bin/env bash
python /usr/local/lib/annigraph/annigraph.py "\$@"
EOF
sudo chmod +x /usr/local/bin/annigraph
```

Verify Installation:

```bash
which annigraph
```

You should see `/usr/local/bin/annigraph` in the output.

## Usage

Run `annigraph` with the appropriate arguments:

```bash
annigraph --file <path_to_data_file> --x-axis <x_axis_column> --y-axes <y_axis_columns> [options]
```

### Command-Line Arguments

--file: Path to the input file (required if not using --import-config).
--delimiter: Delimiter used in the file (default: ,).
--x-axis: Column to use for the x-axis.
--y-axes: Comma-separated list of columns to use for the y-axis.
--x-min: Minimum value for the x-axis.
--x-max: Maximum value for the x-axis.
--y-min: Minimum value for the y-axis.
--y-max: Maximum value for the y-axis.
--colors: Comma-separated list of colors for the graph.
--shapes: Comma-separated list of shapes for the graph.
--legend: Include a legend in the graph.
--dpi: DPI for the output graph (default: 300).
--font-size: Font size for labels and legends (default: 12).
--output-file: Path to save the output graph.
--output-format: Output file format (default: png).
--interactive: Generate an interactive graph.
--use-uncertainties: Include uncertainties in the graph.
--style: Style for the graph (default: petroff10).
--x-ticks: Number of tick marks on the x-axis.
--column-names: Pairs of original and new column names (e.g., OriginalName1 NewName1 OriginalName2 NewName2).
--import-config: Path to a YAML configuration file.
--export-config: Path to save the configuration as a YAML file.
--x-axis-title: Title for the x-axis.
--y-axis-title: Title for the y-axis.

## Example

### Input Data (astronomy_data.csv)

```
Time,Dust_Temp,delta T,Ice_Temp,Ice_Temp_sigup,Ice_Temp_sigdown,Dust_Temp_sigup,Dust_Temp_sigdown
1.0,187,-0.7,250,10,20,24,33
2.0,166,-0.5,260,20,30,16,23
3.0,173,0.3,255,10,20,52,180
```

### CLI Configuration:

```bash
annigraph --file astronomy_data.csv \
--delimiter "," \
--x-axis Time \
--y-axes Dust_Temp,Ice_Temp \
--x-min 0 \
--x-max 4 \
--colors blue,green \
--shapes o,s \
--legend \
--column-names "Dust Temperature=Dust_Temp" "Ice Temperature=Ice_Temp" \
--dpi 300 \
--font-size 12 \
--use-uncertainties \
--y-axis-title "Observed Temperature" \
--output-file graph.png \
--output-format png \
--export-config plot.yaml

### YAML Configuration
Create a YAML configuration file (e.g., plot.yaml) with the desired settings:

```yaml
colors:
- blue
- green
column_names:
  - "Dust Temperature=Dust_Temp"
  - "Ice Temperature=Ice_Temp"
delimiter: ','
dpi: 300
font_size: 12
interactive: false
legend: true
output_file: graph.png
output_format: png
shapes:
- o
- s
style: petroff10
use_uncertainties: true
x_axis: Time
x_axis_title: Time
x_max: 4
x_min: 0.0
x_ticks: 6
y_axes:
- Dust_Temp
- Ice_Temp
y_axis_title: Observed Temperature
```

### Run the script with the YAML configuration:

```bash
annigraph --import-config plot.yaml --file astronomy_data.csv
```

### Generated Graph
!graph.png

### Interactive Plotting

```bash
pnnigraph --file astronomy_data.csv\
--delimiter ","\
--x-axis Time\
--y-axes Dust_Temp,Ice_Temp\
--x-min 0\
--x-max 4\
--colors blue,green\
--shapes o,s\
--legend\ 
--column-names "Ice_Temp=Ice Temperature" "Dust_Temp=Dust Temperature"\
--dpi 300\
--font-size 12\
--interactive\
--use-uncertainties\
--y-axis-title "Observed Temperature"\
--output-file graph.html
```
#### Generated Plot
!interactive.png
