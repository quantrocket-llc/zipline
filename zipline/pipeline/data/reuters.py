# Copyright 2017 QuantRocket LLC - All Rights Reserved
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

from zipline.utils.numpy_utils import float64_dtype
from zipline.pipeline.data import Column, DataSetFamily

class Financials(DataSetFamily):
    """
    DataSetFamily representing Reuters financials. In order to use
    the data in a pipeline, it must first be sliced to generate a regular
    pipeline DataSet.

    Financials can be sliced along two dimensions:

    - `interim` : True for interim financials and False for annual financials.

    - `period_offset` : must be set to 0. In the future this dimension will
      allow requesting data from earlier periods.

    Attributes
    ----------
    AACR : float
        Accounts Receivable - Trade, Net

    ACAE : float
        Cash & Equivalents

    ACSH : float
        Cash

    ADEP : float
        Accumulated Depreciation, Total

    AGWI : float
        Goodwill, Net

    AINT : float
        Intangibles, Net

    AITL : float
        Total Inventory

    ALTR : float
        Note Receivable - Long Term

    APPN : float
        Property/Plant/Equipment, Total - Net

    APPY : float
        Prepaid Expenses

    APTC : float
        Property/Plant/Equipment, Total - Gross

    ASTI : float
        Short Term Investments

    ATCA : float
        Total Current Assets

    ATOT : float
        Total Assets

    ATRC : float
        Total Receivables, Net

    CEIA : float
        Equity In Affiliates

    CGAP : float
        U.S. GAAP Adjustment

    CIAC : float
        Income Available to Com Excl ExtraOrd

    CMIN : float
        Minority Interest

    DDPS1 : float
        DPS - Common Stock Primary Issue

    EIBT : float
        Net Income Before Taxes

    ERAD : float
        Research & Development

    ETOE : float
        Total Operating Expense

    FCDP : float
        Total Cash Dividends Paid

    FPRD : float
        Issuance (Retirement) of Debt, Net

    FPSS : float
        Issuance (Retirement) of Stock, Net

    FTLF : float
        Cash from Financing Activities

    ITLI : float
        Cash from Investing Activities

    LAEX : float
        Accrued Expenses

    LAPB : float
        Accounts Payable

    LCLD : float
        Current Port. of  LT Debt/Capital Leases

    LCLO : float
        Capital Lease Obligations

    LLTD : float
        Long Term Debt

    LMIN : float
        Minority Interest

    LPBA : float
        Payable/Accrued

    LSTD : float
        Notes Payable/Short Term Debt

    LTCL : float
        Total Current Liabilities

    LTLL : float
        Total Liabilities

    LTTD : float
        Total Long Term Debt

    NGLA : float
        Gain (Loss) on Sale of Assets

    NIBX : float
        Net Income Before Extra. Items

    NINC : float
        Net Income

    OBDT : float
        Deferred Taxes

    ONET : float
        Net Income/Starting Line

    OTLO : float
        Cash from Operating Activities

    QEDG : float
        ESOP Debt Guarantee

    QPIC : float
        Additional Paid-In Capital

    QRED : float
        Retained Earnings (Accumulated Deficit)

    QTCO : float
        Total Common Shares Outstanding

    QTEL : float
        Total Liabilities & Shareholders' Equity

    QTLE : float
        Total Equity

    QTPO : float
        Total Preferred Shares Outstanding

    QTSC : float
        Treasury Stock - Common

    QUGL : float
        Unrealized Gain (Loss)

    RTLR : float
        Total Revenue

    SAMT : float
        Amortization

    SANI : float
        Total Adjustments to Net Income

    SBDT : float
        Deferred Income Tax

    SCEX : float
        Capital Expenditures

    SCIP : float
        Cash Interest Paid

    SCMS : float
        Common Stock, Total

    SCOR : float
        Cost of Revenue, Total

    SCSI : float
        Cash and Short Term Investments

    SCTP : float
        Cash Taxes Paid

    SDAJ : float
        Dilution Adjustment

    SDBF : float
        Diluted EPS Excluding ExtraOrd Items

    SDED : float
        Depreciation/Depletion

    SDNI : float
        Diluted Net Income

    SDPR : float
        Depreciation/Amortization

    SDWS : float
        Diluted Weighted Average Shares

    SFCF : float
        Financing Cash Flow Items

    SFEE : float
        Foreign Exchange Effects

    SGRP : float
        Gross Profit

    SICF : float
        Other Investing Cash Flow Items, Total

    SINN : float
        Interest Exp.(Inc.),Net-Operating, Total

    SINV : float
        Long Term Investments

    SLTL : float
        Other Liabilities, Total

    SNCC : float
        Net Change in Cash

    SNCI : float
        Non-Cash Items

    SNIN : float
        Interest Inc.(Exp.),Net-Non-Op., Total

    SOCA : float
        Other Current Assets, Total

    SOCF : float
        Changes in Working Capital

    SOCL : float
        Other Current liabilities, Total

    SOLA : float
        Other Long Term Assets, Total

    SONT : float
        Other, Net

    SOOE : float
        Other Operating Expenses, Total

    SOPI : float
        Operating Income

    SORE : float
        Other Revenue, Total

    SOTE : float
        Other Equity, Total

    SPRS : float
        Preferred Stock - Non Redeemable, Net

    SREV : float
        Revenue

    SRPR : float
        Redeemable Preferred Stock, Total

    SSGA : float
        Selling/General/Admin. Expenses, Total

    STBP : float
        Tangible Book Value per Share, Common Eq

    STLD : float
        Total Debt

    STXI : float
        Total Extraordinary Items

    SUIE : float
        Unusual Expense (Income)

    TIAT : float
        Net Income After Taxes

    TTAX : float
        Provision for Income Taxes

    VDES : float
        Diluted Normalized EPS

    XNIC : float
        Income Available to Com Incl ExtraOrd

    Examples
    --------
    Create a CustomFactor for PB ratio, using annual financials:

    >>> annual_financials = reuters.Financials.slice(interim=False, period_offset=0)
    >>> class PriceBookRatio(CustomFactor):
            inputs = [
                EquityPricing.close,
                annual_financials.ATOT,  # total assets
                annual_financials.LTLL,  # total liabilities
                annual_financials.QTCO  # common shares outstanding
            ]
            window_length = 1
            def compute(self, today, assets, out, closes, tot_assets, tot_liabilities, shares_out):
                book_values_per_share = (tot_assets - tot_liabilities)/shares_out
                pb_ratios = closes/book_values_per_share
                out[:] = pb_ratios
    """
    extra_dims = [
        ('interim', {True, False}),
        ('period_offset', {0}),
    ]

    SCMS = Column(float64_dtype) # Common Stock, Total
    VDES = Column(float64_dtype) # Diluted Normalized EPS
    SDNI = Column(float64_dtype) # Diluted Net Income
    SPRS = Column(float64_dtype) # Preferred Stock - Non Redeemable, Net
    SOPI = Column(float64_dtype) # Operating Income
    LAPB = Column(float64_dtype) # Accounts Payable
    NINC = Column(float64_dtype) # Net Income
    SOCL = Column(float64_dtype) # Other Current liabilities, Total
    ETOE = Column(float64_dtype) # Total Operating Expense
    SOLA = Column(float64_dtype) # Other Long Term Assets, Total
    SREV = Column(float64_dtype) # Revenue
    LAEX = Column(float64_dtype) # Accrued Expenses
    XNIC = Column(float64_dtype) # Income Available to Com Incl ExtraOrd
    SUIE = Column(float64_dtype) # Unusual Expense (Income)
    APTC = Column(float64_dtype) # Property/Plant/Equipment, Total - Gross
    SOBL = Column(float64_dtype) # Other Bearing Liabilities, Total
    SNII = Column(float64_dtype) # Non-Interest Income, Bank
    CEIA = Column(float64_dtype) # Equity In Affiliates
    ERAD = Column(float64_dtype) # Research & Development
    SDBF = Column(float64_dtype) # Diluted EPS Excluding ExtraOrd Items
    SDWS = Column(float64_dtype) # Diluted Weighted Average Shares
    SORE = Column(float64_dtype) # Other Revenue, Total
    SCEX = Column(float64_dtype) # Capital Expenditures
    ELLP = Column(float64_dtype) # Loan Loss Provision
    ACSH = Column(float64_dtype) # Cash
    AACR = Column(float64_dtype) # Accounts Receivable - Trade, Net
    SCOR = Column(float64_dtype) # Cost of Revenue, Total
    SUPN = Column(float64_dtype) # Total Utility Plant, Net
    EIBT = Column(float64_dtype) # Net Income Before Taxes
    AGWI = Column(float64_dtype) # Goodwill, Net
    SCIP = Column(float64_dtype) # Cash Interest Paid
    SDED = Column(float64_dtype) # Depreciation/Depletion
    RNII = Column(float64_dtype) # Net Investment Income
    ADPA = Column(float64_dtype) # Deferred Policy Acquisition Costs
    SONT = Column(float64_dtype) # Other, Net
    CGAP = Column(float64_dtype) # U.S. GAAP Adjustment
    AINT = Column(float64_dtype) # Intangibles, Net
    SGRP = Column(float64_dtype) # Gross Profit
    SNIE = Column(float64_dtype) # Non-Interest Expense, Bank
    EDOE = Column(float64_dtype) # Operations & Maintenance
    SSGA = Column(float64_dtype) # Selling/General/Admin. Expenses, Total
    SNIN = Column(float64_dtype) # Interest Inc.(Exp.),Net-Non-Op., Total
    QTSC = Column(float64_dtype) # Treasury Stock - Common
    OCPD = Column(float64_dtype) # Cash Payments
    OBDT = Column(float64_dtype) # Deferred Taxes
    TTAX = Column(float64_dtype) # Provision for Income Taxes
    LPBA = Column(float64_dtype) # Payable/Accrued
    QRED = Column(float64_dtype) # Retained Earnings (Accumulated Deficit)
    SCSI = Column(float64_dtype) # Cash and Short Term Investments
    SIAP = Column(float64_dtype) # Net Interest Inc. After Loan Loss Prov.
    ANTL = Column(float64_dtype) # Net Loans
    QTCO = Column(float64_dtype) # Total Common Shares Outstanding
    LDBT = Column(float64_dtype) # Total Deposits
    SANI = Column(float64_dtype) # Total Adjustments to Net Income
    AITL = Column(float64_dtype) # Total Inventory
    ATRC = Column(float64_dtype) # Total Receivables, Net
    SBDT = Column(float64_dtype) # Deferred Income Tax
    ASTI = Column(float64_dtype) # Short Term Investments
    OTLO = Column(float64_dtype) # Cash from Operating Activities
    OCRC = Column(float64_dtype) # Cash Receipts
    RRGL = Column(float64_dtype) # Realized & Unrealized Gains (Losses)
    STLD = Column(float64_dtype) # Total Debt
    LTTD = Column(float64_dtype) # Total Long Term Debt
    LTLL = Column(float64_dtype) # Total Liabilities
    APPN = Column(float64_dtype) # Property/Plant/Equipment, Total - Net
    SCTP = Column(float64_dtype) # Cash Taxes Paid
    SLTL = Column(float64_dtype) # Other Liabilities, Total
    DDPS1 = Column(float64_dtype) # DPS - Common Stock Primary Issue
    SRPR = Column(float64_dtype) # Redeemable Preferred Stock, Total
    ITLI = Column(float64_dtype) # Cash from Investing Activities
    ONET = Column(float64_dtype) # Net Income/Starting Line
    SDPR = Column(float64_dtype) # Depreciation/Amortization
    STIE = Column(float64_dtype) # Total Interest Expense
    APRE = Column(float64_dtype) # Insurance Receivables
    SNCC = Column(float64_dtype) # Net Change in Cash
    SFCF = Column(float64_dtype) # Financing Cash Flow Items
    SINN = Column(float64_dtype) # Interest Exp.(Inc.),Net-Operating, Total
    CMIN = Column(float64_dtype) # Minority Interest
    SOAT = Column(float64_dtype) # Other Assets, Total
    SNCI = Column(float64_dtype) # Non-Cash Items
    LCLD = Column(float64_dtype) # Current Port. of  LT Debt/Capital Leases
    SDAJ = Column(float64_dtype) # Dilution Adjustment
    SIIB = Column(float64_dtype) # Interest Income, Bank
    QUGL = Column(float64_dtype) # Unrealized Gain (Loss)
    NIBX = Column(float64_dtype) # Net Income Before Extra. Items
    SOOE = Column(float64_dtype) # Other Operating Expenses, Total
    SAMT = Column(float64_dtype) # Amortization
    SFEE = Column(float64_dtype) # Foreign Exchange Effects
    STXI = Column(float64_dtype) # Total Extraordinary Items
    APPY = Column(float64_dtype) # Prepaid Expenses
    EFEX = Column(float64_dtype) # Fuel Expense
    QTPO = Column(float64_dtype) # Total Preferred Shares Outstanding
    NGLA = Column(float64_dtype) # Gain (Loss) on Sale of Assets
    SINV = Column(float64_dtype) # Long Term Investments
    SOCA = Column(float64_dtype) # Other Current Assets, Total
    FCDP = Column(float64_dtype) # Total Cash Dividends Paid
    FPSS = Column(float64_dtype) # Issuance (Retirement) of Stock, Net
    RTLR = Column(float64_dtype) # Total Revenue
    ACDB = Column(float64_dtype) # Cash & Due from Banks
    TIAT = Column(float64_dtype) # Net Income After Taxes
    SOEA = Column(float64_dtype) # Other Earning Assets, Total
    SOTE = Column(float64_dtype) # Other Equity, Total
    SPOL = Column(float64_dtype) # Policy Liabilities
    NAFC = Column(float64_dtype) # Allowance for Funds Used During Const.
    QPIC = Column(float64_dtype) # Additional Paid-In Capital
    QTLE = Column(float64_dtype) # Total Equity
    ACAE = Column(float64_dtype) # Cash & Equivalents
    FPRD = Column(float64_dtype) # Issuance (Retirement) of Debt, Net
    ALTR = Column(float64_dtype) # Note Receivable - Long Term
    SLBA = Column(float64_dtype) # Losses, Benefits, and Adjustments, Total
    ATCA = Column(float64_dtype) # Total Current Assets
    SOCF = Column(float64_dtype) # Changes in Working Capital
    LCLO = Column(float64_dtype) # Capital Lease Obligations
    LSTD = Column(float64_dtype) # Notes Payable/Short Term Debt
    STBP = Column(float64_dtype) # Tangible Book Value per Share, Common Eq
    SICF = Column(float64_dtype) # Other Investing Cash Flow Items, Total
    ENII = Column(float64_dtype) # Net Interest Income
    QTEL = Column(float64_dtype) # Total Liabilities & Shareholders' Equity
    FTLF = Column(float64_dtype) # Cash from Financing Activities
    LTCL = Column(float64_dtype) # Total Current Liabilities
    SPRE = Column(float64_dtype) # Total Premiums Earned
    LSTB = Column(float64_dtype) # Total Short Term Borrowings
    EPAC = Column(float64_dtype) # Amortization of Policy Acquisition Costs
    LLTD = Column(float64_dtype) # Long Term Debt
    ATOT = Column(float64_dtype) # Total Assets
    CIAC = Column(float64_dtype) # Income Available to Com Excl ExtraOrd
    QEDG = Column(float64_dtype) # ESOP Debt Guarantee
    LMIN = Column(float64_dtype) # Minority Interest
    ADEP = Column(float64_dtype) # Accumulated Depreciation, Total

# legacy aliases
ReutersAnnualFinancials = Financials.slice(interim=False, period_offset=0)
ReutersInterimFinancials = Financials.slice(interim=True, period_offset=0)

class Estimates(DataSetFamily):
    """
    DataSetFamily representing Reuters estimates and actuals. In order to use
    the data in a pipeline, it must first be sliced to generate a regular
    pipeline DataSet.

    Estimates can be sliced along three dimensions:

    - `period_type` : the choices are 'Q' for quarterly or 'A' for annual or
      'S' for semi-annual.

    - `field` : the choices are 'Actual', 'Mean', 'High', 'Low', 'Median', 'NumOfEst',
      or 'StdDev'. All fields except Actual refer to estimates.

    - `period_offset` : must be set to 0. In the future this dimension will
      allow requesting data from earlier periods.

    Attributes
    ----------
    BVPS : float
        Book Value Per Share

    CAPEX : float
        Capital Expenditure

    CPS : float
        Cash Flow Per Share

    DPS : float
        Dividend Per Share

    EBIT : float
        Earnings Before Interest and Tax

    EBITDA : float
        Earnings Before Interest, Taxes, Depreciation and Amortization

    EPS : float
        Earnings Per Share Excluding Exceptional Items

    EPSEBG : float
        Earnings Per Share Before Goodwill

    EPSREP : float
        Earnings Per Share Reported

    FFO : float
        Funds From Operations Per Share

    NAV : float
        Net Asset Value Per Share

    NDEBT : float
        Net Debt

    NPROFIT : float
        Net Profit Excluding Exceptional Items

    NPROFITEBG : float
        Net Profit Before Goodwill

    NPROFITREP : float
        Net Profit Reported

    OPROFIT : float
        Operating Profit

    PPROFIT : float
        Pre-Tax Profit Excluding Exceptional Items

    PPROFITEBG : float
        Pre-Tax Profit Before Goodwill

    PPROFITREP : float
        Pre-Tax Profit Reported

    REVENUE : float
        Revenue

    ROA : float
        Return On Assets

    ROE : float
        Return On Equity

    Examples
    --------
    Select stocks with high book values, using quarterly actuals:

    >>> have_high_bvps = reuters.Estimates.slice(period_type="Q", field="Actual", period_offset=0).BVPS.latest.percentile_between(80, 100)
    """
    extra_dims = [
        ('period_type', {'Q', 'A', 'S'}),
        ('field', {'Actual', 'Mean', 'High', 'Low', 'Median', 'NumOfEst', 'StdDev'}),
        ('period_offset', {0}),
    ]

    BVPS = Column(float64_dtype) # Book Value Per Share
    CAPEX = Column(float64_dtype) # Capital Expenditure
    CPS = Column(float64_dtype) # Cash Flow Per Share
    DPS = Column(float64_dtype) # Dividend Per Share
    EBIT = Column(float64_dtype) # Earnings Before Interest and Tax
    EBITDA = Column(float64_dtype) # Earnings Before Interest, Taxes, Depreciation and Amortization
    EPS = Column(float64_dtype) # Earnings Per Share Excluding Exceptional Items
    EPSEBG = Column(float64_dtype) # Earnings Per Share Before Goodwill
    EPSREP = Column(float64_dtype) # Earnings Per Share Reported
    FFO = Column(float64_dtype) # Funds From Operations Per Share
    NAV = Column(float64_dtype) # Net Asset Value Per Share
    NDEBT = Column(float64_dtype) # Net Debt
    NPROFIT = Column(float64_dtype) # Net Profit Excluding Exceptional Items
    NPROFITEBG = Column(float64_dtype) # Net Profit Before Goodwill
    NPROFITREP = Column(float64_dtype) # Net Profit Reported
    OPROFIT = Column(float64_dtype) # Operating Profit
    PPROFIT = Column(float64_dtype) # Pre-Tax Profit Excluding Exceptional Items
    PPROFITEBG = Column(float64_dtype) # Pre-Tax Profit Before Goodwill
    PPROFITREP = Column(float64_dtype) # Pre-Tax Profit Reported
    REVENUE = Column(float64_dtype) # Revenue
    ROA = Column(float64_dtype) # Return On Assets
    ROE = Column(float64_dtype) # Return On Equity

# legacy aliases
ReutersAnnualEstimates = Estimates.slice(period_type="A", field="Mean", period_offset=0)
ReutersQuarterlyEstimates = Estimates.slice(period_type="Q", field="Mean", period_offset=0)
ReutersAnnualActuals = Estimates.slice(period_type="A", field="Actual", period_offset=0)
ReutersQuarterlyActuals = Estimates.slice(period_type="Q", field="Actual", period_offset=0)
