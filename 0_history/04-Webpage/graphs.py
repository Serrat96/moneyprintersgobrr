import functions as ft
import folder_tb as fo

import os

# Helpers
abspath = os.path.abspath
dirname = os.path.dirname
sep = os.sep

# Columna1, grafico 1 : incremento masas monetarias anual e incremento IPC anual
data_path = fo.path_to_folder(1, "02-Data")

m2_usa = ft.read_data(data_path + 'M2' + sep + 'm2.parquet')
cpi_usa = ft.read_data(data_path + 'CPI' + sep + 'cpi.parquet')
m2_cpi_graph = ft.two_plots(m2_usa, cpi_usa,  legend_graph_one='M2', legend_graph_two='CPI',
              principal_title='M2 and CPI real values', name_graph_one='M2 USA in billions', name_graph_two='CPI USA',
              tickformat='')

# Columna 2, gráfico 1: % incremento masas monetarias anual y % incremento IPC anual

m2_usa_percentage = m2_usa.pct_change(12).dropna()
cpi_usa_percentage = cpi_usa.pct_change(12).dropna()
m2_cpi_percentage_graph = ft.two_plots(m2_usa_percentage, cpi_usa_percentage, legend_graph_one='M2',
                        legend_graph_two='CPI', principal_title='M2 and CPI anual change', name_graph_one='M2',
                        name_graph_two='CPI')
# Columna 3, gráfico 1: Correlación entre % incremento masas monetarias anual y % incremento IPC anual

correlation = float(ft.two_variables_correlation(m2_usa, cpi_usa).iloc[1,0])
annual_change_correlation = float(ft.two_variables_correlation(m2_usa.pct_change(12).dropna(), cpi_usa.pct_change(24).dropna()).iloc[1,0])




