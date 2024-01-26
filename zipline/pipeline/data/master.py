# Copyright 2020 QuantRocket LLC - All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import TYPE_CHECKING
from zipline.utils.numpy_utils import (
    bool_dtype,
    float64_dtype,
    object_dtype,
    datetime64ns_dtype,
    NaTD)
from zipline.pipeline.data import Column, DataSet
if TYPE_CHECKING:
    from zipline.pipeline.data.dataset import (
        BoundBooleanColumn,
        BoundFloatColumn,
        BoundObjectColumn,
        BoundDatetimeColumn
    )

class SecuritiesMaster(DataSet):
    """
    Dataset representing the securities master file.

    Attributes
    ----------

    Sid : str
        the security identifier

    Symbol : str
        the ticker symbol

    Exchange : str
        primary exchange of the security

    Currency : str
        currency in which the security is traded

    SecType : str
        the security type

    Etf : bool
        whether the security is an ETF

    Timezone : str
        the timezone in which the security is traded

    Name : str
        the name of the security

    PriceMagnifier : float
        price divisor to use when prices are quoted in a different currency than the security's currency (for example GBP-denominated securities which trade in GBX will have a PriceMagnifier of 100)

    Multiplier : float
        contract multiplier for options and futures

    Delisted : bool
        whether the security is delisted

    DateDelisted : datetime64D
        date the security was delisted

    LastTradeDate : datetime64D
        last trade date for derivatives

    RolloverDate : datetime64D
        rollover date for futures

    alpaca_AssetId : str
        Asset ID

    alpaca_AssetClass : str
        always "us_equity"

    alpaca_Exchange : str
        AMEX, ARCA, BATS, NYSE, NASDAQ or NYSEARCA

    alpaca_Symbol : str
        ticker symbol

    alpaca_Name : str
        the name of the security

    alpaca_Status : str
        active or inactive

    alpaca_Tradable : float
        Asset is tradable on Alpaca or not.

    alpaca_Marginable : float
        Asset is marginable or not.

    alpaca_Shortable : float
        Asset is shortable or not.

    alpaca_EasyToBorrow : float
        Asset is easy-to-borrow or not (filtering for easy_to_borrow = True is
        the best way to check whether the name is currently available to short
        at Alpaca).

    edi_SecId : float
        Unique global level Security ID (can be used to link all multiple
        listings together)

    edi_Currency : str
        the currency in which the security is traded

    edi_PrimaryMic : str
        MIC code for the primary listing (empty if unknown)

    edi_Mic : str
        ISO standard Market Identification Code

    edi_MicSegment : str
        ISO standard Market Identification Code

    edi_MicTimezone : str
        the timezone in which the security is traded

    edi_IsPrimaryListing : float
        1 if PrimaryMic = Mic

    edi_LocalSymbol : str
        Local code unique at Market level - a ticker or number

    edi_IssuerId : float
        Unique global level Issuer ID (can be used to link all securities of a
        company togther)

    edi_IssuerName : str
        the name of the issuer

    edi_IsoCountryInc : str
        ISO Country of Incorporation of Issuer

    edi_CountryInc : str
        country of incorporation of the issuer

    edi_IsoCountryListed : str
        country of Exchange where listed

    edi_CountryListed : str
        country of Exchange where listed

    edi_SicCode : int
        Standard Industrial Classification Code

    edi_Sic : str
        SIC name

    edi_SicIndustryGroup : str
        SIC Industry Group

    edi_SicMajorGroup : str
        SIC Major Group

    edi_SicDivision : str
        SIC Division

    edi_Cik : str
        Central Index Key

    edi_Industry : str
        Industry of the issuer

    edi_SecTypeCode : str
        Type of Equity Instrument

    edi_SecTypeDesc : str
        Type of Equity Instrument (lookup SECTYPE with SectyCD)

    edi_SecurityDesc : str
        description of security

    edi_PreferredName : str
        for ETFs, the SecurityDesc, else the IssuerName

    edi_GlobalListingStatus : str
        Inactive at the global level else security is active. Not to be
        confused with delisted which is inactive at the exchange level (lookup
        SECSTATUS)

    edi_ExchangeListingStatus : str
        Indicates whether a security is Listed on an Exchange or Unlisted
        Indicates Exchange Listing Status (lookup LISTSTAT)

    edi_DateDelisted : datetime64D
        date the security was delisted

    edi_StructureCode : str

    edi_StructureDesc : str

    edi_RecordModified : str
        Date event updated, format is yyyy/mm/dd hh:mm:ss

    edi_RecordCreated : str
        Date event first entered

    edi_FirstPriceDate : datetime64D
        first date a price is available

    edi_LastPriceDate : datetime64D
        latest date a price is available

    ibkr_ConId : float
        IBKR Contract ID

    ibkr_Symbol : str
        ticker symbol

    ibkr_SecType : str
        security type

    ibkr_Etf : bool
        whether the security is an ETF

    ibkr_PrimaryExchange : str
        the primary exchange of the security

    ibkr_Currency : str
        the currency in which the security is traded

    ibkr_StockType : str
        the stock type, e.g. COMMON, PREFERRED, ADR, ETF, etc.

    ibkr_LocalSymbol : str
        ticker symbol used on the exchange

    ibkr_TradingClass : str

    ibkr_MarketName : str

    ibkr_LongName : str
        the name of the security

    ibkr_Timezone : str
        the timezone in which the security is traded

    ibkr_ValidExchanges : str
        comma-separated list of exchanges where the security is traded

    ibkr_AggGroup : float

    ibkr_Sector : str
        the sector of the security

    ibkr_Industry : str
        the industry of the security

    ibkr_Category : str
        the category of the security

    ibkr_MinTick : float

    ibkr_PriceMagnifier : float
        price divisor to use when prices are quoted in a different currency than the security's currency (for example GBP-denominated securities which trade in GBX will have an ibkr_PriceMagnifier of 100)

    ibkr_LastTradeDate : datetime64D
        the last trade date for derivatives

    ibkr_ContractMonth : float
        expiration year-month for derivatives

    ibkr_RealExpirationDate : datetime64D
        expiration date for derivative contracts

    ibkr_Multiplier : float
        contract multiplier for options and futures

    ibkr_UnderConId : float
        Contract ID of the underlying security for derivatives

    ibkr_UnderSymbol : str
        ticker symbol of the underlying security for derivatives

    ibkr_UnderSecType : str
        security type of the underlying security for derivatives

    ibkr_MarketRuleIds : str

    ibkr_Strike : float
        option strike price

    ibkr_Right : str
        whether the option is a call or put

    ibkr_Isin : str
        ISIN identifier for the security

    ibkr_Cusip : str

    ibkr_EvRule : str

    ibkr_EvMultiplier : float

    ibkr_MinSize : float
        minimum order size, i.e. lot size

    ibkr_SizeIncrement : float
        minimum order size increment that can be added to ibkr_MinSize

    ibkr_SuggestedSizeIncrement : float
        suggested order size increment (i.e. suggested lot size)

    ibkr_Delisted : bool
        whether the security is delisted

    ibkr_DateDelisted : datetime64D
        date the security was delisted

    sharadar_Permaticker : float
        Permanent Ticker Symbol - The permaticker is a unique and unchanging
        identifier for an issuer in the dataset which is issued by Sharadar.

    sharadar_Ticker : str
        Ticker Symbol - The ticker is a unique identifer for an issuer in the
        database. Where a ticker contains a "." or a "-" this is removed from
        the ticker. For example BRK.B is BRKB. We include the BRK.B ticker in
        the Related Tickers field. Where a company is delisted and the ticker
        is recycled; we use that ticker for the currently active company and
        append a number to the ticker of the delisted company. eg GM is the
        current actively traded entity; & GM1 is the entity that filed for
        bankruptcy in 2009.

    sharadar_Name : str
        Issuer Name - The name of the security issuer.

    sharadar_Exchange : str
        Stock Exchange - The exchange on which the security trades. Examples
        are: "NASDAQ";"NYSE";"NYSEARCA";"BATS";"OTC" and "NYSEMKT" (previously
        the American Stock exchange).

    sharadar_Delisted : bool
        Is Delisted? - Is the security delisted?

    sharadar_DateDelisted : datetime64D
        Date the security was delisted

    sharadar_Category : str
        Issuer Category - The category of the issuer: "Domestic"; "Canadian"
        or "ADR".

    sharadar_Cusips : str
        CUSIPs - A security identifier. Space delimited in the event of
        multiple identifiers.

    sharadar_SicCode : int
        Standard Industrial Classification (SIC) Code - The Standard
        Industrial Classification (SIC) is a system for classifying industries
        by a four-digit code; as sourced from SEC filings. More on the SIC
        system here:
        https://en.wikipedia.org/wiki/Standard_Industrial_Classification

    sharadar_SicSector : str
        SIC Sector - The SIC sector is based on the SIC code and the division
        tabled here:
        https://en.wikipedia.org/wiki/Standard_Industrial_Classification

    sharadar_SicIndustry : str
        SIC Industry - The SIC industry is based on the SIC code and the
        industry tabled here: https://www.sec.gov/info/edgar/siccodes.htm

    sharadar_FamaSector : str
        Fama Sector - Not currently active - coming in a future update.

    sharadar_FamaIndustry : str
        Fama Industry - Industry classifications based on the SIC code and
        classifications by Fama and French here: http://mba.tuck.dartmouth.edu
        /pages/faculty/ken.french/Data_Library/det_48_ind_port.html

    sharadar_Sector : str
        Sector - Sharadar's sector classification based on SIC codes in a
        format which approximates to GICS.

    sharadar_Industry : str
        Industry - Sharadar's industry classification based on SIC codes in a
        format which approximates to GICS.

    sharadar_ScaleMarketCap : str
        Company Scale - Market Cap - This field is experimental and subject to
        change. It categorises the company according to it's maximum observed
        market cap as follows: 1 - Nano <$50m; 2 - Micro < $300m; 3 - Small <
        $2bn; 4 - Mid <$10bn; 5 - Large < $200bn; 6 - Mega >= $200bn

    sharadar_ScaleRevenue : str
        Company Scale - Revenue - This field is experimental and subject to
        change. It categorises the company according to it's maximum observed
        annual revenue as follows: 1 - Nano <$50m; 2 - Micro < $300m; 3 -
        Small < $2bn; 4 - Mid <$10bn; 5 - Large < $200bn; 6 - Mega >= $200bn

    sharadar_RelatedTickers : str
        Related Tickers - Where related tickers have been identified this
        field is populated. Related tickers can include the prior ticker
        before a ticker change; and it tickers for alternative share classes.

    sharadar_Currency : str
        Currency - The company functional reporting currency for the SF1
        Fundamentals table or the currency for EOD prices in SEP and SFP.

    sharadar_Location : str
        Location - The company location as registered with the Securities and
        Exchange Commission.

    sharadar_CountryListed : str
        ISO country code where security is listed

    sharadar_LastUpdated : datetime64D
        Last Updated Date - Last Updated represents the last date that this
        database entry was updated; which is useful to users when updating
        their local records.

    sharadar_FirstAdded : datetime64D
        First Added Date - The date that the ticker was first added to
        coverage in the dataset.

    sharadar_FirstPriceDate : datetime64D
        First Price Date - The date of the first price observation for a given
        ticker. Can be used as a proxy for IPO date. Minimum value of
        1986-01-01 for IPO's that occurred prior to this date. Note: this does
        not necessarily represent the first price date available in our
        datasets since our end of day price history currently starts in
        December 1998.

    sharadar_LastPriceDate : datetime64D
        Last Price Date - The most recent price observation available.

    sharadar_FirstQuarter : datetime64D
        First Quarter - The first financial quarter available in the dataset.

    sharadar_LastQuarter : datetime64D
        Last Quarter - The last financial quarter available in the dataset.

    sharadar_SecFilings : str
        SEC Filings URL - The URL pointing to the SEC filings which also
        contains the Central Index Key (CIK).

    sharadar_CompanySite : str
        Company Website URL - The URL pointing to the company website.

    usstock_Mic : str
        market identifier code for the security

    usstock_Symbol : str
        ticker symbol

    usstock_Name : str
        the name of the security

    usstock_Sector : str
        sector in which company operates. There are 11 possible sectors.

    usstock_Industry : str
        industry in which company operates. There are 58 possible industries.

    usstock_SicCode : str
        Standard Industrial Classification Code, used in SEC filings

    usstock_Sic : str
        SIC code description, bottom tier in SIC hierarchy, e.g.
        "Electronic Computers"

    usstock_SicIndustryGroup : str
         3rd-level tier in SIC hierarchy, e.g. "Computer And Office Equipment"

    usstock_SicMajorGroup : str
        2nd-level tier in SIC hierarchy, e.g. "Industrial And Commercial
        Machinery And Computer Equipment"

    usstock_SicDivision : str
        Top-level tier in SIC hierarchy

    usstock_SecurityType : str
        security type (more detailed than usstock_SecurityType2)

    usstock_SecurityType2 : str
        security type (less detailed than usstock_SecurityType)

    usstock_CIK : str
        the Central Index Key is the unique company identifier in SEC filings

    usstock_PrimaryShareSid : str
        the sid of the primary share class, if not this security (for companies with
        multiple share classes). Filtering to securities where usstock_PrimaryShareSid
        is null is a way to deduplicate companies with multiple share classes.

    usstock_DateDelisted : datetime64D
        date the security was delisted

    usstock_FirstPriceDate : datetime64D
        date of first available price

    usstock_LastPriceDate : datetime64D
        date of last available price

    figi_Figi : str
        e.g. BBG000BBBRC7

    figi_Name : str
        e.g. AFLAC INC

    figi_Ticker : str
        e.g. AFL

    figi_CompositeFigi : str
        e.g. BBG000BBBNC6

    figi_ExchCode : str
        e.g. UN

    figi_UniqueId : str
        e.g. EQ0010001500001000

    figi_SecurityType : str
        e.g. Common Stock

    figi_MarketSector : str
        e.g. Equity

    figi_ShareClassFigi : str
        e.g. BBG001S5NGJ4

    figi_UniqueIdFutOpt : str

    figi_SecurityType2 : str
        e.g. Common Stock

    figi_SecurityDescription : str
        e.g. AFL

    figi_IsComposite : bool
        whether the Figi column contains a composite FIGI

    Notes
    -----
    Usage Guide:

    * Securities master: https://qrok.it/dl/z/pipeline-securities-master

    Examples
    --------
    Filter ETFs::

        are_etfs = SecuritiesMaster.Etf.latest

    Filter NYSE stocks::

        are_nyse_stocks = SecuritiesMaster.Exchange.latest.eq("XNYS")

    Filter to primary shares, which can be identified by a null
    usstock_PrimaryShareSid field (i.e. they have no pointer to another
    primary share)::

        are_primary_shares = master.SecuritiesMaster.usstock_PrimaryShareSid.latest.isnull()
    """
    Sid: 'BoundObjectColumn' = Column(object_dtype)
    """security identifier"""
    Symbol: 'BoundObjectColumn' = Column(object_dtype)
    """ticker symbol"""
    Exchange: 'BoundObjectColumn' = Column(object_dtype)
    """primary exchange of the security"""
    Currency: 'BoundObjectColumn' = Column(object_dtype)
    """currency in which the security is traded"""
    SecType: 'BoundObjectColumn' = Column(object_dtype)
    """ the security type"""
    Etf: 'BoundBooleanColumn' = Column(bool_dtype)
    """ whether the security is an ETF"""
    Timezone: 'BoundObjectColumn' = Column(object_dtype)
    """the timezone in which the security is traded"""
    Name: 'BoundObjectColumn' = Column(object_dtype)
    """the name of the security"""
    PriceMagnifier: 'BoundFloatColumn' = Column(float64_dtype)
    """price divisor to use when prices are quoted in a different currency than the security's currency (for example GBP-denominated securities which trade in GBX will have a PriceMagnifier of 100)"""
    Multiplier: 'BoundFloatColumn' = Column(float64_dtype)
    """contract multiplier for options and futures"""
    Delisted: 'BoundBooleanColumn' = Column(bool_dtype)
    """whether the security is delisted"""
    DateDelisted: 'BoundDatetimeColumn' = Column(datetime64ns_dtype, missing_value=NaTD)
    """date the security was delisted"""
    LastTradeDate: 'BoundDatetimeColumn' = Column(datetime64ns_dtype, missing_value=NaTD)
    """last trade date for derivatives"""
    RolloverDate: 'BoundDatetimeColumn' = Column(datetime64ns_dtype, missing_value=NaTD)
    """rollover date for futures"""
    alpaca_AssetId: 'BoundObjectColumn' = Column(object_dtype)
    """Asset ID"""
    alpaca_AssetClass: 'BoundObjectColumn' = Column(object_dtype)
    """always 'us_equity'"""
    alpaca_Exchange: 'BoundObjectColumn' = Column(object_dtype)
    """AMEX, ARCA, BATS, NYSE, NASDAQ or NYSEARCA"""
    alpaca_Symbol: 'BoundObjectColumn' = Column(object_dtype)
    """ticker symbol"""
    alpaca_Name: 'BoundObjectColumn' = Column(object_dtype)
    """the name of the security"""
    alpaca_Status: 'BoundObjectColumn' = Column(object_dtype)
    """active or inactive"""
    alpaca_Tradable: 'BoundFloatColumn' = Column(float64_dtype)
    """Asset is tradable on Alpaca or not"""
    alpaca_Marginable: 'BoundFloatColumn' = Column(float64_dtype)
    """Asset is marginable or not"""
    alpaca_Shortable: 'BoundFloatColumn' = Column(float64_dtype)
    """Asset is shortable or not"""
    alpaca_EasyToBorrow: 'BoundFloatColumn' = Column(float64_dtype)
    """Asset is easy-to-borrow or not (filtering for easy_to_borrow = True is the best way to check whether the name is currently available to short at Alpaca)."""
    edi_SecId: 'BoundFloatColumn' = Column(float64_dtype)
    """Unique global level Security ID (can be used to link all multiple listings together)"""
    edi_Currency: 'BoundObjectColumn' = Column(object_dtype)
    """the currency in which the security is traded"""
    edi_PrimaryMic: 'BoundObjectColumn' = Column(object_dtype)
    """MIC code for the primary listing (empty if unknown)"""
    edi_Mic: 'BoundObjectColumn' = Column(object_dtype)
    """ISO standard Market Identification Code"""
    edi_MicSegment: 'BoundObjectColumn' = Column(object_dtype)
    """ISO standard Market Identification Code"""
    edi_MicTimezone: 'BoundObjectColumn' = Column(object_dtype)
    """the timezone in which the security is traded"""
    edi_IsPrimaryListing: 'BoundFloatColumn' = Column(float64_dtype)
    """1 if PrimaryMic = Mic"""
    edi_LocalSymbol: 'BoundObjectColumn' = Column(object_dtype)
    """Local code unique at Market level - a ticker or number"""
    edi_IssuerId: 'BoundFloatColumn' = Column(float64_dtype)
    """Unique global level Issuer ID (can be used to link all securities of a company togther)"""
    edi_IssuerName: 'BoundObjectColumn' = Column(object_dtype)
    """the name of the issuer"""
    edi_IsoCountryInc: 'BoundObjectColumn' = Column(object_dtype)
    """ISO Country of Incorporation of Issuer"""
    edi_CountryInc: 'BoundObjectColumn' = Column(object_dtype)
    """country of incorporation of the issuer"""
    edi_IsoCountryListed: 'BoundObjectColumn' = Column(object_dtype)
    """country of Exchange where listed"""
    edi_CountryListed: 'BoundObjectColumn' = Column(object_dtype)
    """country of Exchange where listed"""
    edi_SicCode: 'BoundObjectColumn' = Column(object_dtype)
    """Standard Industrial Classification Code"""
    edi_Sic: 'BoundObjectColumn' = Column(object_dtype)
    """SIC name"""
    edi_SicIndustryGroup: 'BoundObjectColumn' = Column(object_dtype)
    """SIC Industry Group"""
    edi_SicMajorGroup: 'BoundObjectColumn' = Column(object_dtype)
    """SIC Major Group"""
    edi_SicDivision: 'BoundObjectColumn' = Column(object_dtype)
    """SIC Division"""
    edi_Cik: 'BoundObjectColumn' = Column(object_dtype)
    """Central Index Key"""
    edi_Industry: 'BoundObjectColumn' = Column(object_dtype)
    """Industry of the issuer"""
    edi_SecTypeCode: 'BoundObjectColumn' = Column(object_dtype)
    """Type of Equity Instrument"""
    edi_SecTypeDesc: 'BoundObjectColumn' = Column(object_dtype)
    """Type of Equity Instrument (lookup SECTYPE with SectyCD)"""
    edi_SecurityDesc: 'BoundObjectColumn' = Column(object_dtype)
    """description of security"""
    edi_PreferredName: 'BoundObjectColumn' = Column(object_dtype)
    """for ETFs, the SecurityDesc, else the IssuerName"""
    edi_GlobalListingStatus: 'BoundObjectColumn' = Column(object_dtype)
    """Inactive at the global level else security is active. Not to be confused with delisted which is inactive at the exchange level (lookup SECSTATUS)"""
    edi_ExchangeListingStatus: 'BoundObjectColumn' = Column(object_dtype)
    """Indicates whether a security is Listed on an Exchange or Unlisted Indicates Exchange Listing Status (lookup LISTSTAT)"""
    edi_DateDelisted: 'BoundDatetimeColumn' = Column(datetime64ns_dtype, missing_value=NaTD)
    """date the security was delisted"""
    edi_StructureCode: 'BoundObjectColumn' = Column(object_dtype)
    edi_StructureDesc: 'BoundObjectColumn' = Column(object_dtype)
    edi_RecordModified: 'BoundObjectColumn' = Column(object_dtype)
    """Date event updated, format is yyyy/mm/dd hh:mm:ss"""
    edi_RecordCreated: 'BoundObjectColumn' = Column(object_dtype)
    """Date event first entered"""
    edi_FirstPriceDate: 'BoundDatetimeColumn' = Column(datetime64ns_dtype, missing_value=NaTD)
    """first date a price is available"""
    edi_LastPriceDate: 'BoundDatetimeColumn' = Column(datetime64ns_dtype, missing_value=NaTD)
    """latest date a price is available"""
    ibkr_ConId: 'BoundFloatColumn' = Column(float64_dtype)
    """IBKR Contract ID"""
    ibkr_Symbol: 'BoundObjectColumn' = Column(object_dtype)
    """ticker symbol"""
    ibkr_SecType: 'BoundObjectColumn' = Column(object_dtype)
    """security type"""
    ibkr_Etf: 'BoundBooleanColumn' = Column(bool_dtype)
    """whether the security is an ETF"""
    ibkr_PrimaryExchange: 'BoundObjectColumn' = Column(object_dtype)
    """the primary exchange of the security"""
    ibkr_Currency: 'BoundObjectColumn' = Column(object_dtype)
    """the currency in which the security is traded"""
    ibkr_StockType: 'BoundObjectColumn' = Column(object_dtype)
    """the stock type, e.g. COMMON, PREFERRED, ADR, ETF, etc."""
    ibkr_LocalSymbol: 'BoundObjectColumn' = Column(object_dtype)
    """ticker symbol used on the exchange"""
    ibkr_TradingClass: 'BoundObjectColumn' = Column(object_dtype)
    ibkr_MarketName: 'BoundObjectColumn' = Column(object_dtype)
    ibkr_LongName: 'BoundObjectColumn' = Column(object_dtype)
    """the name of the security"""
    ibkr_Timezone: 'BoundObjectColumn' = Column(object_dtype)
    """the timezone in which the security is traded"""
    ibkr_ValidExchanges: 'BoundObjectColumn' = Column(object_dtype)
    """comma-separated list of exchanges where the security is traded"""
    ibkr_AggGroup: 'BoundFloatColumn' = Column(float64_dtype)
    ibkr_Sector: 'BoundObjectColumn' = Column(object_dtype)
    """the sector of the security"""
    ibkr_Industry: 'BoundObjectColumn' = Column(object_dtype)
    """the industry of the security"""
    ibkr_Category: 'BoundObjectColumn' = Column(object_dtype)
    """the category of the security"""
    ibkr_MinTick: 'BoundFloatColumn' = Column(float64_dtype)
    ibkr_PriceMagnifier: 'BoundFloatColumn' = Column(float64_dtype)
    """price divisor to use when prices are quoted in a different currency than the security's currency (for example GBP-denominated securities which trade in GBX will have an ibkr_PriceMagnifier of 100)"""
    ibkr_MdSizeMultiplier: 'BoundFloatColumn' = Column(float64_dtype) # deprecated
    ibkr_LastTradeDate: 'BoundDatetimeColumn' = Column(datetime64ns_dtype, missing_value=NaTD)
    """the last trade date for derivatives"""
    ibkr_ContractMonth: 'BoundFloatColumn' = Column(float64_dtype)
    """expiration year-month for derivatives"""
    ibkr_RealExpirationDate: 'BoundDatetimeColumn' = Column(datetime64ns_dtype, missing_value=NaTD)
    """expiration date for derivative contracts"""
    ibkr_Multiplier: 'BoundFloatColumn' = Column(float64_dtype)
    """contract multiplier for options and futures"""
    ibkr_UnderConId: 'BoundFloatColumn' = Column(float64_dtype)
    """Contract ID of the underlying security for derivatives"""
    ibkr_UnderSymbol: 'BoundObjectColumn' = Column(object_dtype)
    """ticker symbol of the underlying security for derivatives"""
    ibkr_UnderSecType: 'BoundObjectColumn' = Column(object_dtype)
    """security type of the underlying security for derivatives"""
    ibkr_MarketRuleIds: 'BoundObjectColumn' = Column(object_dtype)
    ibkr_Strike: 'BoundFloatColumn' = Column(float64_dtype)
    """option strike price"""
    ibkr_Right: 'BoundObjectColumn' = Column(object_dtype)
    """whether the option is a call or put"""
    ibkr_Isin: 'BoundObjectColumn' = Column(object_dtype)
    """ISIN identifier for the security"""
    ibkr_Cusip: 'BoundObjectColumn' = Column(object_dtype)
    ibkr_EvRule: 'BoundObjectColumn' = Column(object_dtype)
    ibkr_EvMultiplier: 'BoundFloatColumn' = Column(float64_dtype)
    ibkr_MinSize: 'BoundFloatColumn' = Column(float64_dtype)
    """minimum order size, i.e. lot size"""
    ibkr_SizeIncrement: 'BoundFloatColumn' = Column(float64_dtype)
    """minimum order size increment that can be added to ibkr_MinSize"""
    ibkr_SuggestedSizeIncrement: 'BoundFloatColumn' = Column(float64_dtype)
    """suggested order size increment (i.e. suggested lot size)"""
    ibkr_Delisted: 'BoundBooleanColumn' = Column(bool_dtype)
    """whether the security is delisted"""
    ibkr_DateDelisted: 'BoundDatetimeColumn' = Column(datetime64ns_dtype, missing_value=NaTD)
    """date the security was delisted"""
    sharadar_Permaticker: 'BoundFloatColumn' = Column(float64_dtype)
    """Permanent Ticker Symbol - The permaticker is a unique and unchanging identifier for an issuer in the dataset which is issued by Sharadar."""
    sharadar_Ticker: 'BoundObjectColumn' = Column(object_dtype)
    """Ticker Symbol - The ticker is a unique identifer for an issuer in the
    database. Where a ticker contains a "." or a "-" this is removed from
    the ticker. For example BRK.B is BRKB. We include the BRK.B ticker in
    the Related Tickers field. Where a company is delisted and the ticker
    is recycled; we use that ticker for the currently active company and
    append a number to the ticker of the delisted company. eg GM is the
    current actively traded entity; & GM1 is the entity that filed for
    bankruptcy in 2009."""
    sharadar_Name: 'BoundObjectColumn' = Column(object_dtype)
    """Issuer Name - The name of the security issuer."""
    sharadar_Exchange: 'BoundObjectColumn' = Column(object_dtype)
    """Stock Exchange - The exchange on which the security trades. Examples
    are: "NASDAQ";"NYSE";"NYSEARCA";"BATS";"OTC" and "NYSEMKT" (previously
    the American Stock exchange)."""
    sharadar_Delisted: 'BoundBooleanColumn' = Column(bool_dtype)
    """Is Delisted? - Is the security delisted?"""
    sharadar_DateDelisted: 'BoundDatetimeColumn' = Column(datetime64ns_dtype, missing_value=NaTD)
    """Date the security was delisted"""
    sharadar_Category: 'BoundObjectColumn' = Column(object_dtype)
    """Issuer Category - The category of the issuer: "Domestic"; "Canadian"
    or "ADR"."""
    sharadar_Cusips: 'BoundObjectColumn' = Column(object_dtype)
    """CUSIPs - A security identifier. Space delimited in the event of
    multiple identifiers."""
    sharadar_SicCode: 'BoundObjectColumn' = Column(object_dtype)
    """Standard Industrial Classification (SIC) Code - The Standard
    Industrial Classification (SIC) is a system for classifying industries
    by a four-digit code; as sourced from SEC filings. More on the SIC
    system here:
    https://en.wikipedia.org/wiki/Standard_Industrial_Classification"""
    sharadar_SicSector: 'BoundObjectColumn' = Column(object_dtype)
    """SIC Sector - The SIC sector is based on the SIC code and the division
    tabled here:
    https://en.wikipedia.org/wiki/Standard_Industrial_Classification"""
    sharadar_SicIndustry: 'BoundObjectColumn' = Column(object_dtype)
    """SIC Industry - The SIC industry is based on the SIC code and the
    industry tabled here: https://www.sec.gov/info/edgar/siccodes.htm"""
    sharadar_FamaSector: 'BoundObjectColumn' = Column(object_dtype)
    """Fama Sector - Not currently active - coming in a future update."""
    sharadar_FamaIndustry: 'BoundObjectColumn' = Column(object_dtype)
    """Fama Industry - Industry classifications based on the SIC code and
    classifications by Fama and French here: http://mba.tuck.dartmouth.edu
    /pages/faculty/ken.french/Data_Library/det_48_ind_port.html"""
    sharadar_Sector: 'BoundObjectColumn' = Column(object_dtype)
    """Sector - Sharadar's sector classification based on SIC codes in a
    format which approximates to GICS."""
    sharadar_Industry: 'BoundObjectColumn' = Column(object_dtype)
    """Industry - Sharadar's industry classification based on SIC codes in a
    format which approximates to GICS."""
    sharadar_ScaleMarketCap: 'BoundObjectColumn' = Column(object_dtype)
    """Company Scale - Market Cap - This field is experimental and subject to
    change. It categorises the company according to it's maximum observed
    market cap as follows: 1 - Nano <$50m; 2 - Micro < $300m; 3 - Small <
    $2bn; 4 - Mid <$10bn; 5 - Large < $200bn; 6 - Mega >= $200bn"""
    sharadar_ScaleRevenue: 'BoundObjectColumn' = Column(object_dtype)
    """Company Scale - Revenue - This field is experimental and subject to
    change. It categorises the company according to it's maximum observed
    annual revenue as follows: 1 - Nano <$50m; 2 - Micro < $300m; 3 -
    Small < $2bn; 4 - Mid <$10bn; 5 - Large < $200bn; 6 - Mega >= $200bn"""
    sharadar_RelatedTickers: 'BoundObjectColumn' = Column(object_dtype)
    """Related Tickers - Where related tickers have been identified this
    field is populated. Related tickers can include the prior ticker
    before a ticker change; and it tickers for alternative share classes."""
    sharadar_Currency: 'BoundObjectColumn' = Column(object_dtype)
    """Currency - The company functional reporting currency for the SF1
    Fundamentals table or the currency for EOD prices in SEP and SFP."""
    sharadar_Location: 'BoundObjectColumn' = Column(object_dtype)
    """Location - The company location as registered with the Securities and
    Exchange Commission."""
    sharadar_CountryListed: 'BoundObjectColumn' = Column(object_dtype)
    """ISO country code where security is listed"""
    sharadar_LastUpdated: 'BoundDatetimeColumn' = Column(datetime64ns_dtype, missing_value=NaTD)
    """Last Updated Date - Last Updated represents the last date that this
    database entry was updated; which is useful to users when updating
    their local records."""
    sharadar_FirstAdded: 'BoundDatetimeColumn' = Column(datetime64ns_dtype, missing_value=NaTD)
    """First Added Date - The date that the ticker was first added to
    coverage in the dataset."""
    sharadar_FirstPriceDate: 'BoundDatetimeColumn' = Column(datetime64ns_dtype, missing_value=NaTD)
    """First Price Date - The date of the first price observation for a given
    ticker. Can be used as a proxy for IPO date. Minimum value of
    1986-01-01 for IPO's that occurred prior to this date. Note: this does
    not necessarily represent the first price date available in our
    datasets since our end of day price history currently starts in
    December 1998."""
    sharadar_LastPriceDate: 'BoundDatetimeColumn' = Column(datetime64ns_dtype, missing_value=NaTD)
    """Last Price Date - The most recent price observation available."""
    sharadar_FirstQuarter: 'BoundDatetimeColumn' = Column(datetime64ns_dtype, missing_value=NaTD)
    """First Quarter - The first financial quarter available in the dataset."""
    sharadar_LastQuarter: 'BoundDatetimeColumn' = Column(datetime64ns_dtype, missing_value=NaTD)
    """Last Quarter - The last financial quarter available in the dataset."""
    sharadar_SecFilings: 'BoundObjectColumn' = Column(object_dtype)
    """SEC Filings URL - The URL pointing to the SEC filings which also
    contains the Central Index Key (CIK)."""
    sharadar_CompanySite: 'BoundObjectColumn' = Column(object_dtype)
    """Company Website URL - The URL pointing to the company website."""
    usstock_Mic: 'BoundObjectColumn' = Column(object_dtype)
    """market identifier code for the security"""
    usstock_Symbol: 'BoundObjectColumn' = Column(object_dtype)
    """ticker symbol"""
    usstock_Name: 'BoundObjectColumn' = Column(object_dtype)
    """the name of the security"""
    usstock_Sector: 'BoundObjectColumn' = Column(object_dtype)
    """sector in which company operates. There are 11 possible sectors."""
    usstock_Industry: 'BoundObjectColumn' = Column(object_dtype)
    """industry in which company operates. There are 58 possible industries."""
    usstock_SicCode: 'BoundObjectColumn' = Column(object_dtype)
    """Standard Industrial Classification Code, used in SEC filings"""
    usstock_Sic: 'BoundObjectColumn' = Column(object_dtype)
    """SIC code description, bottom tier in SIC hierarchy, e.g.
    "Electronic Computers"""
    usstock_SicIndustryGroup: 'BoundObjectColumn' = Column(object_dtype)
    """3rd-level tier in SIC hierarchy, e.g. "Computer And Office Equipment"""
    usstock_SicMajorGroup: 'BoundObjectColumn' = Column(object_dtype)
    """2nd-level tier in SIC hierarchy, e.g. "Industrial And Commercial
    Machinery And Computer Equipment"""
    usstock_SicDivision: 'BoundObjectColumn' = Column(object_dtype)
    """Top-level tier in SIC hierarchy"""
    usstock_SecurityType: 'BoundObjectColumn' = Column(object_dtype)
    """security type (more detailed than usstock_SecurityType2)"""
    usstock_SecurityType2: 'BoundObjectColumn' = Column(object_dtype)
    """security type (less detailed than usstock_SecurityType)"""
    usstock_CIK: 'BoundObjectColumn' = Column(object_dtype)
    """the Central Index Key is the unique company identifier in SEC filings"""
    usstock_PrimaryShareSid: 'BoundObjectColumn' = Column(object_dtype)
    """the sid of the primary share class, if not this security (for companies with
    multiple share classes). Filtering to securities where usstock_PrimaryShareSid
    is null is a way to deduplicate companies with multiple share classes."""
    usstock_DateDelisted: 'BoundDatetimeColumn' = Column(datetime64ns_dtype, missing_value=NaTD)
    """date the security was delisted"""
    usstock_FirstPriceDate: 'BoundDatetimeColumn' = Column(datetime64ns_dtype, missing_value=NaTD)
    """date of first available price"""
    usstock_LastPriceDate: 'BoundDatetimeColumn' = Column(datetime64ns_dtype, missing_value=NaTD)
    """date of last available price"""
    figi_Figi: 'BoundObjectColumn' = Column(object_dtype)
    """e.g. BBG000BBBRC7"""
    figi_Name: 'BoundObjectColumn' = Column(object_dtype)
    """e.g. AFLAC INC"""
    figi_Ticker: 'BoundObjectColumn' = Column(object_dtype)
    """e.g. AFL"""
    figi_CompositeFigi: 'BoundObjectColumn' = Column(object_dtype)
    """e.g. BBG000BBBNC6"""
    figi_ExchCode: 'BoundObjectColumn' = Column(object_dtype)
    """e.g. UN"""
    figi_UniqueId: 'BoundObjectColumn' = Column(object_dtype)
    """e.g. EQ0010001500001000"""
    figi_SecurityType: 'BoundObjectColumn' = Column(object_dtype)
    """e.g. Common Stock"""
    figi_MarketSector: 'BoundObjectColumn' = Column(object_dtype)
    """e.g. Equity"""
    figi_ShareClassFigi: 'BoundObjectColumn' = Column(object_dtype)
    """ e.g. BBG001S5NGJ4"""
    figi_UniqueIdFutOpt: 'BoundObjectColumn' = Column(object_dtype)
    figi_SecurityType2: 'BoundObjectColumn' = Column(object_dtype)
    """e.g. Common Stock"""
    figi_SecurityDescription: 'BoundObjectColumn' = Column(object_dtype)
    """e.g. AFL"""
    figi_IsComposite: 'BoundBooleanColumn' = Column(bool_dtype)
    """whether the Figi column contains a composite FIGI"""
