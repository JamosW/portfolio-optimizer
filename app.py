from shiny import App, Inputs, Outputs, Session, render, ui, reactive
import shiny.experimental as x
from datetime import date, timedelta
from core_funcs import np, min_date_dfs, stock_returns, get_params, portfolios, portfolios_plot, get_tickers
from shinyswatch import theme
from re import sub, split
from htmltools import css

today = date.today()
    
def card(title, values, ispercent):
    
    cleaned_lists = sub(r'[\[\]\(\)]|[a-z]', '', str(values))
    percentages = [str(np.round((np.float16(i) * 100), 2)) + "%" for i in split(' ', cleaned_lists) if i != '']
    non_percent = sub(r'[\[\]]', '', str(values))
    
    toDisplay = []
    if(ispercent):
        toDisplay.append(percentages)
    else:
        toDisplay.append(non_percent)
    
    return(
        x.ui.card(
            x.ui.card_title(title,  style=css(font_weight="bold", color="#002147")),
            x.ui.card_body(
                ui.div(ui.h2(sub(r'[\[\]\(\),\']', '',str(toDisplay))))
            ),
            height = '130px'
        )
    )
    

app_ui = ui.page_fluid(
    theme.cosmo(),
    #ui.panel_conditional("input.calculate", x.ui.layout_column_wrap(1 / 4, *[value_box(title) for title in ["Optimal Weights", "Sharpe ratio", "three", "four"]])),
    ui.output_ui("value_boxes"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.row(
                ui.column(
                4, 
                #70 days, slightly bigger than 2 months, the minimum needed for there to be any variance (as were using average monthly returns)
                ui.input_date(id = "start", label = "Start", max = today - timedelta(days=96), value = today - timedelta(days=96), width = "130px"),
                ui.input_date(id = "end", label = "End", max = today, value = today, min = today, width = "130px")
            ),
            ui.column(
                4,
                ui.input_text("tickers", "Choose Ticker", placeholder= "AAPL")
                
            ),
            ),
            ui.input_slider("samples", "Number of Samples", min=1000, max=20000, value=5000, step = 200),
            ui.input_action_button("calculate", "Calculate"),
                        ui.output_text("txter")
        ),
        ui.panel_main(
            ui.output_plot("plot"),
            ui.output_text_verbatim("txt"),
        ),
    ),
)

def server(input: Inputs, output: Outputs, session: Session):
        
        #validation method, if all checks, we return an event, else return a modal message
        @reactive.Calc
        @reactive.event(input.calculate)
        def validate():
            if(len(input.tickers()) > 1):
                return 1
            else:
                m = ui.modal(
                "The ticker length must be greater than 1.",
                easy_close=True,
                footer=None,
            )
        
                return ui.modal_show(m)
        
        #update the selectize order, to match the weights values, np.unique sorts names
        @reactive.Effect
        @reactive.event(validate)
        def _():
            a = list(input.tickers())
            a.sort()
            ui.update_selectize(
                "tickers",
                selected = a
            )
            
        
        @reactive.Calc
        def main_df():
            lower_bound, dfs = min_date_dfs(symbols = input.tickers(), start = input.start(), end = input.end())

            return dfs
        
        
        @reactive.Calc
        def portfolio_vis_data():
            df = stock_returns(main_df())
            params = get_params(df)
            all_portfolios = portfolios(len(input.tickers()), params, df, input.samples())
            
            return all_portfolios
        
        @output
        @render.ui
        @reactive.event(validate)
        def value_boxes():
            
            portfolio_data = portfolio_vis_data()
            optimal_weights, min_variance_weights = [np.round(i, 3) for i in [portfolio_data[3], portfolio_data[4]]]
            
            return ui.TagList(
                x.ui.layout_column_wrap(1 / 4, *[card(title, val, perc) for title,val,perc in zip(["Optimal Weights", "Highest Sharpe Ratio", "Minimum Variance Portfolio", "Minimum Variance"], 
                                                                                        [optimal_weights,
                                                                                        np.float16(np.round(portfolio_data[2], 3)),
                                                                                        min_variance_weights, portfolio_data[5]],
                                                                                        [True] * 3 + [False]
                                                                                        )])
            )
        
        @output
        @render.plot
        @reactive.event(validate)
        def plot():
            return portfolios_plot(*portfolio_vis_data()[0:2])
        
        
        @output
        @render.text
        @reactive.event(validate)
        def txter():
            lower_bound, dfs = min_date_dfs(symbols = input.tickers(), start = input.start(), end = input.end())
            
            #conditional message if start date is lower than the lower bound
            if input.start() < lower_bound - timedelta(days = 30):
                return f"Lowest date all {len(input.tickers())} tickers share in common is {lower_bound}"
            else:
                return None

app = App(app_ui, server)

#document plt change