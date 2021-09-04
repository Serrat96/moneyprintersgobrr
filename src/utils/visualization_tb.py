import matplotlib.pyplot as plt

from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px

import sys, os

# Helpers
abspath = os.path.abspath
dirname = os.path.dirname
sep = os.sep

# Path modification
current_folder = dirname(abspath(__file__))
for i in range(1): current_folder = dirname(abspath(current_folder))
sys.path.append(current_folder)

# In-house functions
import utils.mining_data_tb as md

# Objects
processor = md.processor

##################################################### FUNCTIONS #####################################################
#####
class st_plotter:
    @staticmethod
    def line_plotter(dict_, start_date, end_date, note='', x_annot=0, y_annot=0, x_legend=0, y_legend=1, title="", tickformat="", palette=False):
        dfs, legends, secondary_ys, names = dict_["dfs"], dict_["legends"], dict_["secondary_ys"], dict_["names"]
        # General settings
        start_date_str = str(start_date)
        end_date_str = str(end_date)
        palette_ = px.colors.qualitative.Plotly
        if palette:
            palette_ = palette

        fig = make_subplots()
        
        if any(secondary_ys):
            fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Iterate over
        for ind, df in enumerate(dfs):
            filtered_df = processor.filter_between_dates(df, start_date_str, end_date_str)
            fig.add_trace(go.Scatter(x=filtered_df.index, y=filtered_df.iloc[:, 0], name=legends[ind],
                                     line=dict(color=palette_[ind])), secondary_y=secondary_ys[ind])
        
        # Layout
        fig.update_layout(title=title, xaxis_rangeslider_visible=False, title_font_size=30,
                          legend=dict(bgcolor='rgba(0,0,0,0)',
                x=x_legend,
                y=y_legend,
                font=dict(
                    size=10)))

        # Axes
        fig.update_xaxes(rangeslider_thickness=0.1, showgrid=False)
        fig.update_yaxes(title_text=names[0], tickformat=tickformat, secondary_y=False, showgrid=False, zeroline=False)
        if len(names) > 1:
            fig.update_yaxes(title_text=names[1], tickformat=tickformat, secondary_y=True, showgrid=False, zeroline=False)

        if note != '':
            fig.add_annotation(
                showarrow=False,
                text=note,
                font=dict(size=10),
                xref='x domain',
                x=x_annot,
                yref='y domain',
                y=y_annot
            )

        return fig


#####
class notebook_plotter:
    '''
    Class to perform some exploratory analysis on the data
    '''

    ####
    def __n_rows(self, df, n_columns):
        '''
        It calculates the number of rows (for the axes) depending on the number of variables to plot and the columns we want for the figure.
        args:
        n_columns: number of columns
        '''
        columns = list(df.columns)

        if len(columns) % n_columns == 0:
            axes_rows = len(columns) // n_columns
        else:
            axes_rows = (len(columns) // n_columns) + 1

        return axes_rows
        
    ####
    def multi_axes(self, df, n_columns, figsize = (12, 12)):
        '''
        It creates a plot with multiple rows and columns. It returns a figure.
        n_columns: number of columns for the row
        kind: ("strip", "dist", "box")
        figsize: size of the figure
        '''
        # Calculating the number of rows from number of columns and variables to plot
        n_rows_ = self.__n_rows(df, n_columns)

        # Creating the figure and as many axes as needed
        fig, axes = plt.subplots(n_rows_, n_columns, figsize = figsize)
        # To keep the count of the plotted variables
        count = 0

        # Some transformation, because with only one row, the shape is: (2,)
        axes_col = axes.shape[0]
        try:
            axes_row = axes.shape[1]
        except:
            axes_row = 1

        # Loop through rows
        for row in range(axes_col):
            # Loop through columns
            for column in range(axes_row):
                # Data to plot
                x = df.iloc[:, count]
                labels = x.unique()

                # Plot
                #sns.countplot(x = x, data = df, ax = axes[row][column])
                axes[row][column].plot(x)

                # Some extras
                axes[row][column].set(xlabel = "")
                axes[row][column].set_title(x.name)

                # To stop plotting
                if (count + 1) < df.shape[1]:
                    count += 1
                else:
                    break

        plt.tight_layout()
        
        return fig