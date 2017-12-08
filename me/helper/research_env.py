import osimport pandas as pdimport refrom zipline.data.bundles.core import loadfrom zipline.data.data_portal import DataPortalfrom zipline.finance.trading import TradingEnvironmentfrom zipline.pipeline.data import USEquityPricingfrom zipline.pipeline.engine import (    SimplePipelineEngine,)from zipline.pipeline.loaders import USEquityPricingLoaderfrom zipline.utils.calendars import get_calendarDEFAULT_CAPITAL_BASE = 1e5import ziplinefrom zipline.data.bundles import registerfrom zipline.data.bundles.viadb import viadbpd.set_option('display.width', 800)def research_env_get_instance(bundle='my-db-bundle', calendar='SHSZ', exchange_tz="Asia/Shanghai"):    ############################################# bundle #############################################    equities1 = {}    register(        bundle,  # name this whatever you like        viadb(equities1),        calendar=calendar    )    bundle = 'my-db-bundle'    bundle_timestamp = pd.Timestamp.utcnow()    environ = os.environ    bundle_data = load(        bundle,        environ,        bundle_timestamp,    )    prefix, connstr = re.split(        r'sqlite:///',        str(bundle_data.asset_finder.engine.url),        maxsplit=1,    )    # print prefix, connstr    if prefix:        raise ValueError(            "invalid url %r, must begin with 'sqlite:///'" %            str(bundle_data.asset_finder.engine.url),        )    ############################################# trading_environment #############################################    trading_calendar = get_calendar(calendar)    trading_environment = TradingEnvironment(bm_symbol=None,                                             exchange_tz=exchange_tz,                                             trading_calendar=trading_calendar,                                             asset_db_path=connstr)    ############################################# choose_loader #############################################    pipeline_loader = USEquityPricingLoader(        bundle_data.equity_daily_bar_reader,        bundle_data.adjustment_reader,    )    def choose_loader(column):        if column in USEquityPricing.columns:            return pipeline_loader        raise ValueError(            "No PipelineLoader registered for column %s." % column        )    your_engine = SimplePipelineEngine(get_loader=choose_loader, calendar=trading_calendar.all_sessions,                                       asset_finder=trading_environment.asset_finder)    # your_engine._finder    first_trading_day = \        bundle_data.equity_minute_bar_reader.first_trading_day    data = DataPortal(        trading_environment.asset_finder, get_calendar(calendar),        first_trading_day=first_trading_day,        equity_minute_reader=bundle_data.equity_minute_bar_reader,        equity_daily_reader=bundle_data.equity_daily_bar_reader,        adjustment_reader=bundle_data.adjustment_reader,    )    return your_engine, data,class Research(object):    def __init__(self, bundle='my-db-bundle', calendar='SHSZ', exchange_tz="Asia/Shanghai"):        self.__bundle_name__ = bundle        self.__calendar_name__ = calendar        self.__exchange_tz__ = exchange_tz        ############################################# bundle #############################################        equities1 = {}        register(            bundle,  # name this whatever you like            viadb(equities1),            calendar=calendar        )        bundle = 'my-db-bundle'        bundle_timestamp = pd.Timestamp.utcnow()        environ = os.environ        bundle_data = load(            bundle,            environ,            bundle_timestamp,        )        prefix, connstr = re.split(            r'sqlite:///',            str(bundle_data.asset_finder.engine.url),            maxsplit=1,        )        # print prefix, connstr        if prefix:            raise ValueError(                "invalid url %r, must begin with 'sqlite:///'" %                str(bundle_data.asset_finder.engine.url),            )        self.__bundle__ = bundle_data        ############################################# trading_environment #############################################        trading_calendar = get_calendar(calendar)        trading_environment = TradingEnvironment(bm_symbol=None,                                                 exchange_tz=exchange_tz,                                                 trading_calendar=trading_calendar,                                                 asset_db_path=connstr)        self.__calendar__ = trading_calendar        self.__trading_environment__ = trading_environment        ############################################# choose_loader #############################################        pipeline_loader = USEquityPricingLoader(            bundle_data.equity_daily_bar_reader,            bundle_data.adjustment_reader,        )        def choose_loader(column):            if column in USEquityPricing.columns:                return pipeline_loader            raise ValueError(                "No PipelineLoader registered for column %s." % column            )        self.__choose_loader__ = choose_loader        your_engine = SimplePipelineEngine(get_loader=choose_loader, calendar=trading_calendar.all_sessions,                                           asset_finder=trading_environment.asset_finder)        self.__engine__ = your_engine        # your_engine._finder        first_trading_day = \            bundle_data.equity_minute_bar_reader.first_trading_day        data = DataPortal(            trading_environment.asset_finder, get_calendar(calendar),            first_trading_day=first_trading_day,            equity_minute_reader=bundle_data.equity_minute_bar_reader,            equity_daily_reader=bundle_data.equity_daily_bar_reader,            adjustment_reader=bundle_data.adjustment_reader,        )        self.__data_portal__ = data        self.__first_trading_day__ = first_trading_day    def get_engine(self):        return self.__engine__    def get_data_portal(self):        return self.__data_portal__    def run_pipeline(self, pipeline, start_date, end_date):        return self.__engine__.run_pipeline(pipeline, start_date, end_date)    # support open, high,low, close, volume not price    def get_pricing(self, stocks, start, end, frequency, fields, ffill=True):        # assets = [self.__trading_environment__.asset_finder.lookup_symbol(msid,as_of_date=None).sid for msid in stocks]        # print stocks,type(stocks)        assets = [self.__trading_environment__.asset_finder.lookup_symbol(msid, as_of_date=None) for msid in stocks]        # print "assets:",assets,type(assets),stocks        # print start,end        # print fields,type(fields)        # print pd.Timestamp(start),pd.Timestamp(end)        end_dt = pd.Timestamp(end) - pd.Timedelta(days=0)        bar_count = pd.Timestamp(end) - pd.Timestamp(start) + pd.Timedelta(days=1)        bar_count = bar_count.days        if '1.0.2' == zipline.__version__[0:5]:            df_dict = {                    field: self.__data_portal__.get_history_window(                        assets,                        end_dt,                        bar_count,                        frequency,                        field                    ).reindex(pd.date_range(start, end, tz='UTC', freq='C')) for field in fields            }            return pd.Panel(df_dict)        elif  '1.1.1' == zipline.__version__[0:5]:            df_dict = {                field: self.__data_portal__.get_history_window(                    assets,                    end_dt,                    bar_count,                    frequency,                    field,                    'daily',                ).reindex(pd.date_range(start, end, tz='UTC', freq='C')) for field in fields            }            return pd.Panel(df_dict)        else:            pass