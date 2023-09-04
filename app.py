from shiny import App, Inputs, Outputs, Session, render, ui, reactive
from yahooquery import Ticker
from datetime import date, timedelta
from core_funcs import extra_params, stock_returns, get_params, portfolios, get_symbols, portfolios_plot

today = date.today()

app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.row(
                ui.column(
                4,
                ui.input_select(id = "interval", label = "Interval",  choices = extra_params()["intervals"][-5:], width= "130px"), 
                ui.input_date(id = "start", label = "Start", max = today, width = "130px"),
                ui.output_ui("end")
            ),
            ui.column(
                4,
                ui.input_selectize("tickers", "Choose Ticker", choices = get_symbols(), multiple=True)
                
            ),
            ),
            ui.input_slider("samples", "Number of Samples", min=1000, max=10000, value=5000, step = 200),
            ui.input_action_button("calculate", "Calculate")
        ),
        ui.panel_main(
            ui.output_plot("plot"),
            ui.output_text_verbatim("txt"),
        ),
    ),
)

def server(input: Inputs, output: Outputs, session: Session):
    
    @reactive.Calc
    @reactive.event(input.calculate)
    def main_df():
        #change later
        dfs = Ticker(input.tickers(), asynchronous = True).history(interval=input.interval(), start = input.start(), end = "2021-01-07")
        #the lowest date we can 
        lower_bound = max([i for i in dfs.reset_index().groupby("symbol")["date"].min()])
        
        return dfs
    
    @output
    @render.ui
    @reactive.Calc
    def end():
        return ui.TagList(
            ui.input_date(id = "end", label = "End", min = input.start(), value = input.start(), max = min([today, input.start() + timedelta(weeks = 300)]), width = "130px")
        )
    
    @reactive.Calc
    def portfolio_vis_data():
        df = stock_returns(main_df())
        params = get_params(df)
        all_portfolios = portfolios(len(input.tickers()), params, stock_returns(main_df()), input.samples())
        
        return all_portfolios
    
    @output
    @render.plot
    @reactive.event(input.calculate)
    def plot():
        return portfolios_plot(*portfolio_vis_data())
    

app = App(app_ui, server)


#document plt change
#limit to 1 month, no need for select input
#upload stock data to server
#filter ticker name from start and end date range
#pull stock data from from server
#add boxes of value data