import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from pandas.api.types import is_numeric_dtype # Import added
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk
)

class CsvVisualizerApp(tk.Tk):
    """
    A desktop application for loading, processing, and visualizing CSV data
    using Tkinter, Pandas, and Matplotlib.
    """

    def __init__(self):
        super().__init__()
        self.title("CSV Data Processor and Visualizer")
        self.geometry("1300x800")
        
        # Set a modern theme
        self.style = ttk.Style(self)
        self.style.theme_use('clam') # 'clam', 'alt', 'default', 'classic'

        # Data placeholders
        self.df = None
        self.figure = None
        self.canvas_widget = None
        self.toolbar = None
        self.filename = ""

        # Create the main layout
        self._create_widgets()
        self.update_status("Ready. Please load a CSV file.")

    def _create_widgets(self):
        """Creates and lays out all the main GUI components."""
        
        # Main container frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 1. Left Control Panel
        control_panel = self._create_control_panel(main_frame)
        control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=5)

        # 2. Right Main Display Panel (Notebook)
        self.notebook = self._create_display_panel(main_frame)
        self.notebook.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=5)
        
        # 3. Bottom Status Bar
        self.status_bar = ttk.Label(self, text="", relief=tk.SUNKEN, anchor=tk.W, padding=5)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _create_control_panel(self, parent):
        """Creates the left-side panel with all user controls."""
        frame = ttk.LabelFrame(parent, text="Controls", width=300)
        frame.pack_propagate(False) # Prevent frame from shrinking to fit content

        # A. Load CSV Button
        ttk.Button(
            frame, 
            text="Load CSV File", 
            command=self.load_csv
        ).pack(fill=tk.X, pady=10, padx=10)

        # B. File Info Label
        self.file_info_label = ttk.Label(
            frame, 
            text="No file loaded.", 
            wraplength=280, 
            justify=tk.LEFT
        )
        self.file_info_label.pack(fill=tk.X, pady=5, padx=10)
        
        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=10, padx=10)

        # C. Chart Type
        ttk.Label(frame, text="Select Chart Type:").pack(anchor=tk.W, padx=10)
        self.chart_type_var = tk.StringVar()
        self.chart_type_combo = ttk.Combobox(
            frame, 
            textvariable=self.chart_type_var,
            values=["Bar Chart", "Line Chart", "Scatter Plot", "Histogram"],
            state='disabled'
        )
        self.chart_type_combo.pack(fill=tk.X, pady=5, padx=10)
        self.chart_type_combo.bind('<<ComboboxSelected>>', self.on_chart_type_select)

        # D. X-Axis
        ttk.Label(frame, text="Select X-Axis:").pack(anchor=tk.W, padx=10)
        self.x_axis_var = tk.StringVar()
        self.x_axis_combo = ttk.Combobox(
            frame, 
            textvariable=self.x_axis_var, 
            state='disabled'
        )
        self.x_axis_combo.pack(fill=tk.X, pady=5, padx=10)

        # E. Y-Axis
        ttk.Label(frame, text="Select Y-Axis:").pack(anchor=tk.W, padx=10)
        self.y_axis_var = tk.StringVar()
        self.y_axis_combo = ttk.Combobox(
            frame, 
            textvariable=self.y_axis_var, 
            state='disabled'
        )
        self.y_axis_combo.pack(fill=tk.X, pady=5, padx=10)
        
        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=10, padx=10)

        # F. Generate Plot Button
        self.generate_plot_button = ttk.Button(
            frame, 
            text="Generate Plot", 
            command=self.generate_plot, 
            state='disabled'
        )
        self.generate_plot_button.pack(fill=tk.X, pady=5, padx=10)

        # G. Export Plot Button
        self.export_plot_button = ttk.Button(
            frame, 
            text="Export Plot", 
            command=self.export_plot, 
            state='disabled'
        )
        self.export_plot_button.pack(fill=tk.X, pady=5, padx=10)

        return frame

    def _create_display_panel(self, parent):
        """Creates the right-side notebook with tabs for data, stats, and plot."""
        notebook = ttk.Notebook(parent)
        
        # Tab 1: Data Table
        tab_data = ttk.Frame(notebook)
        notebook.add(tab_data, text="Data Table")
        self._create_data_tab(tab_data)

        # Tab 2: Statistics
        tab_stats = ttk.Frame(notebook)
        notebook.add(tab_stats, text="Statistics")
        self._create_stats_tab(tab_stats)

        # Tab 3: Plot
        self.tab_plot = ttk.Frame(notebook)
        notebook.add(self.tab_plot, text="Plot")
        self._create_plot_tab(self.tab_plot)

        return notebook

    def _create_data_tab(self, parent):
        """Creates the scrollable Treeview widget for displaying the DataFrame."""
        data_frame = ttk.Frame(parent)
        data_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        v_scroll = ttk.Scrollbar(data_frame, orient=tk.VERTICAL)
        h_scroll = ttk.Scrollbar(data_frame, orient=tk.HORIZONTAL)

        # Treeview
        self.tree = ttk.Treeview(
            data_frame, 
            yscrollcommand=v_scroll.set, 
            xscrollcommand=h_scroll.set,
            show='headings' # Don't show the default first column
        )

        v_scroll.config(command=self.tree.yview)
        h_scroll.config(command=self.tree.xview)

        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def _create_stats_tab(self, parent):
        """Creates the text widget for displaying descriptive statistics."""
        self.stats_text = tk.Text(parent, wrap=tk.WORD, height=10, state='disabled', font=('Courier', 10))
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def _create_plot_tab(self, parent):
        """Creates the frame that will hold the Matplotlib canvas."""
        # This frame acts as a container. The canvas is added/removed in generate_plot()
        self.plot_frame = ttk.Frame(parent)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)
        # Add a label that will be destroyed when a plot is generated
        self.plot_placeholder_label = ttk.Label(self.plot_frame, text="Generate a plot using the controls on the left.", anchor=tk.CENTER)
        self.plot_placeholder_label.pack(pady=50, fill=tk.BOTH, expand=True)

    # --- Core Functionality Methods ---

    def load_csv(self):
        """Opens a file dialog to load a CSV file into a Pandas DataFrame."""
        file_path = filedialog.askopenfilename(
            title="Select a CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            return # User cancelled

        try:
            self.df = pd.read_csv(file_path)
            self.filename = file_path.split('/')[-1]
            self.update_status(f"Loaded '{self.filename}' successfully.")
            
            # Update GUI components
            self._update_data_table()
            self._update_stats_tab()
            self._update_control_panel_for_new_data()
            
            # Switch to the data tab
            self.notebook.select(0)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")
            self.update_status(f"Error loading file.")

    def _update_data_table(self):
        """Populates the Treeview widget with data from the DataFrame."""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if self.df is None:
            return

        # Set columns
        self.tree["columns"] = list(self.df.columns)
        for col in self.df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.W)
            
        # Insert data (limit to 1000 rows for performance)
        df_head = self.df.head(1000)
        for index, row in df_head.iterrows():
            self.tree.insert("", tk.END, values=list(row))
        
        if len(self.df) > 1000:
             self.update_status(f"Loaded '{self.filename}'. Data table is showing the first 1000 rows.")
             # Add a visual indicator of truncation
             self.tree.insert("", tk.END, values=["..." for _ in self.df.columns])


    def _update_stats_tab(self):
        """Calculates and displays descriptive statistics."""
        if self.df is None:
            return
        
        try:
            # Get stats only for numeric columns
            numeric_df = self.df.select_dtypes(include=['number'])
            if numeric_df.empty:
                stats = "No numeric data found for statistics."
            else:
                stats = numeric_df.describe().to_string()
        except Exception as e:
            stats = f"Error generating statistics: {e}"

        self.stats_text.config(state='normal')
        self.stats_text.delete('1.0', tk.END)
        self.stats_text.insert('1.0', stats)
        self.stats_text.config(state='disabled')

    def _update_control_panel_for_new_data(self):
        """Updates control panel elements after new data is loaded."""
        if self.df is None:
            return
            
        # Update file info label
        rows, cols = self.df.shape
        self.file_info_label.config(text=f"File: {self.filename}\nRows: {rows}, Columns: {cols}")

        # Update comboboxes
        column_names = list(self.df.columns)
        self.chart_type_combo.config(state='readonly')
        self.x_axis_combo.config(values=column_names, state='readonly')
        self.y_axis_combo.config(values=column_names, state='readonly')
        
        # Enable buttons
        self.generate_plot_button.config(state='normal')
        
        # Reset selections
        self.x_axis_var.set('')
        self.y_axis_var.set('')
        self.chart_type_var.set('')
        self.y_axis_combo.config(state='disabled') # Disabled until chart type is chosen

    def on_chart_type_select(self, event=None):
        """Enables or disables the Y-axis combobox based on chart type."""
        chart_type = self.chart_type_var.get()
        if chart_type == "Histogram":
            # The line below was incorrect and has been removed.
            # ttk.Label(self.plot_frame, text="Generate a plot using the controls on the left.").pack(pady=50)
            self.y_axis_combo.config(state='disabled')
            self.y_axis_var.set('') # Clear selection
        else:
            self.y_axis_combo.config(state='readonly')

    def generate_plot(self):
        """Generates and embeds the selected Matplotlib plot."""
        chart_type = self.chart_type_var.get()
        x_col = self.x_axis_var.get()
        y_col = self.y_axis_var.get()

        # --- Input Validation ---
        if not chart_type or not x_col:
            self.update_status("Error: Chart Type and X-Axis must be selected.")
            return
        
        if chart_type != "Histogram" and not y_col:
            self.update_status("Error: Y-Axis must be selected for this chart type.")
            return
        
        if self.df is None:
            self.update_status("Error: No data loaded.")
            return
            
        # --- Data for plotting ---
        plot_df = self.df.copy()

        # --- Input Validation (moved before plot creation) ---
        try:
            if chart_type == "Bar Chart":
                if not is_numeric_dtype(plot_df[y_col]):
                    raise ValueError("Bar charts require a numeric Y-axis.")
            
            elif chart_type == "Line Chart":
                if not is_numeric_dtype(plot_df[y_col]):
                    raise ValueError("Line charts require a numeric Y-axis.")
                # Sort by x-axis if it's numeric for a coherent line
                if is_numeric_dtype(plot_df[x_col]):
                    plot_df = plot_df.sort_values(by=x_col)

            elif chart_type == "Scatter Plot":
                if not is_numeric_dtype(plot_df[x_col]) or \
                   not is_numeric_dtype(plot_df[y_col]):
                    raise ValueError("Scatter plots require numeric X and Y axes.")

            elif chart_type == "Histogram":
                if not is_numeric_dtype(plot_df[x_col]):
                    raise ValueError("Histograms require a numeric X-axis.")
        
        except KeyError as e:
            messagebox.showerror("Plotting Error", f"Column not found: {e}. Please check your selections.")
            self.update_status(f"Error plotting: Column {e} not found.")
            return
        except ValueError as e:
            messagebox.showerror("Plotting Error", f"Incompatible data: {e}")
            self.update_status(f"Error plotting: {e}")
            return
        except Exception as e:
            messagebox.showerror("Plotting Error", f"An unexpected error occurred during validation: {e}")
            self.update_status(f"Error plotting: {e}")
            return


        # --- Clear previous plot ---
        # Destroy canvas and toolbar explicitly if they exist
        if self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()
            self.canvas_widget = None
        if self.toolbar:
            self.toolbar.destroy()
            self.toolbar = None
        
        # Destroy placeholder label if it exists
        if self.plot_placeholder_label:
            self.plot_placeholder_label.destroy()
            self.plot_placeholder_label = None
            
        # Fallback clear all children
        for widget in self.plot_frame.winfo_children():
            widget.destroy() 
        
        if self.figure:
            plt.close(self.figure) # Close the figure to free memory

        # --- Create new figure ---
        try:
            self.figure, ax = plt.subplots(figsize=(8, 6))

            # --- Plotting logic ---
            if chart_type == "Bar Chart":
                plot_df.plot(kind='bar', x=x_col, y=y_col, ax=ax, legend=True)
                ax.set_title(f"Bar Chart: {y_col} vs {x_col}")
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)

            elif chart_type == "Line Chart":
                plot_df.plot(kind='line', x=x_col, y=y_col, ax=ax, legend=True, marker='o')
                ax.set_title(f"Line Chart: {y_col} vs {x_col}")
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)

            elif chart_type == "Scatter Plot":
                plot_df.plot(kind='scatter', x=x_col, y=y_col, ax=ax)
                ax.set_title(f"Scatter Plot: {y_col} vs {x_col}")
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)

            elif chart_type == "Histogram":
                plot_df[x_col].plot(kind='hist', ax=ax, bins=30, edgecolor='black')
                ax.set_title(f"Histogram of {x_col}")
                ax.set_xlabel(x_col)
                ax.set_ylabel("Frequency")

            ax.grid(True, linestyle='--', alpha=0.6)
            self.figure.tight_layout() # Adjust plot to fit

            # --- Embed the plot ---
            self.canvas_widget = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
            self.canvas_widget.draw()
            
            # Add new toolbar
            self.toolbar = NavigationToolbar2Tk(self.canvas_widget, self.plot_frame, pack_toolbar=False)
            self.toolbar.update()
            self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
            
            # Pack the canvas *after* the toolbar
            self.canvas_widget.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            self.update_status(f"Generated {chart_type} successfully.")
            self.export_plot_button.config(state='normal')
            
            # Switch to the plot tab
            self.notebook.select(self.tab_plot)

        except Exception as e:
            messagebox.showerror("Plotting Error", f"Failed to generate plot: {e}")
            self.update_status(f"Error plotting: {e}")
            if self.figure:
                plt.close(self.figure) # Clean up the failed figure
            self.figure = None
            # Re-create placeholder label on error
            self.plot_placeholder_label = ttk.Label(self.plot_frame, text=f"Plot generation failed.\nError: {e}", anchor=tk.CENTER, justify=tk.CENTER)
            self.plot_placeholder_label.pack(pady=50, fill=tk.BOTH, expand=True)

    def export_plot(self):
        """Opens a 'save as' dialog to export the current plot as an image."""
        if not self.figure:
            self.update_status("Error: No plot to export.")
            messagebox.showwarning("Export Error", "There is no plot to export. Please generate a plot first.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save Plot As",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("PDF File", "*.pdf")],
            defaultextension=".png"
        )
        
        if not file_path:
            return # User cancelled

        try:
            self.figure.savefig(file_path, dpi=300, bbox_inches='tight')
            self.update_status(f"Plot saved to '{file_path.split('/')[-1]}'")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save plot: {e}")
            self.update_status("Error saving plot.")

    def update_status(self, message):
        """Updates the text in the bottom status bar."""
        self.status_bar.config(text=message)


if __name__ == "__main__":
    app = CsvVisualizerApp()
    app.mainloop()


