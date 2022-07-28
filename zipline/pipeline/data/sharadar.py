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
    datetime64ns_dtype,
    NaTD)
from zipline.pipeline.data import Column, DataSet, DataSetFamily
from zipline.pipeline.domain import US_EQUITIES

class SP500(DataSet):
    """
    Dataset representing membership in the S&P 500.

    Attributes
    ----------
    in_sp500 : bool
        whether the security is a member of S&P 500

    Examples
    --------

    >>> in_sp500 = sharadar.SP500.in_sp500.latest    # doctest: +SKIP
    """
    domain = US_EQUITIES
    in_sp500 = Column(bool_dtype)

# legacy alias
SharadarSP500 = SP500

class Fundamentals(DataSetFamily):
    """
    DataSetFamily representing Sharadar fundamentals. In order to use
    the data in a pipeline, it must first be sliced to generate a regular
    pipeline DataSet.

    Fundamentals can be sliced along two dimensions:

    - `dimension` : the choices are ARQ, ARY, ART, MRQ, MRY, MRT, where
      AR=As Reported, MR=Most Recent Reported, Q=Quarterly, Y=Annual, and
      T=Trailing Twelve Month.

    - `period_offset` : which fiscal period to return data for. If period_offset
      is 0, returns the most recent point-in-time fundamentals. If period_offset
      is -1, returns fundamentals for the prior fiscal period; if -2, two fiscal
      periods ago, etc. For quarterly and trailing-twelve-month dimensions,
      previous period means previous quarter, while for annual dimensions,
      previous period means previous year. Value should be a negative integer or
      0.

    Attributes
    ----------
    ACCOCI : float
        Accumulated Other Comprehensive Income - [Balance Sheet] A component
        of [Equity] representing the accumulated change in equity from
        transactions and other events and circumstances from non-owner
        sources; net of tax effect; at period end. Includes foreign currency
        translation items; certain pension adjustments; unrealized gains and
        losses on certain investments in debt and equity securities.

    ASSETS : float
        Total Assets - [Balance Sheet] Sum of the carrying amounts as of the
        balance sheet date of all assets that are recognized. Major components
        are [CashnEq]; [Investments];[Intangibles]; [PPNENet];[TaxAssets] and
        [Receivables].

    ASSETSAVG : float
        Average Assets - [Metrics] Average asset value for the period used in
        calculation of [ROE] and [ROA]; derived from [Assets].

    ASSETSC : float
        Current Assets - [Balance Sheet] The current portion of [Assets];
        reported if a company operates a classified balance sheet that
        segments current and non-current assets.

    ASSETSNC : float
        Assets Non-Current - [Balance Sheet] Amount of non-current assets; for
        companies that operate a classified balance sheet. Calculated as the
        different between Total Assets [Assets] and Current Assets [AssetsC].

    ASSETTURNOVER : float
        Asset Turnover - [Metrics] Asset turnover is a measure of a firms
        operating efficiency; calculated by dividing [Revenue] by [AssetsAVG].
        Often a component of DuPont ROE analysis.

    BVPS : float
        Book Value per Share - [Metrics] Measures the ratio between [Equity]
        and [SharesWA] as adjusted by [ShareFactor].

    CALENDARDATE : datetime64D
        Calendar Date - [Entity] The Calendar Date represents the normalized
        [ReportPeriod]. This provides a common date to query for which is
        necessary due to irregularity in report periods across companies. For
        example; if the report period is "2015-09-26"; the calendar date will be
        "2015-09-30" for quarterly and trailing-twelve-month dimensions
        (ARQ;MRQ;ART;MRT); and "2015-12-31" for annual dimensions (ARY;MRY).
        We also employ offsets in order to maximise comparability of the period
        across companies. For example consider two companies: one with a quarter
        ending on 2018-07-24; and the other with a quarter ending on 2018-06-28.
        A naive normalization process would assign these to differing calendar
        quarters of 2018-09-30 and 2018-06-30 respectively. However, we assign
        these both to the 2018-06-30 calendar quarter because this maximises the
        overlap in the report periods in question and therefore the comparability
        of this period.

    CAPEX : float
        Capital Expenditure - [Cash Flow Statement] A component of [NCFI]
        representing the net cash inflow (outflow) associated with the
        acquisition & disposal of long-lived; physical & intangible assets
        that are used in the normal conduct of business to produce goods and
        services and are not intended for resale. Includes cash
        inflows/outflows to pay for construction of self-constructed assets &
        software.

    CASHNEQ : float
        Cash and Equivalents - [Balance Sheet] A component of [Assets]
        representing the amount of currency on hand as well as demand deposits
        with banks or financial institutions.

    CASHNEQUSD : float
        Cash and Equivalents (USD) - [Balance Sheet] [CashnEq] in USD;
        converted by [FXUSD].

    CONSOLINC : float
        Consolidated Income - [Income Statement] The portion of profit or loss
        for the period; net of income taxes; which is attributable to the
        consolidated entity; before the deduction of [NetIncNCI].

    COR : float
        Cost of Revenue - [Income Statement] The aggregate cost of goods
        produced and sold and services rendered during the reporting period.

    CURRENTRATIO : float
        Current Ratio - [Metrics] The ratio between [AssetsC] and
        [LiabilitiesC]; for companies that operate a classified balance sheet.

    DE : float
        Debt to Equity Ratio - [Metrics] Measures the ratio between
        [Liabilities] and [Equity].

    DEBT : float
        Total Debt - [Balance Sheet] A component of [Liabilities] representing
        the total amount of current and non-current debt owed. Includes
        secured and unsecured bonds issued; commercial paper; notes payable;
        credit facilities; lines of credit; capital lease obligations; and
        convertible notes.

    DEBTC : float
        Debt Current - [Balance Sheet] The current portion of [Debt]; reported
        if the company operates a classified balance sheet that segments
        current and non-current liabilities.

    DEBTNC : float
        Debt Non-Current - [Balance Sheet] The non-current portion of [Debt]
        reported if the company operates a classified balance sheet that
        segments current and non-current liabilities.

    DEBTUSD : float
        Total Debt (USD) - [Balance Sheet] [Debt] in USD; converted by
        [FXUSD].

    DEFERREDREV : float
        Deferred Revenue - [Balance Sheet] A component of [Liabilities]
        representing the carrying amount of consideration received or
        receivable on potential earnings that were not recognized as revenue;
        including sales; license fees; and royalties; but excluding interest
        income.

    DEPAMOR : float
        Depreciation Amortization & Accretion - [Cash Flow Statement] A
        component of operating cash flow representing the aggregate net amount
        of depreciation; amortization; and accretion recognized during an
        accounting period. As a non-cash item; the net amount is added back to
        net income when calculating cash provided by or used in operations
        using the indirect method.

    DEPOSITS : float
        Deposit Liabilities - [Balance Sheet] A component of [Liabilities]
        representing the total of all deposit liabilities held; including
        foreign and domestic; interest and noninterest bearing. May include
        demand deposits; saving deposits; Negotiable Order of Withdrawal and
        time deposits among others.

    DIVYIELD : float
        Dividend Yield - [Metrics] Dividend Yield measures the ratio between a
        company's [DPS] and its [Price].

    DPS : float
        Dividends per Basic Common Share - [Income Statement] Aggregate
        dividends declared during the period for each split-adjusted share of
        common stock outstanding. Includes spinoffs where identified.

    EBIT : float
        Earning Before Interest & Taxes (EBIT) - [Income Statement] Earnings
        Before Interest and Tax is calculated by adding [TaxExp] and [IntExp]
        back to [NetInc].

    EBITDA : float
        Earnings Before Interest Taxes & Depreciation Amortization (EBITDA) -
        [Metrics] EBITDA is a non-GAAP accounting metric that is widely used
        when assessing the performance of companies; calculated by adding
        [DepAmor] back to [EBIT].

    EBITDAMARGIN : float
        EBITDA Margin - [Metrics] Measures the ratio between a company's
        [EBITDA] and [Revenue].

    EBITDAUSD : float
        Earnings Before Interest Taxes & Depreciation Amortization (USD) -
        [Metrics] [EBITDA] in USD; converted by [FXUSD].

    EBITUSD : float
        Earning Before Interest & Taxes (USD) - [Income Statement] [EBIT] in
        USD; converted by [FXUSD].

    EBT : float
        Earnings before Tax - [Metrics] Earnings Before Tax is calculated by
        adding [TaxExp] back to [NetInc].

    EPS : float
        Earnings per Basic Share - [Income Statement] Earnings per share as
        calculated and reported by the company. Approximates to the amount of
        [NetIncCmn] for the period per each [SharesWA] after adjusting for
        [ShareFactor].

    EPSDIL : float
        Earnings per Diluted Share - [Income Statement] Earnings per diluted
        share as calculated and reported by the company. Approximates to the
        amount of [NetIncCmn] for the period per each [SharesWADil] after
        adjusting for [ShareFactor]..

    EPSUSD : float
        Earnings per Basic Share (USD) - [Income Statement] [EPS] in USD;
        converted by [FXUSD].

    EQUITY : float
        Shareholders Equity - [Balance Sheet] A principal component of the
        balance sheet; in addition to [Liabilities] and [Assets]; that
        represents the total of all stockholders' equity (deficit) items; net
        of receivables from officers; directors; owners; and affiliates of the
        entity which are attributable to the parent.

    EQUITYAVG : float
        Average Equity - [Metrics] Average equity value for the period used in
        calculation of [ROE]; derived from [Equity].

    EQUITYUSD : float
        Shareholders Equity (USD) - [Balance Sheet] [Equity] in USD; converted
        by [FXUSD].

    EV : float
        Enterprise Value - [Metrics] Enterprise value is a measure of the
        value of a business as a whole; calculated as [MarketCap] plus
        [DebtUSD] minus [CashnEqUSD].

    EVEBIT : float
        Enterprise Value over EBIT - [Metrics] Measures the ratio between [EV]
        and [EBITUSD].

    EVEBITDA : float
        Enterprise Value over EBITDA - [Metrics] Measures the ratio between
        [EV] and [EBITDAUSD].

    FCF : float
        Free Cash Flow - [Metrics] Free Cash Flow is a measure of financial
        performance calculated as [NCFO] minus [CapEx].

    FCFPS : float
        Free Cash Flow per Share - [Metrics] Free Cash Flow per Share is a
        valuation metric calculated by dividing [FCF] by [SharesWA] and
        [ShareFactor].

    FXUSD : float
        Foreign Currency to USD Exchange Rate - [Metrics] The exchange rate
        used for the conversion of foreign currency to USD for non-US
        companies that do not report in USD.

    GP : float
        Gross Profit - [Income Statement] Aggregate revenue [Revenue] less
        cost of revenue [CoR] directly attributable to the revenue generation
        activity.

    GROSSMARGIN : float
        Gross Margin - [Metrics] Gross Margin measures the ratio between a
        company's [GP] and [Revenue].

    INTANGIBLES : float
        Goodwill and Intangible Assets - [Balance Sheet] A component of
        [Assets] representing the carrying amounts of all intangible assets
        and goodwill as of the balance sheet date; net of accumulated
        amortization and impairment charges.

    INTEXP : float
        Interest Expense - [Income Statement] Amount of the cost of borrowed
        funds accounted for as interest expense.

    INVCAP : float
        Invested Capital - [Metrics] Invested capital is an input into the
        calculation of [ROIC]; and is calculated as: [Debt] plus [Assets]
        minus [Intangibles] minus [CashnEq] minus [LiabilitiesC]. Please note
        this calculation method is subject to change.

    INVCAPAVG : float
        Invested Capital Average - [Metrics] Average invested capital value
        for the period used in the calculation of [ROIC]; and derived from
        [InvCap]. Invested capital is an input into the calculation of [ROIC];
        and is calculated as: [Debt] plus [Assets] minus [Intangibles] minus
        [CashnEq] minus [LiabilitiesC]. Please note this calculation method is
        subject to change.

    INVENTORY : float
        Inventory - [Balance Sheet] A component of [Assets] representing the
        amount after valuation and reserves of inventory expected to be sold;
        or consumed within one year or operating cycle; if longer.

    INVESTMENTS : float
        Investments - [Balance Sheet] A component of [Assets] representing the
        total amount of marketable and non-marketable securties; loans
        receivable and other invested assets.

    INVESTMENTSC : float
        Investments Current - [Balance Sheet] The current portion of
        [Investments]; reported if the company operates a classified balance
        sheet that segments current and non-current assets.

    INVESTMENTSNC : float
        Investments Non-Current - [Balance Sheet] The non-current portion of
        [Investments]; reported if the company operates a classified balance
        sheet that segments current and non-current assets.

    LIABILITIES : float
        Total Liabilities - [Balance Sheet] Sum of the carrying amounts as of
        the balance sheet date of all liabilities that are recognized.
        Principal components are [Debt]; [DeferredRev]; [Payables];[Deposits];
        and [TaxLiabilities].

    LIABILITIESC : float
        Current Liabilities - [Balance Sheet] The current portion of
        [Liabilities]; reported if the company operates a classified balance
        sheet that segments current and non-current liabilities.

    LIABILITIESNC : float
        Liabilities Non-Current - [Balance Sheet] The non-current portion of
        [Liabilities]; reported if the company operates a classified balance
        sheet that segments current and non-current liabilities.

    MARKETCAP : float
        Market Capitalization - [Metrics] Represents the product of
        [SharesBas]; [Price] and [ShareFactor].

    NCF : float
        Net Cash Flow / Change in Cash & Cash Equivalents - [Cash Flow
        Statement] Principal component of the cash flow statement representing
        the amount of increase (decrease) in cash and cash equivalents.
        Includes [NCFO]; investing [NCFI] and financing [NCFF] for continuing
        and discontinued operations; and the effect of exchange rate changes
        on cash [NCFX].

    NCFBUS : float
        Net Cash Flow - Business Acquisitions and Disposals - [Cash Flow
        Statement] A component of [NCFI] representing the net cash inflow
        (outflow) associated with the acquisition & disposal of businesses;
        joint-ventures; affiliates; and other named investments.

    NCFCOMMON : float
        Issuance (Purchase) of Equity Shares - [Cash Flow Statement] A
        component of [NCFF] representing the net cash inflow (outflow) from
        common equity changes. Includes additional capital contributions from
        share issuances and exercise of stock options; and outflow from share
        repurchases.

    NCFDEBT : float
        Issuance (Repayment) of Debt Securities  - [Cash Flow Statement] A
        component of [NCFF] representing the net cash inflow (outflow) from
        issuance (repayment) of debt securities.

    NCFDIV : float
        Payment of Dividends & Other Cash Distributions    - [Cash Flow
        Statement] A component of [NCFF] representing dividends and dividend
        equivalents paid on common stock and restricted stock units.

    NCFF : float
        Net Cash Flow from Financing - [Cash Flow Statement] A component of
        [NCF] representing the amount of cash inflow (outflow) from financing
        activities; from continuing and discontinued operations. Principal
        components of financing cash flow are: issuance (purchase) of equity
        shares; issuance (repayment) of debt securities; and payment of
        dividends & other cash distributions.

    NCFI : float
        Net Cash Flow from Investing - [Cash Flow Statement] A component of
        [NCF] representing the amount of cash inflow (outflow) from investing
        activities; from continuing and discontinued operations. Principal
        components of investing cash flow are: capital (expenditure) disposal
        of equipment [CapEx]; business (acquisitions) disposition [NCFBus] and
        investment (acquisition) disposal [NCFInv].

    NCFINV : float
        Net Cash Flow - Investment Acquisitions and Disposals - [Cash Flow
        Statement] A component of [NCFI] representing the net cash inflow
        (outflow) associated with the acquisition & disposal of investments;
        including marketable securities and loan originations.

    NCFO : float
        Net Cash Flow from Operations - [Cash Flow Statement] A component of
        [NCF] representing the amount of cash inflow (outflow) from operating
        activities; from continuing and discontinued operations.

    NCFX : float
        Effect of Exchange Rate Changes on Cash  - [Cash Flow Statement] A
        component of Net Cash Flow [NCF] representing the amount of increase
        (decrease) from the effect of exchange rate changes on cash and cash
        equivalent balances held in foreign currencies.

    NETINC : float
        Net Income - [Income Statement] The portion of profit or loss for the
        period; net of income taxes; which is attributable to the parent after
        the deduction of [NetIncNCI] from [ConsolInc]; and before the
        deduction of [PrefDivIS].

    NETINCCMN : float
        Net Income Common Stock - [Income Statement] The amount of net income
        (loss) for the period due to common shareholders. Typically differs
        from [NetInc] to the parent entity due to the deduction of
        [PrefDivIS].

    NETINCCMNUSD : float
        Net Income Common Stock (USD) - [Income Statement] [NetIncCmn] in USD;
        converted by [FXUSD].

    NETINCDIS : float
        Net Loss Income from Discontinued Operations - [Income Statement]
        Amount of loss (income) from a disposal group; net of income tax;
        reported as a separate component of income.

    NETINCNCI : float
        Net Income to Non-Controlling Interests - [Income Statement] The
        portion of income which is attributable to non-controlling interest
        shareholders; subtracted from [ConsolInc] in order to obtain [NetInc].

    NETMARGIN : float
        Profit Margin - [Metrics] Measures the ratio between a company's
        [NetIncCmn] and [Revenue].

    OPEX : float
        Operating Expenses - [Income Statement] Operating expenses represents
        the total expenditure on [SGnA]; [RnD] and other operating expense
        items; it excludes [CoR].

    OPINC : float
        Operating Income - [Income Statement] Operating income is a measure of
        financial performance before the deduction of [IntExp]; [TaxExp] and
        other Non-Operating items. It is calculated as [GP] minus [OpEx].

    PAYABLES : float
        Trade and Non-Trade Payables - [Balance Sheet] A component of
        [Liabilities] representing trade and non-trade payables.

    PAYOUTRATIO : float
        Payout Ratio - [Metrics] The percentage of earnings paid as dividends
        to common stockholders. Calculated by dividing [DPS] by [EPSUSD].

    PB : float
        Price to Book Value - [Metrics] Measures the ratio between [MarketCap]
        and [EquityUSD].

    PE : float
        Price Earnings (Damodaran Method) - [Metrics] Measures the ratio
        between [MarketCap] and [NetIncCmnUSD]

    PE1 : float
        Price to Earnings Ratio - [Metrics] An alternative to [PE]
        representing the ratio between [Price] and [EPSUSD].

    PPNENET : float
        Property Plant & Equipment Net - [Balance Sheet] A component of
        [Assets] representing the amount after accumulated depreciation;
        depletion and amortization of physical assets used in the normal
        conduct of business to produce goods and services and not intended for
        resale.

    PREFDIVIS : float
        Preferred Dividends Income Statement Impact - [Income Statement]
        Income statement item reflecting dividend payments to preferred
        stockholders. Subtracted from Net Income to Parent [NetInc] to obtain
        Net Income to Common Stockholders [NetIncCmn].

    PRICE : float
        Share Price (Adjusted Close) - [Entity] The price per common share
        adjusted for stock splits but not adjusted for dividends; used in the
        computation of [PE1]; [PS1]; [DivYield] and [SPS].

    PS : float
        Price Sales (Damodaran Method) - [Metrics] Measures the ratio between
        [MarketCap] and [RevenueUSD].

    PS1 : float
        Price to Sales Ratio - [Metrics] An alternative calculation method to
        [PS]; that measures the ratio between a company's [Price] and it's
        [SPS].

    RECEIVABLES : float
        Trade and Non-Trade Receivables - [Balance Sheet] A component of
        [Assets] representing trade and non-trade receivables.

    REPORTPERIOD : datetime64D
        Report Period - [Entity] The Report Period represents the end date of
        the fiscal period.

    RETEARN : float
        Accumulated Retained Earnings (Deficit) - [Balance Sheet] A component
        of [Equity] representing the cumulative amount of the entities
        undistributed earnings or deficit. May only be reported annually by
        certain companies; rather than quarterly.

    REVENUE : float
        Revenues - [Income Statement] Amount of Revenue recognized from goods
        sold; services rendered; insurance premiums; or other activities that
        constitute an earning process. Interest income for financial
        institutions is reported net of interest expense and provision for
        credit losses.

    REVENUEUSD : float
        Revenues (USD) - [Income Statement] [Revenue] in USD; converted by
        [FXUSD].

    RND : float
        Research and Development Expense - [Income Statement] A component of
        [OpEx] representing the aggregate costs incurred in a planned search
        or critical investigation aimed at discovery of new knowledge with the
        hope that such knowledge will be useful in developing a new product or
        service.

    ROA : float
        Return on Average Assets - [Metrics] Return on assets measures how
        profitable a company is [NetIncCmn] relative to its total assets
        [AssetsAvg].

    ROE : float
        Return on Average Equity - [Metrics] Return on equity measures a
        corporation's profitability by calculating the amount of [NetIncCmn]
        returned as a percentage of [EquityAvg].

    ROIC : float
        Return on Invested Capital - [Metrics] Return on Invested Capital is
        ratio estimated by dividing [EBIT] by [InvCapAvg]. [InvCap] is
        calculated as: [Debt] plus [Assets] minus [Intangibles] minus
        [CashnEq] minus [LiabilitiesC]. Please note this calculation method is
        subject to change.

    ROS : float
        Return on Sales - [Metrics] Return on Sales is a ratio to evaluate a
        company's operational efficiency; calculated by dividing [EBIT] by
        [Revenue]. ROS is often a component of DuPont ROE analysis.

    SBCOMP : float
        Share Based Compensation - [Cash Flow Statement] A component of [NCFO]
        representing the total amount of noncash; equity-based employee
        remuneration. This may include the value of stock or unit options;
        amortization of restricted stock or units; and adjustment for
        officers' compensation. As noncash; this element is an add back when
        calculating net cash generated by operating activities using the
        indirect method.

    SGNA : float
        Selling General and Administrative Expense - [Income Statement] A
        component of [OpEx] representing the aggregate total costs related to
        selling a firm's product and services; as well as all other general
        and administrative expenses. Direct selling expenses (for example;
        credit; warranty; and advertising) are expenses that can be directly
        linked to the sale of specific products. Indirect selling expenses are
        expenses that cannot be directly linked to the sale of specific
        products; for example telephone expenses; Internet; and postal
        charges. General and administrative expenses include salaries of non-
        sales personnel; rent; utilities; communication; etc.

    SHAREFACTOR : float
        Share Factor - [Entity] Share factor is a multiplicant in the
        calculation of [MarketCap] and is used to adjust for: American
        Depository Receipts (ADRs) that represent more or less than 1
        underlying share; and; companies which have different earnings share
        for different share classes (eg Berkshire Hathaway - BRKB).

    SHARESBAS : float
        Shares (Basic) - [Entity] The number of shares or other units
        outstanding of the entity's capital or common stock or other ownership
        interests; as stated on the cover of related periodic report
        (10-K/10-Q); after adjustment for stock splits.

    SHARESWA : float
        Weighted Average Shares - [Income Statement] The weighted average
        number of shares or units issued and outstanding that are used by the
        company to calculate [EPS]; determined based on the timing of issuance
        of shares or units in the period.

    SHARESWADIL : float
        Weighted Average Shares Diluted - [Income Statement] The weighted
        average number of shares or units issued and outstanding that are used
        by the company to calculate [EPSDil]; determined based on the timing
        of issuance of shares or units in the period.

    SPS : float
        Sales per Share - [Metrics] Sales per Share measures the ratio between
        [RevenueUSD] and [SharesWA] as adjusted by [ShareFactor].

    TANGIBLES : float
        Tangible Asset Value - [Metrics] The value of tangibles assets
        calculated as the difference between [Assets] and [Intangibles].

    TAXASSETS : float
        Tax Assets - [Balance Sheet] A component of [Assets] representing tax
        assets and receivables.

    TAXEXP : float
        Income Tax Expense - [Income Statement] Amount of current income tax
        expense (benefit) and deferred income tax expense (benefit) pertaining
        to continuing operations.

    TAXLIABILITIES : float
        Tax Liabilities - [Balance Sheet] A component of [Liabilities]
        representing outstanding tax liabilities.

    TBVPS : float
        Tangible Assets Book Value per Share - [Metrics] Measures the ratio
        between [Tangibles] and [SharesWA] as adjusted by [ShareFactor].

    WORKINGCAPITAL : float
        Working Capital - [Metrics] Working capital measures the difference
        between [AssetsC] and [LiabilitiesC].

    Examples
    --------
    Select stocks with low enterprise multiples using quarterly fundamentals:

    >>> have_low_enterprise_multiples = sharadar.Fundamentals.slice(
        dimension='ARQ', period_offset=0).EVEBITDA.latest.percentile_between(0, 20)    # doctest: +SKIP

    Create a boolean filter indicating whether assets increased in the current
    year relative to the prior year:

    >>> current_year_fundamentals = sharadar.Fundamentals.slice(
            dimension='ARY',
            period_offset=0)
    >>> previous_year_fundamentals = sharadar.Fundamentals.slice(
            dimension='ARY',
            period_offset=-1)
    >>> total_assets = current_year_fundamentals.ASSETS.latest
    >>> previous_total_assets = previous_year_fundamentals.ASSETS.latest
    >>> assets_increased = total_assets > previous_total_assets
    """
    extra_dims = [
        ('dimension', {'ARQ', 'ART', 'ARY', 'MRQ', 'MRT', 'MRY'}),
        ('period_offset', set(range(-127,1))),
    ]

    domain = US_EQUITIES

    REVENUE = Column(float64_dtype) # Revenues - [Income Statement] Amount of Revenue recognized from goods sold; services rendered; insurance premiums; or other activities that constitute an earning process. Interest income for financial institutions is reported net of interest expense and provision for credit losses.
    COR = Column(float64_dtype) # Cost of Revenue - [Income Statement] The aggregate cost of goods produced and sold and services rendered during the reporting period.
    SGNA = Column(float64_dtype) # Selling General and Administrative Expense - [Income Statement] A component of [OpEx] representing the aggregate total costs related to selling a firm's product and services; as well as all other general and administrative expenses. Direct selling expenses (for example; credit; warranty; and advertising) are expenses that can be directly linked to the sale of specific products. Indirect selling expenses are expenses that cannot be directly linked to the sale of specific products; for example telephone expenses; Internet; and postal charges. General and administrative expenses include salaries of non-sales personnel; rent; utilities; communication; etc.
    RND = Column(float64_dtype) # Research and Development Expense - [Income Statement] A component of [OpEx] representing the aggregate costs incurred in a planned search or critical investigation aimed at discovery of new knowledge with the hope that such knowledge will be useful in developing a new product or service.
    OPEX = Column(float64_dtype) # Operating Expenses - [Income Statement] Operating expenses represents the total expenditure on [SGnA]; [RnD] and other operating expense items; it excludes [CoR].
    INTEXP = Column(float64_dtype) # Interest Expense - [Income Statement] Amount of the cost of borrowed funds accounted for as interest expense.
    TAXEXP = Column(float64_dtype) # Income Tax Expense - [Income Statement] Amount of current income tax expense (benefit) and deferred income tax expense (benefit) pertaining to continuing operations.
    NETINCDIS = Column(float64_dtype) # Net Loss Income from Discontinued Operations - [Income Statement] Amount of loss (income) from a disposal group; net of income tax; reported as a separate component of income.
    CONSOLINC = Column(float64_dtype) # Consolidated Income - [Income Statement] The portion of profit or loss for the period; net of income taxes; which is attributable to the consolidated entity; before the deduction of [NetIncNCI].
    NETINCNCI = Column(float64_dtype) # Net Income to Non-Controlling Interests - [Income Statement] The portion of income which is attributable to non-controlling interest shareholders; subtracted from [ConsolInc] in order to obtain [NetInc].
    NETINC = Column(float64_dtype) # Net Income - [Income Statement] The portion of profit or loss for the period; net of income taxes; which is attributable to the parent after the deduction of [NetIncNCI] from [ConsolInc]; and before the deduction of [PrefDivIS].
    PREFDIVIS = Column(float64_dtype) # Preferred Dividends Income Statement Impact - [Income Statement] Income statement item reflecting dividend payments to preferred stockholders. Subtracted from Net Income to Parent [NetInc] to obtain Net Income to Common Stockholders [NetIncCmn].
    NETINCCMN = Column(float64_dtype) # Net Income Common Stock - [Income Statement] The amount of net income (loss) for the period due to common shareholders. Typically differs from [NetInc] to the parent entity due to the deduction of [PrefDivIS].
    EPS = Column(float64_dtype) # Earnings per Basic Share - [Income Statement] Earnings per share as calculated and reported by the company. Approximates to the amount of [NetIncCmn] for the period per each [SharesWA] after adjusting for [ShareFactor].
    EPSDIL = Column(float64_dtype) # Earnings per Diluted Share - [Income Statement] Earnings per diluted share as calculated and reported by the company. Approximates to the amount of [NetIncCmn] for the period per each [SharesWADil] after adjusting for [ShareFactor]..
    SHARESWA = Column(float64_dtype) # Weighted Average Shares - [Income Statement] The weighted average number of shares or units issued and outstanding that are used by the company to calculate [EPS]; determined based on the timing of issuance of shares or units in the period.
    SHARESWADIL = Column(float64_dtype) # Weighted Average Shares Diluted - [Income Statement] The weighted average number of shares or units issued and outstanding that are used by the company to calculate [EPSDil]; determined based on the timing of issuance of shares or units in the period.
    CAPEX = Column(float64_dtype) # Capital Expenditure - [Cash Flow Statement] A component of [NCFI] representing the net cash inflow (outflow) associated with the acquisition & disposal of long-lived; physical & intangible assets that are used in the normal conduct of business to produce goods and services and are not intended for resale. Includes cash inflows/outflows to pay for construction of self-constructed assets & software.
    NCFBUS = Column(float64_dtype) # Net Cash Flow - Business Acquisitions and Disposals - [Cash Flow Statement] A component of [NCFI] representing the net cash inflow (outflow) associated with the acquisition & disposal of businesses; joint-ventures; affiliates; and other named investments.
    NCFINV = Column(float64_dtype) # Net Cash Flow - Investment Acquisitions and Disposals - [Cash Flow Statement] A component of [NCFI] representing the net cash inflow (outflow) associated with the acquisition & disposal of investments; including marketable securities and loan originations.
    NCFF = Column(float64_dtype) # Net Cash Flow from Financing - [Cash Flow Statement] A component of [NCF] representing the amount of cash inflow (outflow) from financing activities; from continuing and discontinued operations. Principal components of financing cash flow are: issuance (purchase) of equity shares; issuance (repayment) of debt securities; and payment of dividends & other cash distributions.
    NCFDEBT = Column(float64_dtype) # Issuance (Repayment) of Debt Securities  - [Cash Flow Statement] A component of [NCFF] representing the net cash inflow (outflow) from issuance (repayment) of debt securities.
    NCFCOMMON = Column(float64_dtype) # Issuance (Purchase) of Equity Shares - [Cash Flow Statement] A component of [NCFF] representing the net cash inflow (outflow) from common equity changes. Includes additional capital contributions from share issuances and exercise of stock options; and outflow from share repurchases.
    NCFDIV = Column(float64_dtype) # Payment of Dividends & Other Cash Distributions    - [Cash Flow Statement] A component of [NCFF] representing dividends and dividend equivalents paid on common stock and restricted stock units.
    NCFI = Column(float64_dtype) # Net Cash Flow from Investing - [Cash Flow Statement] A component of [NCF] representing the amount of cash inflow (outflow) from investing activities; from continuing and discontinued operations. Principal components of investing cash flow are: capital (expenditure) disposal of equipment [CapEx]; business (acquisitions) disposition [NCFBus] and investment (acquisition) disposal [NCFInv].
    NCFO = Column(float64_dtype) # Net Cash Flow from Operations - [Cash Flow Statement] A component of [NCF] representing the amount of cash inflow (outflow) from operating activities; from continuing and discontinued operations.
    NCFX = Column(float64_dtype) # Effect of Exchange Rate Changes on Cash  - [Cash Flow Statement] A component of Net Cash Flow [NCF] representing the amount of increase (decrease) from the effect of exchange rate changes on cash and cash equivalent balances held in foreign currencies.
    NCF = Column(float64_dtype) # Net Cash Flow / Change in Cash & Cash Equivalents - [Cash Flow Statement] Principal component of the cash flow statement representing the amount of increase (decrease) in cash and cash equivalents. Includes [NCFO]; investing [NCFI] and financing [NCFF] for continuing and discontinued operations; and the effect of exchange rate changes on cash [NCFX].
    SBCOMP = Column(float64_dtype) # Share Based Compensation - [Cash Flow Statement] A component of [NCFO] representing the total amount of noncash; equity-based employee remuneration. This may include the value of stock or unit options; amortization of restricted stock or units; and adjustment for officers' compensation. As noncash; this element is an add back when calculating net cash generated by operating activities using the indirect method.
    DEPAMOR = Column(float64_dtype) # Depreciation Amortization & Accretion - [Cash Flow Statement] A component of operating cash flow representing the aggregate net amount of depreciation; amortization; and accretion recognized during an accounting period. As a non-cash item; the net amount is added back to net income when calculating cash provided by or used in operations using the indirect method.
    ASSETS = Column(float64_dtype) # Total Assets - [Balance Sheet] Sum of the carrying amounts as of the balance sheet date of all assets that are recognized. Major components are [CashnEq]; [Investments];[Intangibles]; [PPNENet];[TaxAssets] and [Receivables].
    CASHNEQ = Column(float64_dtype) # Cash and Equivalents - [Balance Sheet] A component of [Assets] representing the amount of currency on hand as well as demand deposits with banks or financial institutions.
    INVESTMENTS = Column(float64_dtype) # Investments - [Balance Sheet] A component of [Assets] representing the total amount of marketable and non-marketable securties; loans receivable and other invested assets.
    INVESTMENTSC = Column(float64_dtype) # Investments Current - [Balance Sheet] The current portion of [Investments]; reported if the company operates a classified balance sheet that segments current and non-current assets.
    INVESTMENTSNC = Column(float64_dtype) # Investments Non-Current - [Balance Sheet] The non-current portion of [Investments]; reported if the company operates a classified balance sheet that segments current and non-current assets.
    DEFERREDREV = Column(float64_dtype) # Deferred Revenue - [Balance Sheet] A component of [Liabilities] representing the carrying amount of consideration received or receivable on potential earnings that were not recognized as revenue; including sales; license fees; and royalties; but excluding interest income.
    DEPOSITS = Column(float64_dtype) # Deposit Liabilities - [Balance Sheet] A component of [Liabilities] representing the total of all deposit liabilities held; including foreign and domestic; interest and noninterest bearing. May include demand deposits; saving deposits; Negotiable Order of Withdrawal and time deposits among others.
    PPNENET = Column(float64_dtype) # Property Plant & Equipment Net - [Balance Sheet] A component of [Assets] representing the amount after accumulated depreciation; depletion and amortization of physical assets used in the normal conduct of business to produce goods and services and not intended for resale.
    INVENTORY = Column(float64_dtype) # Inventory - [Balance Sheet] A component of [Assets] representing the amount after valuation and reserves of inventory expected to be sold; or consumed within one year or operating cycle; if longer.
    TAXASSETS = Column(float64_dtype) # Tax Assets - [Balance Sheet] A component of [Assets] representing tax assets and receivables.
    RECEIVABLES = Column(float64_dtype) # Trade and Non-Trade Receivables - [Balance Sheet] A component of [Assets] representing trade and non-trade receivables.
    PAYABLES = Column(float64_dtype) # Trade and Non-Trade Payables - [Balance Sheet] A component of [Liabilities] representing trade and non-trade payables.
    INTANGIBLES = Column(float64_dtype) # Goodwill and Intangible Assets - [Balance Sheet] A component of [Assets] representing the carrying amounts of all intangible assets and goodwill as of the balance sheet date; net of accumulated amortization and impairment charges.
    LIABILITIES = Column(float64_dtype) # Total Liabilities - [Balance Sheet] Sum of the carrying amounts as of the balance sheet date of all liabilities that are recognized. Principal components are [Debt]; [DeferredRev]; [Payables];[Deposits]; and [TaxLiabilities].
    EQUITY = Column(float64_dtype) # Shareholders Equity - [Balance Sheet] A principal component of the balance sheet; in addition to [Liabilities] and [Assets]; that represents the total of all stockholders' equity (deficit) items; net of receivables from officers; directors; owners; and affiliates of the entity which are attributable to the parent.
    RETEARN = Column(float64_dtype) # Accumulated Retained Earnings (Deficit) - [Balance Sheet] A component of [Equity] representing the cumulative amount of the entities undistributed earnings or deficit. May only be reported annually by certain companies; rather than quarterly.
    ACCOCI = Column(float64_dtype) # Accumulated Other Comprehensive Income - [Balance Sheet] A component of [Equity] representing the accumulated change in equity from transactions and other events and circumstances from non-owner sources; net of tax effect; at period end. Includes foreign currency translation items; certain pension adjustments; unrealized gains and losses on certain investments in debt and equity securities.
    ASSETSC = Column(float64_dtype) # Current Assets - [Balance Sheet] The current portion of [Assets]; reported if a company operates a classified balance sheet that segments current and non-current assets.
    ASSETSNC = Column(float64_dtype) # Assets Non-Current - [Balance Sheet] Amount of non-current assets; for companies that operate a classified balance sheet. Calculated as the different between Total Assets [Assets] and Current Assets [AssetsC].
    LIABILITIESC = Column(float64_dtype) # Current Liabilities - [Balance Sheet] The current portion of [Liabilities]; reported if the company operates a classified balance sheet that segments current and non-current liabilities.
    LIABILITIESNC = Column(float64_dtype) # Liabilities Non-Current - [Balance Sheet] The non-current portion of [Liabilities]; reported if the company operates a classified balance sheet that segments current and non-current liabilities.
    TAXLIABILITIES = Column(float64_dtype) # Tax Liabilities - [Balance Sheet] A component of [Liabilities] representing outstanding tax liabilities.
    DEBT = Column(float64_dtype) # Total Debt - [Balance Sheet] A component of [Liabilities] representing the total amount of current and non-current debt owed. Includes secured and unsecured bonds issued; commercial paper; notes payable; credit facilities; lines of credit; capital lease obligations; and convertible notes.
    DEBTC = Column(float64_dtype) # Debt Current - [Balance Sheet] The current portion of [Debt]; reported if the company operates a classified balance sheet that segments current and non-current liabilities.
    DEBTNC = Column(float64_dtype) # Debt Non-Current - [Balance Sheet] The non-current portion of [Debt] reported if the company operates a classified balance sheet that segments current and non-current liabilities.
    EBT = Column(float64_dtype) # Earnings before Tax - [Metrics] Earnings Before Tax is calculated by adding [TaxExp] back to [NetInc].
    EBIT = Column(float64_dtype) # Earning Before Interest & Taxes (EBIT) - [Income Statement] Earnings Before Interest and Tax is calculated by adding [TaxExp] and [IntExp] back to [NetInc].
    EBITDA = Column(float64_dtype) # Earnings Before Interest Taxes & Depreciation Amortization (EBITDA) - [Metrics] EBITDA is a non-GAAP accounting metric that is widely used when assessing the performance of companies; calculated by adding [DepAmor] back to [EBIT].
    FXUSD = Column(float64_dtype) # Foreign Currency to USD Exchange Rate - [Metrics] The exchange rate used for the conversion of foreign currency to USD for non-US companies that do not report in USD.
    EQUITYUSD = Column(float64_dtype) # Shareholders Equity (USD) - [Balance Sheet] [Equity] in USD; converted by [FXUSD].
    EPSUSD = Column(float64_dtype) # Earnings per Basic Share (USD) - [Income Statement] [EPS] in USD; converted by [FXUSD].
    REVENUEUSD = Column(float64_dtype) # Revenues (USD) - [Income Statement] [Revenue] in USD; converted by [FXUSD].
    NETINCCMNUSD = Column(float64_dtype) # Net Income Common Stock (USD) - [Income Statement] [NetIncCmn] in USD; converted by [FXUSD].
    CASHNEQUSD = Column(float64_dtype) # Cash and Equivalents (USD) - [Balance Sheet] [CashnEq] in USD; converted by [FXUSD].
    DEBTUSD = Column(float64_dtype) # Total Debt (USD) - [Balance Sheet] [Debt] in USD; converted by [FXUSD].
    EBITUSD = Column(float64_dtype) # Earning Before Interest & Taxes (USD) - [Income Statement] [EBIT] in USD; converted by [FXUSD].
    EBITDAUSD = Column(float64_dtype) # Earnings Before Interest Taxes & Depreciation Amortization (USD) - [Metrics] [EBITDA] in USD; converted by [FXUSD].
    SHARESBAS = Column(float64_dtype) # Shares (Basic) - [Entity] The number of shares or other units outstanding of the entity's capital or common stock or other ownership interests; as stated on the cover of related periodic report (10-K/10-Q); after adjustment for stock splits.
    DPS = Column(float64_dtype) # Dividends per Basic Common Share - [Income Statement] Aggregate dividends declared during the period for each split-adjusted share of common stock outstanding. Includes spinoffs where identified.
    SHAREFACTOR = Column(float64_dtype) # Share Factor - [Entity] Share factor is a multiplicant in the calculation of [MarketCap] and is used to adjust for: American Depository Receipts (ADRs) that represent more or less than 1 underlying share; and; companies which have different earnings share for different share classes (eg Berkshire Hathaway - BRKB).
    MARKETCAP = Column(float64_dtype) # Market Capitalization - [Metrics] Represents the product of [SharesBas]; [Price] and [ShareFactor].
    EV = Column(float64_dtype) # Enterprise Value - [Metrics] Enterprise value is a measure of the value of a business as a whole; calculated as [MarketCap] plus [DebtUSD] minus [CashnEqUSD].
    INVCAP = Column(float64_dtype) # Invested Capital - [Metrics] Invested capital is an input into the calculation of [ROIC]; and is calculated as: [Debt] plus [Assets] minus [Intangibles] minus [CashnEq] minus [LiabilitiesC]. Please note this calculation method is subject to change.
    EQUITYAVG = Column(float64_dtype) # Average Equity - [Metrics] Average equity value for the period used in calculation of [ROE]; derived from [Equity].
    ASSETSAVG = Column(float64_dtype) # Average Assets - [Metrics] Average asset value for the period used in calculation of [ROE] and [ROA]; derived from [Assets].
    INVCAPAVG = Column(float64_dtype) # Invested Capital Average - [Metrics] Average invested capital value for the period used in the calculation of [ROIC]; and derived from [InvCap]. Invested capital is an input into the calculation of [ROIC]; and is calculated as: [Debt] plus [Assets] minus [Intangibles] minus [CashnEq] minus [LiabilitiesC]. Please note this calculation method is subject to change.
    TANGIBLES = Column(float64_dtype) # Tangible Asset Value - [Metrics] The value of tangibles assets calculated as the difference between [Assets] and [Intangibles].
    ROE = Column(float64_dtype) # Return on Average Equity - [Metrics] Return on equity measures a corporation's profitability by calculating the amount of [NetIncCmn] returned as a percentage of [EquityAvg].
    ROA = Column(float64_dtype) # Return on Average Assets - [Metrics] Return on assets measures how profitable a company is [NetIncCmn] relative to its total assets [AssetsAvg].
    FCF = Column(float64_dtype) # Free Cash Flow - [Metrics] Free Cash Flow is a measure of financial performance calculated as [NCFO] minus [CapEx].
    ROIC = Column(float64_dtype) # Return on Invested Capital - [Metrics] Return on Invested Capital is ratio estimated by dividing [EBIT] by [InvCapAvg]. [InvCap] is calculated as: [Debt] plus [Assets] minus [Intangibles] minus [CashnEq] minus [LiabilitiesC]. Please note this calculation method is subject to change.
    GP = Column(float64_dtype) # Gross Profit - [Income Statement] Aggregate revenue [Revenue] less cost of revenue [CoR] directly attributable to the revenue generation activity.
    OPINC = Column(float64_dtype) # Operating Income - [Income Statement] Operating income is a measure of financial performance before the deduction of [IntExp]; [TaxExp] and other Non-Operating items. It is calculated as [GP] minus [OpEx].
    GROSSMARGIN = Column(float64_dtype) # Gross Margin - [Metrics] Gross Margin measures the ratio between a company's [GP] and [Revenue].
    NETMARGIN = Column(float64_dtype) # Profit Margin - [Metrics] Measures the ratio between a company's [NetIncCmn] and [Revenue].
    EBITDAMARGIN = Column(float64_dtype) # EBITDA Margin - [Metrics] Measures the ratio between a company's [EBITDA] and [Revenue].
    ROS = Column(float64_dtype) # Return on Sales - [Metrics] Return on Sales is a ratio to evaluate a company's operational efficiency; calculated by dividing [EBIT] by [Revenue]. ROS is often a component of DuPont ROE analysis.
    ASSETTURNOVER = Column(float64_dtype) # Asset Turnover - [Metrics] Asset turnover is a measure of a firms operating efficiency; calculated by dividing [Revenue] by [AssetsAVG]. Often a component of DuPont ROE analysis.
    PAYOUTRATIO = Column(float64_dtype) # Payout Ratio - [Metrics] The percentage of earnings paid as dividends to common stockholders. Calculated by dividing [DPS] by [EPSUSD].
    EVEBITDA = Column(float64_dtype) # Enterprise Value over EBITDA - [Metrics] Measures the ratio between [EV] and [EBITDAUSD].
    EVEBIT = Column(float64_dtype) # Enterprise Value over EBIT - [Metrics] Measures the ratio between [EV] and [EBITUSD].
    PE = Column(float64_dtype) # Price Earnings (Damodaran Method) - [Metrics] Measures the ratio between [MarketCap] and [NetIncCmnUSD]
    PE1 = Column(float64_dtype) # Price to Earnings Ratio - [Metrics] An alternative to [PE] representing the ratio between [Price] and [EPSUSD].
    SPS = Column(float64_dtype) # Sales per Share - [Metrics] Sales per Share measures the ratio between [RevenueUSD] and [SharesWA] as adjusted by [ShareFactor].
    PS1 = Column(float64_dtype) # Price to Sales Ratio - [Metrics] An alternative calculation method to [PS]; that measures the ratio between a company's [Price] and it's [SPS].
    PS = Column(float64_dtype) # Price Sales (Damodaran Method) - [Metrics] Measures the ratio between [MarketCap] and [RevenueUSD].
    PB = Column(float64_dtype) # Price to Book Value - [Metrics] Measures the ratio between [MarketCap] and [EquityUSD].
    DE = Column(float64_dtype) # Debt to Equity Ratio - [Metrics] Measures the ratio between [Liabilities] and [Equity].
    DIVYIELD = Column(float64_dtype) # Dividend Yield - [Metrics] Dividend Yield measures the ratio between a company's [DPS] and its [Price].
    CURRENTRATIO = Column(float64_dtype) # Current Ratio - [Metrics] The ratio between [AssetsC] and [LiabilitiesC]; for companies that operate a classified balance sheet.
    WORKINGCAPITAL = Column(float64_dtype) # Working Capital - [Metrics] Working capital measures the difference between [AssetsC] and [LiabilitiesC].
    FCFPS = Column(float64_dtype) # Free Cash Flow per Share - [Metrics] Free Cash Flow per Share is a valuation metric calculated by dividing [FCF] by [SharesWA] and [ShareFactor].
    BVPS = Column(float64_dtype) # Book Value per Share - [Metrics] Measures the ratio between [Equity] and [SharesWA] as adjusted by [ShareFactor].
    TBVPS = Column(float64_dtype) # Tangible Assets Book Value per Share - [Metrics] Measures the ratio between [Tangibles] and [SharesWA] as adjusted by [ShareFactor].
    PRICE = Column(float64_dtype) # Share Price (Adjusted Close) - [Entity] The price per common share adjusted for stock splits but not adjusted for dividends; used in the computation of [PE1]; [PS1]; [DivYield] and [SPS].
    CALENDARDATE = Column(datetime64ns_dtype, missing_value=NaTD) # Calendar Date - [Entity] The Calendar Date represents the normalized [ReportPeriod]. This provides a common date to query for which is necessary due to irregularity in report periods across companies. For example; if the report period is "2015-09-26"; the calendar date will be "2015-09-30" for quarterly and trailing-twelve-month dimensions (ARQ;MRQ;ART;MRT); and "2015-12-31" for annual dimensions (ARY;MRY). We also employ offsets in order to maximise comparability of the period across companies. For example consider two companies: one with a quarter ending on 2018-07-24; and the other with a quarter ending on 2018-06-28. A naive normalization process would assign these to differing calendar quarters of 2018-09-30 and 2018-06-30 respectively. However, we assign these both to the 2018-06-30 calendar quarter because this maximises the overlap in the report periods in question and therefore the comparability of this period.
    REPORTPERIOD = Column(datetime64ns_dtype, missing_value=NaTD) #Report Period - [Entity] The Report Period represents the end date of the fiscal period.

# legacy aliases
SharadarQuarterlyFundamentals = Fundamentals.slice(dimension="ARQ", period_offset=0)
SharadarAnnualFundamentals = Fundamentals.slice(dimension="ARY", period_offset=0)
SharadarTrailingTwelveMonthFundamentals = Fundamentals.slice(dimension="ART", period_offset=0)

class Institutions(DataSetFamily):
    """
    DataSetFamily representing Sharadar institutional ownership. In order to use
    the data in a pipeline, it must first be sliced to generate a regular
    pipeline DataSet.

    Institutions can be sliced along one dimension:

    - `period_offset` : must be set to 0. In the future this dimension will
      allow requesting data from earlier quarters.

    Attributes
    ----------
    CLLHOLDERS : float
        Number of Call holders (Institutional) - The number of call holders.

    CLLUNITS : float
        Number of Call Units held (institutional) - The total number of call
        units held.

    CLLVALUE : float
        Value of Call units held (institutional) - The total value of call
        units held.

    DBTHOLDERS : float
        Number of Debt holders (institutional) - The number of debt holders.

    DBTUNITS : float
        Number of Debt Units held (institutional) - The total number of debt
        units held.

    DBTVALUE : float
        Value of Debt units held (institutional) - The total value of debt
        units held.

    FNDHOLDERS : float
        Number of Fund holders (institutional) - The number of fund holders.

    FNDUNITS : float
        Number of Fund units held (institutional) - The total number of fund
        units held.

    FNDVALUE : float
        Value of Fund units held (institutional) - The total value of fund
        units held.

    PERCENTOFTOTAL : float
        Percentage of Total Institutional Holdings for the Quarter - The
        percentage that the [TotalValue] of this line item constitutes of all
        institutional holdings for this quarter.

    PRFHOLDERS : float
        Number of Preferred Stock holders (institutional) - The number of
        preferred stock holders.

    PRFUNITS : float
        Number of Preferred Stock units held (institutional) - The total
        number of preferred stock units held.

    PRFVALUE : float
        Value of Preferred Stock units held (institutional) - The total value
        of preferred stock units held.

    PUTHOLDERS : float
        Number of Put holders (institutional) - The number of put holders.

    PUTUNITS : float
        Number of Put Units held (institutional) - The total number of put
        units held.

    PUTVALUE : float
        Value of Put units held (institutional) - The total value of put units
        held.

    SHRHOLDERS : float
        Number of Shareholders (Institutional) - The number of shareholders.

    SHRUNITS : float
        Number of Share Units held (institutional) - The total number of share
        units held.

    SHRVALUE : float
        Value of Share units held (institutional) - The total value of share
        units held.

    TOTALVALUE : float
        Total Value of all Security types held (institutional) - The total
        value of all security types held.

    UNDHOLDERS : float
        Number of Unidentified Security type holders (institutional) - The
        number of unidentified security type holders.

    UNDUNITS : float
        Number of Unidentified Security type units held (institutional) - The
        total number of unidentified security type units held.

    UNDVALUE : float
        Value of Unidentified Security type units held (institutional) - The
        total value of unidentified security type units held.

    WNTHOLDERS : float
        Number of Warrant holders (institutional) - The number of warrant
        holders.

    WNTUNITS : float
        Number of Warrant Units held (institutional) - The total number of
        warrant units held.

    WNTVALUE : float
        Value of Warrant units held (institutional) - The total value of
        warrant units held.

    Examples
    --------
    Select stocks with large institutional ownership:

    >>> have_inst_own = sharadar.Institutions.slice(period_offset=0).TOTALVALUE.latest.percentile_between(80, 100)    # doctest: +SKIP
    """
    extra_dims = [
        ('period_offset', {0}),
    ]

    domain = US_EQUITIES

    SHRHOLDERS = Column(float64_dtype) # Number of Shareholders (Institutional) - The number of shareholders.
    CLLHOLDERS = Column(float64_dtype) # Number of Call holders (Institutional) - The number of call holders.
    PUTHOLDERS = Column(float64_dtype) # Number of Put holders (institutional) - The number of put holders.
    WNTHOLDERS = Column(float64_dtype) # Number of Warrant holders (institutional) - The number of warrant holders.
    DBTHOLDERS = Column(float64_dtype) # Number of Debt holders (institutional) - The number of debt holders.
    PRFHOLDERS = Column(float64_dtype) # Number of Preferred Stock holders (institutional) - The number of preferred stock holders.
    FNDHOLDERS = Column(float64_dtype) # Number of Fund holders (institutional) - The number of fund holders.
    UNDHOLDERS = Column(float64_dtype) # Number of Unidentified Security type holders (institutional) - The number of unidentified security type holders.
    SHRUNITS = Column(float64_dtype) # Number of Share Units held (institutional) - The total number of share units held.
    CLLUNITS = Column(float64_dtype) # Number of Call Units held (institutional) - The total number of call units held.
    PUTUNITS = Column(float64_dtype) # Number of Put Units held (institutional) - The total number of put units held.
    WNTUNITS = Column(float64_dtype) # Number of Warrant Units held (institutional) - The total number of warrant units held.
    DBTUNITS = Column(float64_dtype) # Number of Debt Units held (institutional) - The total number of debt units held.
    PRFUNITS = Column(float64_dtype) # Number of Preferred Stock units held (institutional) - The total number of preferred stock units held.
    FNDUNITS = Column(float64_dtype) # Number of Fund units held (institutional) - The total number of fund units held.
    UNDUNITS = Column(float64_dtype) # Number of Unidentified Security type units held (institutional) - The total number of unidentified security type units held.
    SHRVALUE = Column(float64_dtype) # Value of Share units held (institutional) - The total value of share units held.
    CLLVALUE = Column(float64_dtype) # Value of Call units held (institutional) - The total value of call units held.
    PUTVALUE = Column(float64_dtype) # Value of Put units held (institutional) - The total value of put units held.
    WNTVALUE = Column(float64_dtype) # Value of Warrant units held (institutional) - The total value of warrant units held.
    DBTVALUE = Column(float64_dtype) # Value of Debt units held (institutional) - The total value of debt units held.
    PRFVALUE = Column(float64_dtype) # Value of Preferred Stock units held (institutional) - The total value of preferred stock units held.
    FNDVALUE = Column(float64_dtype) # Value of Fund units held (institutional) - The total value of fund units held.
    UNDVALUE = Column(float64_dtype) # Value of Unidentified Security type units held (institutional) - The total value of unidentified security type units held.
    TOTALVALUE = Column(float64_dtype) # Total Value of all Security types held (institutional) - The total value of all security types held.
    PERCENTOFTOTAL = Column(float64_dtype) # Percentage of Total Institutional Holdings for the Quarter - The percentage that the [TotalValue] of this line item constitutes of all institutional holdings for this quarter.

# legacy alias
SharadarInstitutions = Institutions.slice(period_offset=0)
