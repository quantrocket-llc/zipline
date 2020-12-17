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

from zipline.utils.numpy_utils import (
    bool_dtype,
    float64_dtype,
    object_dtype,
    datetime64ns_dtype,
    NaTD)
from zipline.pipeline.data import Column, DataSet

class SecuritiesMaster(DataSet):
    """
    Dataset representing the securities master file.

    Attributes
    ----------

    Sid : str

    Symbol : str

    Exchange : str

    Currency : str

    SecType : str

    Etf : bool

    Timezone : str

    Name : str

    PriceMagnifier : float

    Multiplier : float

    Delisted : bool

    DateDelisted : datetime64D

    LastTradeDate : datetime64D

    RolloverDate : datetime64D

    alpaca_AssetId : str
        Asset ID

    alpaca_AssetClass : str
        "us_equity"

    alpaca_Exchange : str
        AMEX, ARCA, BATS, NYSE, NASDAQ or NYSEARCA

    alpaca_Symbol : str

    alpaca_Name : str

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

    edi_PrimaryMic : str
        MIC code for the primary listing (empty if unknown)

    edi_Mic : str
        ISO standard Market Identification Code

    edi_MicSegment : str
        ISO standard Market Identification Code

    edi_MicTimezone : str

    edi_IsPrimaryListing : float
        1 if PrimaryMic = Mic

    edi_LocalSymbol : str
        Local code unique at Market level - a ticker or number

    edi_IssuerId : float
        Unique global level Issuer ID (can be used to link all securities of a
        company togther)

    edi_IssuerName : str

    edi_IsoCountryInc : str
        ISO Country of Incorporation of Issuer

    edi_CountryInc : str

    edi_IsoCountryListed : str
        Country of Exchange where listed

    edi_CountryListed : str

    edi_SicCode : int
        Standard Industrial Classification Code

    edi_Sic : str

    edi_SicIndustryGroup : str

    edi_SicMajorGroup : str

    edi_SicDivision : str

    edi_Cik : str
        Central Index Key

    edi_Industry : str

    edi_SecTypeCode : str
        Type of Equity Instrument

    edi_SecTypeDesc : str
        Type of Equity Instrument (lookup SECTYPE with SectyCD)

    edi_SecurityDesc : str

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

    ibkr_Symbol : str

    ibkr_SecType : str

    ibkr_Etf : bool

    ibkr_PrimaryExchange : str

    ibkr_Currency : str

    ibkr_LocalSymbol : str

    ibkr_TradingClass : str

    ibkr_MarketName : str

    ibkr_LongName : str

    ibkr_Timezone : str

    ibkr_ValidExchanges : str

    ibkr_AggGroup : float

    ibkr_Sector : str

    ibkr_Industry : str

    ibkr_Category : str

    ibkr_MinTick : float

    ibkr_PriceMagnifier : float

    ibkr_MdSizeMultiplier : float

    ibkr_LastTradeDate : datetime64D

    ibkr_ContractMonth : float

    ibkr_RealExpirationDate : datetime64D

    ibkr_Multiplier : float

    ibkr_UnderConId : float

    ibkr_UnderSymbol : str

    ibkr_UnderSecType : str

    ibkr_MarketRuleIds : str

    ibkr_Strike : float

    ibkr_Right : str

    ibkr_Isin : str

    ibkr_Cusip : str

    ibkr_EvRule : str

    ibkr_EvMultiplier : float

    ibkr_Delisted : bool

    ibkr_DateDelisted : datetime64D

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

    usstock_Symbol : str

    usstock_Name : str

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

    Examples
    --------
    Filter ETFs:

    >>> are_etfs = SecuritiesMaster.Etf.latest

    Filter NYSE stocks:

    >>> are_nyse_stocks = SecuritiesMaster.Exchange.latest.eq("XNYS")
    """
    Sid = Column(object_dtype)
    Symbol = Column(object_dtype)
    Exchange = Column(object_dtype)
    Currency = Column(object_dtype)
    SecType = Column(object_dtype)
    Etf = Column(bool_dtype)
    Timezone = Column(object_dtype)
    Name = Column(object_dtype)
    PriceMagnifier = Column(float64_dtype)
    Multiplier = Column(float64_dtype)
    Delisted = Column(bool_dtype)
    DateDelisted = Column(datetime64ns_dtype, missing_value=NaTD)
    LastTradeDate = Column(datetime64ns_dtype, missing_value=NaTD)
    RolloverDate = Column(datetime64ns_dtype, missing_value=NaTD)
    alpaca_AssetId = Column(object_dtype)
    alpaca_AssetClass = Column(object_dtype)
    alpaca_Exchange = Column(object_dtype)
    alpaca_Symbol = Column(object_dtype)
    alpaca_Name = Column(object_dtype)
    alpaca_Status = Column(object_dtype)
    alpaca_Tradable = Column(float64_dtype)
    alpaca_Marginable = Column(float64_dtype)
    alpaca_Shortable = Column(float64_dtype)
    alpaca_EasyToBorrow = Column(float64_dtype)
    edi_SecId = Column(float64_dtype)
    edi_Currency = Column(object_dtype)
    edi_PrimaryMic = Column(object_dtype)
    edi_Mic = Column(object_dtype)
    edi_MicSegment = Column(object_dtype)
    edi_MicTimezone = Column(object_dtype)
    edi_IsPrimaryListing = Column(float64_dtype)
    edi_LocalSymbol = Column(object_dtype)
    edi_IssuerId = Column(float64_dtype)
    edi_IssuerName = Column(object_dtype)
    edi_IsoCountryInc = Column(object_dtype)
    edi_CountryInc = Column(object_dtype)
    edi_IsoCountryListed = Column(object_dtype)
    edi_CountryListed = Column(object_dtype)
    edi_SicCode = Column(object_dtype)
    edi_Sic = Column(object_dtype)
    edi_SicIndustryGroup = Column(object_dtype)
    edi_SicMajorGroup = Column(object_dtype)
    edi_SicDivision = Column(object_dtype)
    edi_Cik = Column(object_dtype)
    edi_Industry = Column(object_dtype)
    edi_SecTypeCode = Column(object_dtype)
    edi_SecTypeDesc = Column(object_dtype)
    edi_SecurityDesc = Column(object_dtype)
    edi_PreferredName = Column(object_dtype)
    edi_GlobalListingStatus = Column(object_dtype)
    edi_ExchangeListingStatus = Column(object_dtype)
    edi_DateDelisted = Column(datetime64ns_dtype, missing_value=NaTD)
    edi_StructureCode = Column(object_dtype)
    edi_StructureDesc = Column(object_dtype)
    edi_RecordModified = Column(object_dtype)
    edi_RecordCreated = Column(object_dtype)
    edi_FirstPriceDate = Column(datetime64ns_dtype, missing_value=NaTD)
    edi_LastPriceDate = Column(datetime64ns_dtype, missing_value=NaTD)
    ibkr_ConId = Column(float64_dtype)
    ibkr_Symbol = Column(object_dtype)
    ibkr_SecType = Column(object_dtype)
    ibkr_Etf = Column(bool_dtype)
    ibkr_PrimaryExchange = Column(object_dtype)
    ibkr_Currency = Column(object_dtype)
    ibkr_LocalSymbol = Column(object_dtype)
    ibkr_TradingClass = Column(object_dtype)
    ibkr_MarketName = Column(object_dtype)
    ibkr_LongName = Column(object_dtype)
    ibkr_Timezone = Column(object_dtype)
    ibkr_ValidExchanges = Column(object_dtype)
    ibkr_AggGroup = Column(float64_dtype)
    ibkr_Sector = Column(object_dtype)
    ibkr_Industry = Column(object_dtype)
    ibkr_Category = Column(object_dtype)
    ibkr_MinTick = Column(float64_dtype)
    ibkr_PriceMagnifier = Column(float64_dtype)
    ibkr_MdSizeMultiplier = Column(float64_dtype)
    ibkr_LastTradeDate = Column(datetime64ns_dtype, missing_value=NaTD)
    ibkr_ContractMonth = Column(float64_dtype)
    ibkr_RealExpirationDate = Column(datetime64ns_dtype, missing_value=NaTD)
    ibkr_Multiplier = Column(float64_dtype)
    ibkr_UnderConId = Column(float64_dtype)
    ibkr_UnderSymbol = Column(object_dtype)
    ibkr_UnderSecType = Column(object_dtype)
    ibkr_MarketRuleIds = Column(object_dtype)
    ibkr_Strike = Column(float64_dtype)
    ibkr_Right = Column(object_dtype)
    ibkr_Isin = Column(object_dtype)
    ibkr_Cusip = Column(object_dtype)
    ibkr_EvRule = Column(object_dtype)
    ibkr_EvMultiplier = Column(float64_dtype)
    ibkr_Delisted = Column(bool_dtype)
    ibkr_DateDelisted = Column(datetime64ns_dtype, missing_value=NaTD)
    sharadar_Permaticker = Column(float64_dtype)
    sharadar_Ticker = Column(object_dtype)
    sharadar_Name = Column(object_dtype)
    sharadar_Exchange = Column(object_dtype)
    sharadar_Delisted = Column(bool_dtype)
    sharadar_DateDelisted = Column(datetime64ns_dtype, missing_value=NaTD)
    sharadar_Category = Column(object_dtype)
    sharadar_Cusips = Column(object_dtype)
    sharadar_SicCode = Column(object_dtype)
    sharadar_SicSector = Column(object_dtype)
    sharadar_SicIndustry = Column(object_dtype)
    sharadar_FamaSector = Column(object_dtype)
    sharadar_FamaIndustry = Column(object_dtype)
    sharadar_Sector = Column(object_dtype)
    sharadar_Industry = Column(object_dtype)
    sharadar_ScaleMarketCap = Column(object_dtype)
    sharadar_ScaleRevenue = Column(object_dtype)
    sharadar_RelatedTickers = Column(object_dtype)
    sharadar_Currency = Column(object_dtype)
    sharadar_Location = Column(object_dtype)
    sharadar_CountryListed = Column(object_dtype)
    sharadar_LastUpdated = Column(datetime64ns_dtype, missing_value=NaTD)
    sharadar_FirstAdded = Column(datetime64ns_dtype, missing_value=NaTD)
    sharadar_FirstPriceDate = Column(datetime64ns_dtype, missing_value=NaTD)
    sharadar_LastPriceDate = Column(datetime64ns_dtype, missing_value=NaTD)
    sharadar_FirstQuarter = Column(datetime64ns_dtype, missing_value=NaTD)
    sharadar_LastQuarter = Column(datetime64ns_dtype, missing_value=NaTD)
    sharadar_SecFilings = Column(object_dtype)
    sharadar_CompanySite = Column(object_dtype)
    usstock_Mic = Column(object_dtype)
    usstock_Symbol = Column(object_dtype)
    usstock_Name = Column(object_dtype)
    usstock_Sector = Column(object_dtype),
    usstock_Industry = Column(object_dtype),
    usstock_SicCode = Column(object_dtype)
    usstock_Sic = Column(object_dtype)
    usstock_SicIndustryGroup = Column(object_dtype)
    usstock_SicMajorGroup = Column(object_dtype)
    usstock_SicDivision = Column(object_dtype)
    usstock_SecurityType = Column(object_dtype)
    usstock_SecurityType2 = Column(object_dtype)
    usstock_CIK = Column(object_dtype),
    usstock_PrimaryShareSid = Column(object_dtype),
    usstock_DateDelisted = Column(datetime64ns_dtype, missing_value=NaTD)
    usstock_FirstPriceDate = Column(datetime64ns_dtype, missing_value=NaTD)
    usstock_LastPriceDate = Column(datetime64ns_dtype, missing_value=NaTD)
    figi_Figi = Column(object_dtype)
    figi_Name = Column(object_dtype)
    figi_Ticker = Column(object_dtype)
    figi_CompositeFigi = Column(object_dtype)
    figi_ExchCode = Column(object_dtype)
    figi_UniqueId = Column(object_dtype)
    figi_SecurityType = Column(object_dtype)
    figi_MarketSector = Column(object_dtype)
    figi_ShareClassFigi = Column(object_dtype)
    figi_UniqueIdFutOpt = Column(object_dtype)
    figi_SecurityType2 = Column(object_dtype)
    figi_SecurityDescription = Column(object_dtype)
    figi_IsComposite = Column(bool_dtype)
