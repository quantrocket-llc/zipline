# Copyright 2022 QuantRocket LLC - All Rights Reserved
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

from typing import Literal
from zipline.pipeline.data import sharadar
from zipline.pipeline.factors import Latest, Factor
from zipline.pipeline.filters import Filter

def PiotroskiFScore(
    dimension: Literal['ARQ', 'ARY', 'ART', 'MRQ', 'MRY', 'MRT'] = "ART",
    period_offset: int = 0,
    previous_period_offset: int = None,
    mask: Filter = None
    ) -> Factor:
    """
    Return a Factor that computes the Piotroski F-Score using Sharadar
    fundamentals.

    The Piotroski F-Score evaluates a firm's financial health on a scale
    of 0-9, with 9 being the best. The score is calculated being awarding
    one point for each of the following nine criteria that are met:

    Profitability Criteria:

    * Positive return on assets (ROA) in the current year
    * Positive operating cash flow in the current year
    * Higher ROA in the current period than in the previous year
    * Cash flow from operations is higher than ROA (quality of earnings)

    Funding Criteria:

    * Lower long term debt in the current period than in the previous year (decreased leverage)
    * Higher current ratio in the current period than in the previous year (more liquidity)
    * No new shares issued in the last year (lack of dilution)

    Operating Efficiency Criteria:

    * Higher gross margin in the current period than in the previous year
    * Higher asset turnover ratio in the current period than in the previous year

    Parameters
    ----------
    dimension : str, optional
        the type of reports to use. Choices are ARQ, ARY, ART, MRQ, MRY,
        MRT, where AR=As Reported, MR=Most Recent Reported, Q=Quarterly,
        Y=Annual, and T=Trailing Twelve Month. Default is ART.

    period_offset : int, optional
        which fiscal period to return F-Scores for. If period_offset
        is 0, returns the most recent point-in-time F-Scores. If period_offset
        is -1, returns F-Scores for the prior fiscal period; if -2, two fiscal
        periods ago, etc. For quarterly and trailing-twelve-month dimensions,
        previous period means previous quarter, while for annual dimensions,
        previous period means previous year. Value should be a negative integer
        or 0. Default is 0.

    previous_period_offset : int, optional
        for Piotroski F-Score components that compare current period financial
        metrics to previous period metrics, how many periods to offset the
        previous period from the current period. If omitted, this defaults to
        -1 for Annual dimensions and -4 for Quarterly and TTM dimensions, meaning
        that the current period would be compared to the period 1 year earlier.
        Value should be a negative integer or 0.

    mask : zipline.pipeline.Filter, optional
        optional Filter to limit the F-Score computation to a subset of stocks.

    Returns
    -------
    zipline.pipeline.Factor
        a Factor that computes the Piotroski F-Score when executed

    Examples
    --------
    Compute the Piotroski F-Score for the most recent fiscal period, using
    trailing-twelve-month financials:

    >>> from zipline.pipeline.sharadar import PiotroskiFScore
    >>> f_score = PiotroskiFScore()
    """

    # F Score
    current_fundamentals = sharadar.Fundamentals.slice(
        dimension=dimension, period_offset=period_offset)
    if not previous_period_offset:
        # For quarterly and TTM, go back 4 periods; for yearly, go back 1
        previous_period_offset = -1 if dimension.endswith("Y") else -4
    previous_fundamentals = sharadar.Fundamentals.slice(
        dimension=dimension, period_offset=period_offset+previous_period_offset)

    return_on_assets = Latest(current_fundamentals.ROA, mask=mask)
    previous_return_on_assets = Latest(previous_fundamentals.ROA, mask=mask)
    total_assets = Latest(current_fundamentals.ASSETSAVG, mask=mask)
    previous_total_assets = Latest(previous_fundamentals.ASSETSAVG, mask=mask)
    operating_cash_flow = Latest(current_fundamentals.NCFO, mask=mask)
    debt = Latest(current_fundamentals.DEBTNC, mask=mask)
    previous_debt = Latest(previous_fundamentals.DEBTNC, mask=mask)
    current_ratio = Latest(current_fundamentals.CURRENTRATIO, mask=mask)
    previous_current_ratio = Latest(previous_fundamentals.CURRENTRATIO, mask=mask)
    shares_out = Latest(current_fundamentals.SHARESWA, mask=mask)
    previous_shares_out = Latest(previous_fundamentals.SHARESWA, mask=mask)
    gross_margin = Latest(current_fundamentals.GROSSMARGIN, mask=mask)
    previous_gross_margin = Latest(previous_fundamentals.GROSSMARGIN, mask=mask)
    asset_turnover = Latest(current_fundamentals.ASSETTURNOVER, mask=mask)
    previous_asset_turnover = Latest(previous_fundamentals.ASSETTURNOVER, mask=mask)

    f_scores = (
        (return_on_assets > 0).as_factor()
        + (operating_cash_flow > 0).as_factor()
        + (return_on_assets > previous_return_on_assets).as_factor()
        + (operating_cash_flow / total_assets > return_on_assets).as_factor()
        + ((debt / total_assets) < (previous_debt / previous_total_assets)).as_factor()
        + (current_ratio > previous_current_ratio).as_factor()
        + (shares_out <= previous_shares_out).as_factor()
        + (gross_margin > previous_gross_margin).as_factor()
        + (asset_turnover > previous_asset_turnover).as_factor()
    )

    return f_scores

def AltmanZScore(
    dimension: Literal['ARQ', 'ARY', 'ART', 'MRQ', 'MRY', 'MRT'] = "ART",
    period_offset: int = 0,
    mask: Filter = None
    ) -> Factor:
    """
    Return a Factor that computes the Altman Z-Score using Sharadar
    fundamentals. The Altman Z-Score measures the likelihood of
    future bankruptcy.

    The Altman Z-score formula is:

        Altman Z-Score = 1.2A + 1.4B + 3.3C + 0.6D + 1.0E

    Where:

    - A = working capital / total assets
    - B = retained earnings / total assets
    - C = earnings before interest and tax / total assets
    - D = market value of equity / total liabilities
    - E = sales / total assets

    Parameters
    ----------
    dimension : str, optional
        the type of reports to use. Choices are ARQ, ARY, ART, MRQ, MRY,
        MRT, where AR=As Reported, MR=Most Recent Reported, Q=Quarterly,
        Y=Annual, and T=Trailing Twelve Month. Default is ART.

    period_offset : int, optional
        which fiscal period to return Z-Scores for. If period_offset
        is 0, returns the most recent point-in-time Z-Scores. If period_offset
        is -1, returns Z-Scores for the prior fiscal period; if -2, two fiscal
        periods ago, etc. For quarterly and trailing-twelve-month dimensions,
        previous period means previous quarter, while for annual dimensions,
        previous period means previous year. Value should be a negative integer
        or 0. Default is 0.

    mask : zipline.pipeline.Filter, optional
        optional Filter to limit the Z-Score computation to a subset of stocks.

    Returns
    -------
    zipline.pipeline.Factor
        a Factor that computes the Altman Z-Score when executed

    Examples
    --------
    Compute the Altman Z-Score using trailing-twelve-month financials:

    >>> from zipline.pipeline.sharadar import AltmanZScore
    >>> altman_zscore = AltmanZScore()
    """

    fundamentals = sharadar.Fundamentals.slice(
        dimension=dimension, period_offset=period_offset)

    working_capital = Latest(fundamentals.WORKINGCAPITAL, mask=mask)
    total_assets = Latest(fundamentals.ASSETS, mask=mask)
    retained_earnings = Latest(fundamentals.RETEARN, mask=mask)
    ebit = Latest(fundamentals.EBIT, mask=mask)
    marketcap = Latest(fundamentals.MARKETCAP, mask=mask)
    total_liabilities = Latest(fundamentals.LIABILITIES, mask=mask)
    revenue = Latest(fundamentals.REVENUE, mask=mask)

    a = working_capital / total_assets
    b = retained_earnings / total_assets
    c = ebit / total_assets
    d = marketcap / total_liabilities
    e = revenue / total_assets

    z_scores = (
        1.2	* a
        + 1.4 * b
        + 3.3 *	c
        + 0.6 * d
        + 1.0 * e
    )

    return z_scores

def InterestCoverageRatio(
    dimension: Literal['ARQ', 'ARY', 'ART', 'MRQ', 'MRY', 'MRT'] = "ART",
    period_offset: int = 0,
    mask: Filter = None
    ) -> Factor:
    """
    Return a Factor that computes the Interest Coverage Ratio (ICR) using
    Sharadar fundamentals. The Interest Coverage Ratio measures a
    company's ability to service its debt.

    Interest coverage ratio is calculated as EBIT (earnings before interest,
    and taxes) divided by interest expense. The ratio shows how many times
    a company could cover its interest expense using current earnings.

    Interest coverage ratio is only computed for companies with positive
    earnings and interest expense. For companies with negative earnings
    or no interest, this Factor returns nulls.

    Parameters
    ----------
    dimension : str, optional
        the type of reports to use. Choices are ARQ, ARY, ART, MRQ, MRY,
        MRT, where AR=As Reported, MR=Most Recent Reported, Q=Quarterly,
        Y=Annual, and T=Trailing Twelve Month. Default is ART.

    period_offset : int, optional
        which fiscal period to return ICR for. If period_offset
        is 0, returns the most recent point-in-time ICR. If period_offset
        is -1, returns ICR for the prior fiscal period; if -2, two fiscal
        periods ago, etc. For quarterly and trailing-twelve-month dimensions,
        previous period means previous quarter, while for annual dimensions,
        previous period means previous year. Value should be a negative integer
        or 0. Default is 0.

    mask : zipline.pipeline.Filter, optional
        optional Filter to limit the ICR computation to a subset of stocks.

    Returns
    -------
    zipline.pipeline.Factor
        a Factor that computes the ICR when executed

    Examples
    --------
    Compute the interest coverage ratio:

    >>> from zipline.pipeline.sharadar import InterestCoverageRatio
    >>> icr = InterestCoverageRatio()
    """
    fundamentals = sharadar.Fundamentals.slice(
        dimension=dimension, period_offset=period_offset)

    intexp = Latest(fundamentals.INTEXP, mask=mask)
    ebit = Latest(fundamentals.EBIT, mask=mask)

    # Only compute ICR for companies that have positive EBIT
    # and interest
    computable = (intexp > 0) & (ebit > 0)
    icr = Latest(fundamentals.EBIT, mask=computable) /  Latest(fundamentals.INTEXP, mask=computable)
    return icr
