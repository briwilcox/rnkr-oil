import numpy
import requests
import Quandl
import datetime

from pyrnkr.application import App
from pyrnkr.widgets import Line
from pyrnkr.formula import Trace

def extract_date_index(ts, format='%Y-%m-%d'):
    return [x.strftime(format) for x in ts.index.tolist()]

class oil(App):
    # This must be consistent with config.json
    required_parameters = []
    title = 'Overview of Oil'  # Appears on top of your application page
    subtitle = 'Supply, Consumption, and Prices of Oil Products'  # Subtitle to the above

    # Production Chart Primary
    MultiLineMultiTypeRigCount = "BKRHUGHES/RIGS_BY_BASIN_TOTAL_US_RIG_COUNT"  # Example data
    SingleLineRigTotal = "BKRHUGHES/RIGS_BY_STATE_TOTALUS_TOTAL"

    # Price Charts
    BRENT = "EIA/PET_RBRTE_D"
    WTI = "EIA/PET_RWTC_D"

    # Oil Secondary
    MiningUSOilProduction = "FRED/IPG211111CN"
    ImportsEndUseCrude = "FRED/IR10000"
    OilAndGasWells = "FRED/IPN213111N"
    PrivateFixedInvestmentWellsExploration = "FRED/E318RC1Q027SBEA"

    # Quandl Token
    TOKEN = ''  # YOUR TOKEN HERE

    def __init__(self, *args, **kwargs):
        super(oil, self).__init__(*args, **kwargs)

    def get_trace(self, symbol):
        """Get trace for a symbol"""
        data = Quandl.get(symbol, authtoken=self.TOKEN)
        if data.empty:
            raise Exception('could not load series from data source')  # If you'd like to handle network
            # errors or retry do it here

        datay = data[data.columns[0]].tolist()  # Data can be manipulated in node.js / python (pandas or numpy)
        x = extract_date_index(data)

        if len(datay) != len(x):
            raise Exception('x and y length do not match')  # Sanity Check, trust but verify data feeds

        tr = Trace(
            x = x,
            y = datay,
            extra = {
                'name': symbol
            }
        )

        return tr  # This returns the data to be plotted

    def execute(self, parameters):
        # Create object to plot
        res = {
            self.SingleLineRigTotal: {
                'title': 'Total U.S. Rig Counts',  # Title of individual plot
                'subtitle': 'Total U.S. Rotary Rig Counts',  # Subtitle of individual plot
                'dimension': 'col-md-12',  # Bootstrap column dimensions
            },
            self.BRENT: {
                'title': 'Brent Crude',
                'subtitle': 'USD Price of Brent Crude Oil',
                'dimension': 'col-md-6',
            },
            self.WTI: {
                'title': 'WTI Crude',
                'subtitle': 'USD Price of WTI Crude Oil',
                'dimension': 'col-md-6',
            },
            self.MiningUSOilProduction: {
                'title': 'US Oil Production',
                'subtitle': 'US Oil Production (Indexed 2012 = 100)',
                'dimension': 'col-md-6',
            },
            self.ImportsEndUseCrude: {
                'title': 'US Crude Imports',
                'subtitle': 'Crude Oil Imports (Indexed 2000 = 100) (Not Seasonally Adjusted)',
                'dimension': 'col-md-6',
            },
            self.OilAndGasWells: {
                'title': 'US Oil and Gas Wells',
                'subtitle': 'Drilling oil and gas wells',
                'dimension': 'col-md-6',
            },
            self.PrivateFixedInvestmentWellsExploration: {
                'title': 'Fixed Investment Wells and Exploration',
                'subtitle': '(In Billions USD) (Quarterly Seasonally Adjusted)',
                'dimension': 'col-md-6',
            }
        }

        # Because we are using only RNKR line plots iterate through the above create line widgets of variable size
        for k, v in res.iteritems():
            ts = self.get_trace(k)
            res[k]['widget'] = Line(
                title=v['title'],
                subtitle=v['subtitle'],
                dimension=v['dimension'],
                traces=[ts]
            )

        # Render the layout object, primary array is app page, secondary arrays are each bootstrap column
        # Styling is dictated here and in the bootstrap column dimensions above
        layout = self.render([
            [res[self.SingleLineRigTotal]['widget']],
            [
                res[self.WTI]['widget'],
                res[self.BRENT]['widget']
            ],
            [
                res[self.MiningUSOilProduction]['widget'],
                res[self.ImportsEndUseCrude]['widget']
            ],
            [
                res[self.OilAndGasWells]['widget'],
                res[self.PrivateFixedInvestmentWellsExploration]['widget']
            ],
        ])

        return layout, None


def handler(event, context):
    """
    AWS Lambda Handler
    Inputs depend on your config.json
    """
    res, err = oil().run(event)
    if err:
        raise Exception(err)

    return res


# Left for convenience / example of debugging aws lambdas prior to upload
#import json
#print json.dumps(handler({}, {}))