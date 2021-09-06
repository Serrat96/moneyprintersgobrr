

cols_filler = {
            #### LEFT
            # Level 1
            0 : {
                # Level 2
                "title" : "CPI & GDP",        # Add this to to_plot dict -> update double_ended function
                # Level 3
                "to_plot" : {"dfs": [cpi_usa, gdp_usa],
                           "legends": ["CPI", "GDP"],
                           "secondary_ys": [False, True],
                           "names": ["CPI", "GDP"]},
                "note" : "CPI: Index 1982-1984=100",
                # Level 3
                "plot_params" : {
                    "x_annot" : 1,
                    "y_annot" : -0.12,
                    "x_legend" : 0,
                    "y_legend" : 0
                },
            },

            #### RIGHT
            1 : {
                # Level 2
                "title" : "Test",        # Add this to to_plot dict -> update double_ended function
                # Level 3
                "to_plot" : {"dfs": [cpi_usa, gdp_usa],
                           "legends": ["CPI", "GDP"],
                           "secondary_ys": [False, True],
                           "names": ["CPI", "GDP"]},
                "note" : "CPI: Index 1982-1984=100",
                # Level 3
                "plot_params" : {
                    "x_annot" : 1,
                    "y_annot" : -0.12,
                    "x_legend" : 0,
                    "y_legend" : 0
                }
            }
        }