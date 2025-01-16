import argparse
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import yaml
import webbrowser

class DataProcessor:
    """
    Handles loading and processing data from a CSV or tab-delimited file.
    """
    def __init__(self, file_path, delimiter):
        """
        Initialize the DataProcessor with a file path and delimiter.

        Args:
            file_path (str): Path to the input file.
            delimiter (str): Delimiter used in the file (e.g., "," for CSV, "\t" for tab-delimited).
        """
        self.file_path = file_path
        self.delimiter = delimiter
        self.data = self.load_data()

    def load_data(self):
        """
        Load the data file into a pandas DataFrame.

        Returns:
            pd.DataFrame: Data from the file.

        Raises:
            ValueError: If there is an issue loading the file.
        """
        try:
            data = pd.read_csv(self.file_path, delimiter=self.delimiter)
            return data
        except Exception as e:
            raise ValueError(f"Error loading data file: {e}")

    def has_column(self, column_name):
        """
        Check if a column exists in the DataFrame.

        Args:
            column_name (str): Name of the column to check.

        Returns:
            bool: True if the column exists, False otherwise.
        """
        return column_name in self.data.columns

    def get_uncertainties(self):
        """
        Identify uncertainty columns ending with 'sigup' and 'sigdown'.

        Returns:
            tuple: Two lists containing columns for 'sigup' and 'sigdown'.
        """
        sigup_columns = [col for col in self.data.columns if col.endswith("sigup")]
        sigdown_columns = [col for col in self.data.columns if col.endswith("sigdown")]
        return sigup_columns, sigdown_columns

class GraphConfig:
    """
    Stores and parses configuration options for the graph.
    """
    def __init__(self, args=None, import_config=None):
        """
        Initialize the GraphConfig with parsed command-line arguments or a YAML configuration file.

        Args:
            args (argparse.Namespace): Parsed command-line arguments.
            import_config (str): Path to a YAML configuration file.
        """
        if import_config:
            with open(import_config, 'r') as file:
                config = yaml.safe_load(file)
            self.x_axis = config.get("x_axis")
            self.y_axes = config.get("y_axes", [])
            self.x_min = config.get("x_min")
            self.x_max = config.get("x_max")
            self.y_min = config.get("y_min")
            self.y_max = config.get("y_max")
            self.colors = config.get("colors", [])
            self.shapes = config.get("shapes", [])
            self.legend = config.get("legend", False)
            self.dpi = config.get("dpi", 300)
            self.font_size = config.get("font_size", 12)
            self.output_file = config.get("output_file")
            self.output_format = config.get("output_format", "png")
            self.interactive = config.get("interactive", False)
            self.use_uncertainties = config.get("use_uncertainties", False)
            self.delimiter = config.get("delimiter", ",")
            self.column_names = self.parse_column_names(config.get("column_names", []))
            self.x_axis_title = config.get("x_axis_title", self.x_axis)
            self.y_axis_title = config.get("y_axis_title", " / ".join(self.y_axes))
            self.style = config.get("style", "petroff10")
            self.x_ticks = config.get("x_ticks", None)
            self.validate_config()
        elif args:
            self.x_axis = args.x_axis
            self.y_axes = args.y_axes.split(",") if args.y_axes else []
            self.x_min = args.x_min
            self.x_max = args.x_max
            self.y_min = args.y_min
            self.y_max = args.y_max
            self.colors = args.colors.split(",") if args.colors else []
            self.shapes = args.shapes.split(",") if args.shapes else []
            self.legend = args.legend
            self.dpi = args.dpi
            self.font_size = args.font_size
            self.output_file = args.output_file
            self.output_format = args.output_format
            self.interactive = args.interactive
            self.use_uncertainties = args.use_uncertainties
            self.delimiter = args.delimiter
            self.column_names = self.parse_column_names(args.column_names) if args.column_names else {}
            self.x_axis_title = args.x_axis_title if args.x_axis_title else self.x_axis
            self.y_axis_title = args.y_axis_title if args.y_axis_title else " / ".join(self.y_axes)
            self.style = args.style if args.style else "petroff10"
            self.x_ticks = args.x_ticks

        if not self.output_file:
            raise ValueError("Output file must be specified either in the command-line arguments or in the configuration file.")

    def parse_column_names(self, column_names_list):
        """
        Parse the column names list into a dictionary.

        Args:
            column_names_list (list): List of column name mappings in the format "Display Name=Column Name".

        Returns:
            dict: Dictionary of column name mappings.
        """
        column_names = {}
        for item in column_names_list:
            display_name, column_name = item.split("=")
            column_names[column_name.strip()] = display_name.strip()
        return column_names

    def validate_config(self):
        """
        Validate the configuration to ensure all required fields are present.
        """
        required_fields = ["x_axis", "y_axes", "output_file"]
        for field in required_fields:
            if getattr(self, field) is None:
                raise ValueError(f"Missing required configuration field: {field}")

    def export_to_yaml(self, output_path):
        """
        Export the current configuration to a YAML file.

        Args:
            output_path (str): Path to save the YAML configuration file.
        """
        config_dict = {
            "x_axis": self.x_axis,
            "y_axes": self.y_axes,
            "x_min": self.x_min,
            "x_max": self.x_max,
            "y_min": self.y_min,
            "y_max": self.y_max,
            "colors": self.colors,
            "shapes": self.shapes,
            "legend": self.legend,
            "dpi": self.dpi,
            "font_size": self.font_size,
            "output_file": self.output_file,
            "output_format": self.output_format,
            "interactive": self.interactive,
            "use_uncertainties": self.use_uncertainties,
            "delimiter": self.delimiter,
            "column_names": [f"{v}={k}" for k, v in self.column_names.items()],
            "x_axis_title": self.x_axis_title,
            "y_axis_title": self.y_axis_title,
            "style": self.style,
            "x_ticks": self.x_ticks
        }
        with open(output_path, 'w') as file:
            yaml.safe_dump(config_dict, file)

class Graph:
    """
    Handles the rendering of graphs based on configuration and data.
    """
    def __init__(self, config, data_processor):
        """
        Initialize the Graph with configuration and data.

        Args:
            config (GraphConfig): Configuration for the graph.
            data_processor (DataProcessor): Processed data.
        """
        self.config = config
        self.data_processor = data_processor
        self.rename_columns()
        self.update_y_axes()

    def rename_columns(self):
        """
        Rename columns in the data according to the provided column mapping.
        """
        print("Original columns:", self.data_processor.data.columns)  # Debugging statement
        self.data_processor.data.rename(columns=self.config.column_names, inplace=True)
        print("Renamed columns:", self.data_processor.data.columns)  # Debugging statement

    def update_y_axes(self):
        """
        Update y_axes to use the renamed columns.
        """
        self.config.y_axes = [self.config.column_names.get(y_axis, y_axis) for y_axis in self.config.y_axes]
        print("Updated y-axes:", self.config.y_axes)  # Debugging statement

    def render(self):
        """
        Render the graph as either static or interactive based on configuration.
        """
        if self.config.interactive:
            self._render_interactive()
        else:
            self._render_static()

    def _render_static(self):
        """
        Render a static graph using matplotlib.
        """
        # Set a style and configure the font
        plt.style.use(self.config.style)
        plt.rcParams.update({
            "font.family": "DejaVu Sans",
            "axes.labelsize": self.config.font_size,
            "font.size": self.config.font_size,
            "legend.fontsize": self.config.font_size,
            "xtick.labelsize": self.config.font_size,
            "ytick.labelsize": self.config.font_size,
            "axes.facecolor": "white",
            "figure.facecolor": "white"
        })

        plt.figure(dpi=self.config.dpi)

        x = self.data_processor.data[self.config.x_axis]

        for i, y_axis in enumerate(self.config.y_axes):
            y_axis = y_axis.strip()  # Ensure no leading/trailing spaces
            print(f"Processing y-axis: {y_axis}")  # Debugging statement
            y = self.data_processor.data[y_axis]

            delta_t_exists = self.data_processor.has_column("delta T")

            if delta_t_exists:
                delta_t = self.data_processor.data["delta T"]
                for idx, value in delta_t.items():
                    shape = self.config.shapes[0] if value >= 0 else "o"
                    color = self.config.colors[i % len(self.config.colors)]
                    plt.scatter(
                        x[idx], y[idx],
                        c=color if value >= 0 else "none",
                        edgecolors=color if value < 0 else None,
                        marker=shape,
                        label=self.config.column_names.get(y_axis, y_axis) if idx == 0 else ""  # Use original column name for label
                    )
            else:
                color = self.config.colors[i % len(self.config.colors)]
                shape = self.config.shapes[i % len(self.config.shapes)]
                plt.scatter(x, y, c=color, marker=shape, label=self.config.column_names.get(y_axis, y_axis))

            if self.config.use_uncertainties:
                sigup_column = f"{y_axis}_sigup"
                sigdown_column = f"{y_axis}_sigdown"
                if self.data_processor.has_column(sigup_column) and self.data_processor.has_column(sigdown_column):
                    yerr = [
                        self.data_processor.data[sigdown_column],
                        self.data_processor.data[sigup_column]
                    ]
                    plt.errorbar(x, y, yerr=yerr, fmt="none", ecolor=color)

        plt.xlabel(self.config.x_axis_title)
        plt.ylabel(self.config.y_axis_title)
        if (self.config.legend):
            plt.legend()
        if (self.config.x_ticks):
            plt.xticks(ticks=range(int(self.config.x_min), int(self.config.x_max) + 1, int((self.config.x_max - self.config.x_min) / self.config.x_ticks)))
        plt.savefig(self.config.output_file, format=self.config.output_format)
        plt.close()

    def _render_interactive(self):
        """
        Render an interactive graph using Plotly.
        """
        x = self.data_processor.data[self.config.x_axis]

        # Mapping Matplotlib markers to Plotly symbols
        marker_mapping = {
            "o": "circle",
            "s": "square",
            "^": "triangle-up",
            "v": "triangle-down",
            "<": "triangle-left",
            ">": "triangle-right",
            "d": "diamond",
            "h": "hexagon",
            "+": "cross",
            "x": "x"
        }

        fig = go.Figure()
        delta_t_exists = self.data_processor.has_column("delta T")

        for i, y_axis in enumerate(self.config.y_axes):
            y_axis = y_axis.strip()  # Ensure no leading/trailing spaces
            y = self.data_processor.data[y_axis]

            if delta_t_exists:
                delta_t = self.data_processor.data["delta T"]
                for idx, value in delta_t.items():
                    shape = marker_mapping.get(self.config.shapes[0], "circle") if value >= 0 else marker_mapping.get(self.config.shapes[1], "circle-open")
                    color = self.config.colors[i % len(self.config.colors)]
                    fig.add_trace(
                        go.Scatter(
                            x=[x[idx]],
                            y=[y[idx]],
                            mode="markers",
                            marker=dict(symbol=shape, color=color),
                            name=self.config.column_names.get(y_axis, y_axis) if idx == 0 else ""  # Use original column name for label
                        )
                    )
            else:
                shape = marker_mapping.get(self.config.shapes[i % len(self.config.shapes)], "circle")
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=y,
                        mode="markers",
                        marker=dict(symbol=shape, color=self.config.colors[i % len(self.config.colors)]),
                        name=self.config.column_names.get(y_axis, y_axis)
                    )
                )

            if self.config.use_uncertainties:
                sigup_column = f"{y_axis}_sigup"
                sigdown_column = f"{y_axis}_sigdown"
                if self.data_processor.has_column(sigup_column) and self.data_processor.has_column(sigdown_column):
                    fig.add_trace(
                        go.Scatter(
                            x=x,
                            y=y + self.data_processor.data[sigup_column],
                            mode="lines",
                            line=dict(color=self.config.colors[i % len(self.config.colors)], dash="dash"),
                            showlegend=False
                        )
                    )
                    fig.add_trace(
                        go.Scatter(
                            x=x,
                            y=y - self.data_processor.data[sigdown_column],
                            mode="lines",
                            line=dict(color=self.config.colors[i % len(self.config.colors)], dash="dash"),
                            showlegend=False
                        )
                    )

        fig.update_layout(
            title="Astronomy Data Graph",
            xaxis_title=self.config.x_axis_title,
            yaxis_title=self.config.y_axis_title,
            legend=dict(visible=self.config.legend),
        )
        if self.config.x_ticks:
            fig.update_xaxes(tickvals=range(int(self.config.x_min), int(self.config.x_max) + 1, int((self.config.x_max - self.config.x_min) / self.config.x_ticks)))
        fig.write_html(self.config.output_file)
        webbrowser.open(self.config.output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Astronomy Data Graph Generator")
    parser.add_argument("--file", required=False, help="Path to the input file")
    parser.add_argument("--delimiter", default=",", help="Delimiter used in the file (default: ',')")
    parser.add_argument("--x-axis", required=False, help="Column to use for the x-axis")
    parser.add_argument("--y-axes", required=False, help="Comma-separated list of columns to use for the y-axis")
    parser.add_argument("--x-min", type=float, help="Minimum value for the x-axis")
    parser.add_argument("--x-max", type=float, help="Maximum value for the x-axis")
    parser.add_argument("--y-min", type=float, help="Minimum value for the y-axis")
    parser.add_argument("--y-max", type=float, help="Maximum value for the y-axis")
    parser.add_argument("--colors", help="Comma-separated list of colors for the graph")
    parser.add_argument("--shapes", help="Comma-separated list of shapes for the graph")
    parser.add_argument("--legend", action="store_true", help="Include a legend in the graph")
    parser.add_argument("--dpi", type=int, default=300, help="DPI for the output graph")
    parser.add_argument("--font-size", type=int, default=12, help="Font size for labels and legends")
    parser.add_argument("--output-file", required=False, help="Path to save the output graph")
    parser.add_argument("--output-format", default="png", help="Output file format (default: 'png')")
    parser.add_argument("--interactive", action="store_true", help="Generate an interactive graph")
    parser.add_argument("--use-uncertainties", action="store_true", help="Include uncertainties in the graph")
    parser.add_argument("--style", default="petroff10", help="Style for the graph (default: 'petroff10')")
    parser.add_argument("--x-ticks", type=int, help="Number of tick marks on the x-axis")
    parser.add_argument(
        "--column-names",
        nargs="+",
        help="Pairs of original and new column names (e.g., OriginalName=NewName)"
    )
    parser.add_argument("--import-config", help="Path to a YAML configuration file")
    parser.add_argument("--export-config", help="Path to save the configuration as a YAML file")
    parser.add_argument("--x-axis-title", help="Title for the x-axis")
    parser.add_argument("--y-axis-title", help="Title for the y-axis")

    args = parser.parse_args()

    if args.import_config:
        config = GraphConfig(import_config=args.import_config)
    else:
        config = GraphConfig(args=args)

    if args.export_config:
        config.export_to_yaml(args.export_config)

    if not args.file and not args.import_config:
        raise ValueError("Input file must be specified when not exporting configuration.")
    
    data_processor = DataProcessor(args.file, config.delimiter)
    
    # Debugging: Print column names
    print("Data columns:", data_processor.data.columns)
    print("Configured y-axes:", config.y_axes)
    
    graph = Graph(config, data_processor)
    graph.render()