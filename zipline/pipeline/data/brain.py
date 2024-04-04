# Copyright 2024 QuantRocket LLC - All Rights Reserved
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

from typing import Literal, TYPE_CHECKING
from zipline.utils.numpy_utils import (
    float64_dtype,
    datetime64ns_dtype,
    object_dtype,
    NaTD)
from zipline.pipeline.data import (
    Column,
    DataSet,
    DataSetFamily
)
from zipline.pipeline.domain import Domain, US_EQUITIES

if TYPE_CHECKING:
    from zipline.pipeline.data.dataset import (
        BoundFloatColumn,
        BoundDatetimeColumn,
        BoundObjectColumn,
    )

class BSI(DataSetFamily):
    """
    DataSetFamily representing Brain Sentiment Indicator (BSI) data.

    This dataset provides news sentiment scores for US stocks, with history
    back to August 2, 2016.

    The sentiment scores are averaged using news articles published over the last
    1, 7, or 30 days. To use the data in a pipeline, it must first be sliced by
    selecting the calculation window using the `N` dimension. For example, to
    select the 7-day sentiment scores, use `BSI.slice(7)`.

    Attributes
    ----------
    VOLUME : float
        Number of news articles detected in the previous $N days for the
        company.

    VOLUME_SENTIMENT : float
        Number of news articles in the previous $N days used to calculate
        the sentiment. This number is less or equal to the field VOLUME and
        corresponds to not neutral news according to the sentiment algorithm.

    SENTIMENT_SCORE : float
        Sentiment score from -1 to 1 where 1 is the most positive and -1 the
        most negative. The sentiment score is calculated as an average of
        sentiment of news articles collected in the previous $N days for the
        specific company.

    BUZZ_VOLUME : float
        Buzz score that quantifies how much attention in terms of news VOLUME
        one company is receiving compared to the past. This is calculated by
        considering the VOLUME distribution of past six months. Then the buzz
        is calculated as current VOLUME minus the average of VOLUME for past
        6 months in units of standard deviations. A value close to 0 means
        that the stock is covered by a VOLUME of stories similar to its past
        average, a value larger than 0 gives how many standard deviations the
        current VOLUME is larger than average. The value is reported only if
        there are enough stories in the past to estimate a reliable value.

    BUZZ_VOLUME_SENTIMENT : float
        Buzz score that quantifies how much attention in terms of news
        VOLUME_SENTIMENT (only stories with a polarized sentiment) one stock
        is receiving compared to the past. This is calculated by considering
        the VOLUME_SENTIMENT distribution of past six months. The buzz is then
        calculated as current VOLUME_SENTIMENT minus the average of
        VOLUME_SENTIMENT for past 6 months in units of standard deviations.
        A value close to 0 means that the stock is covered by a VOLUME_SENTIMENT
        of stories (sentiment bearing story) similar to its past average, a
        value larger than 0 gives how many standard deviations the current
        VOLUME_SENTIMENT is larger than average. The value is reported only if
        there are enough stories in the past to estimate a reliable value.

    Notes
    -----
    Usage Guide:

    * Brain Sentiment Indicator: https://qrok.it/dl/z/pipeline-brain-bsi
    * Pipeline data concepts: https://qrok.it/dl/z/pipeline-data-concepts

    Examples
    --------
    Select the top 100 stocks by 7-day sentiment score::

        top_sentiment = brain.BSI.slice(7).SENTIMENT_SCORE.latest.top(100)
    """

    extra_dims = [
        ('N', {1, 7, 30}),
    ]

    domain: Domain = US_EQUITIES

    VOLUME: 'BoundFloatColumn' = Column(float64_dtype)
    """Number of news articles detected in the previous $N days for the company."""
    VOLUME_SENTIMENT: 'BoundFloatColumn' = Column(float64_dtype)
    """Number of news articles in the previous $N days used to calculate the sentiment. This number is less or equal to the field VOLUME and corresponds to not neutral news according to the sentiment algorithm."""
    SENTIMENT_SCORE: 'BoundFloatColumn' = Column(float64_dtype)
    """Sentiment score from -1 to 1 where 1 is the most positive and -1 the most negative. The sentiment score is calculated as an average of sentiment of news articles collected in the previous $N days for the specific company."""
    BUZZ_VOLUME: 'BoundFloatColumn' = Column(float64_dtype)
    """Buzz score that quantifies how much attention in terms of news VOLUME one company is receiving compared to the past. This is calculated by considering the VOLUME distribution of past six months. Then the buzz is calculated as current VOLUME minus the average of VOLUME for past 6 months in units of standard deviations. A value close to 0 means that the stock is covered by a VOLUME of stories similar to its past average, a value larger than 0 gives how many standard deviations the current VOLUME is larger than average. The value is reported only if there are enough stories in the past to estimate a reliable value."""
    BUZZ_VOLUME_SENTIMENT: 'BoundFloatColumn' = Column(float64_dtype)
    """Buzz score that quantifies how much attention in terms of news VOLUME_SENTIMENT (only stories with a polarized sentiment) one stock is receiving compared to the past. This is calculated by considering the VOLUME_SENTIMENT distribution of past six months. The buzz is then calculated as current VOLUME_SENTIMENT minus the average of VOLUME_SENTIMENT for past 6 months in units of standard deviations. A value close to 0 means that the stock is covered by a VOLUME_SENTIMENT of stories (sentiment bearing story) similar to its past average, a value larger than 0 gives how many standard deviations the current VOLUME_SENTIMENT is larger than average. The value is reported only if there are enough stories in the past to estimate a reliable value."""

    @classmethod
    def slice(
        cls,
        N: Literal[1, 7, 30],
        ) -> 'BSI':
        """
        Return a Brain Sentiment Indicator (BSI) DataSet tied to a particular
        calculation window.

        Parameters
        ----------
        N : int, required
            the number of days over which sentiment is calculated. Choices are
            1, 7, or 30.

        Returns
        -------
        DataSet
            Brain Sentiment Indicator (BSI) DataSet with the specified N.

        Notes
        -----
        Usage Guide:

        * Brain Sentiment Indicator: https://qrok.it/dl/z/pipeline-brain-bsi
        * Pipeline data concepts: https://qrok.it/dl/z/pipeline-data-concepts

        Examples
        --------
        Select the top 100 stocks by 7-day sentiment score::

            top_sentiment = brain.BSI.slice(7).SENTIMENT_SCORE.latest.top(100)
        """
        return super().slice(N=N)

class BLMCF(DataSetFamily):
    """
    DataSetFamily representing Brain Language Metrics on Company Filings (BLMCF) data.

    This dataset provides sentiment scores and other language metrics for
    10-K and 10-Q company filings for US stocks, with history back to
    January 1, 2010.

    To use the data in a pipeline, it must first be sliced by selecting the desired
    report category (10-K, 10-Q, or both) using the `report_category` dimension.
    To include both 10-K and 10-Q reports, slice the DataSetFamily without specifying
    a report category: `BLMCF.slice()`. For 10-K reports only, use:
    `BLMCF.slice(report_category='10-K')`

    Language metrics are calculated separately for the Risk Factors section
    of the report (columns starting with RF), the Management Discussion and
    Analysis section (columns starting with MD), and the report as a whole
    (columns not starting with RF or MD). Columns containing "DELTA" or
    "SIMILARITY" in the name compare the current report with the previous
    report of the same period and category.

    Attributes
    ----------
    LAST_REPORT_CATEGORY : str
        The category of the last available report. It can be either "10-K" or "10-Q".

    LAST_REPORT_DATE : datetime
        The date of last report (with respect to the record's Date) issued by the
        company in YYYY-MM-DD format.

    N_SENTENCES : float
        Number of sentences extracted from the last available report.

    MEAN_SENTENCE_LENGTH : float
        The mean sentence length measured in terms of the mean number of words per
        sentence for the last available report.

    SENTIMENT : float
        The financial sentiment of the last available report.

    SCORE_UNCERTAINTY : float
        The percentage of financial domain "uncertainty" language present in the
        last report.

    SCORE_LITIGIOUS : float
        The percentage of financial domain "litigious" language present in the last
        report.

    SCORE_CONSTRAINING : float
        The percentage of financial domain "constraining" language present in the
        last report.

    SCORE_INTERESTING : float
        The percentage of financial domain "interesting" language present in the
        last report.

    READABILITY : float
        Reading grade level for the the report expressed by a number corresponding
        to US education grade. The score is obtained from the average of various
        readability tests to measure how difficult is the text to understand
        (e.g. Gunning Fog Index).

    LEXICAL_RICHNESS : float
        Lexical richness measured in terms of the Type-Token Ratio (TTR) which
        calculates the number of types (total number of words) divided by the
        number of tokens (number of unique words). The basic logic behind this
        measure is that if the text is more complex, the author uses a more varied
        vocabulary

    LEXICAL_DENSITY : float
        Lexical density to measure the text complexity by computing the ratio
        between number of lexical words (nouns, adjectives, lexical verbs, adverbs)
        divided by the total number of words in the document.

    SPECIFIC_DENSITY : float
        Percentage of words belonging to the specific dictionary used for company
        filings analysis present in the last available report.

    RF_N_SENTENCES : float
        Number of sentences extracted from the "Risk Factors" section of the last
        available report.

    RF_MEAN_SENTENCE_LENGTH : float
        The mean sentence length measured in terms of the mean number of words per
        sentence for the "Risk Factors" section of the last available report.

    RF_SENTIMENT : float
        The financial sentiment for the "Risk Factors" section of the last available
        report.

    RF_SCORE_UNCERTAINTY : float
        The percentage of financial domain "uncertainty" language present in the
        "Risk Factors" section of the last report.

    RF_SCORE_LITIGIOUS : float
        The percentage of financial domain "litigious" language present in the
        "Risk Factors" section of the last report.

    RF_SCORE_CONSTRAINING : float
        The percentage of financial domain "constraining" language present in the
        "Risk Factors" section of the last report.

    RF_SCORE_INTERESTING : float
        The percentage of financial domain "interesting" language present in the
        "Risk Factors" section of the last report.

    RF_READABILITY : float
        Reading grade level for the "Risk Factors" section of the report expressed
        by a number corresponding to US education grade. The score is obtained from
        the average of various readability tests to measure how difficult is the
        text to understand (e.g. Gunning Fog Index).

    RF_LEXICAL_RICHNESS : float
        Lexical richness for the "Risk Factors" section of the last available report,
        measured in terms of the Type-Token Ratio (TTR) which calculates the number
        of types (total number of words) divided by the number of tokens (number of
        unique words).

    RF_LEXICAL_DENSITY : float
        Lexical density for the "Risk Factors" section of the last available report.
        Measures the text complexity by computing the ratio between number of lexical
        words (nouns, adjectives, lexical verbs, adverbs) divided by the total number
        of words in the document.

    RF_SPECIFIC_DENSITY : float
        Percentage of words belonging to the specific dictionary used for company
        filings analysis present in the "Risk Factors" section of the last available
        report.

    MD_N_SENTENCES : float
        Number of sentences extracted from the MD&A section of the last available report.

    MD_MEAN_SENTENCE_LENGTH : float
        The mean sentence length measured in terms of the mean number of words per
        sentence for the MD&A section of the last available report.

    MD_SENTIMENT : float
        The financial sentiment for the MD&A section of the last available report.

    MD_SCORE_UNCERTAINTY : float
        The percentage of financial domain "uncertainty" language present in the
        MD&A section of the last report.

    MD_SCORE_LITIGIOUS : float
        The percentage of financial domain "litigious" language present in the
        MD&A section of the last report.

    MD_SCORE_CONSTRAINING : float
        The percentage of financial domain "constraining" language present in the
        MD&A section of the last report.

    MD_SCORE_INTERESTING : float
        The percentage of financial domain "interesting" language present in the
        MD&A section of the last report.

    MD_READABILITY : float
        Reading grade level for the MD&A section of the report expressed by a number
        corresponding to US education grade. The score is obtained from the average
        of various readability tests to measure how difficult is the text to understand
        (e.g. Gunning Fog Index).

    MD_LEXICAL_RICHNESS : float
        Lexical richness for the MD&A section of the last available report, measured
        in terms of the Type-Token Ratio (TTR) which calculates the number of types
        (total number of words) divided by the number of tokens (number of unique words).

    MD_LEXICAL_DENSITY : float
        Lexical density for the MD&A section of the last available report. Measures
        the text complexity by computing the ratio between number of lexical words
        (nouns, adjectives, lexical verbs, adverbs) divided by the total number of
        words in the document.

    MD_SPECIFIC_DENSITY : float
        Percentage of words belonging to the specific dictionary used for company
        filings analysis present in the MD&A section of the last available report.

    LAST_REPORT_PERIOD : float
        The period of the last available report. For 10-K annual reports this is an
        integer number labelling the annual reports. For 10-Q quarterly reports this
        an integer number from 1 to 3 labelling the period report. This is used to
        perform differences between reports of the same period.

    PREV_REPORT_DATE : datetime
        The date of the previous report.

    PREV_REPORT_CATEGORY : str
        The category of the previous report. It can be either "10-K" or "10-Q".

    PREV_REPORT_PERIOD : float
        The period of the previous report. For 10-K annual reports this is an integer
        number labelling the annual reports. For 10-Q quarterly reports this an integer
        number from 1 to 3 labelling the period report. This is used to perform
        differences between reports of the same period.

    DELTA_PERC_N_SENTENCES : float
        Percentage change of the number of sentences between the last available report
        and the previous report of same period and category.

    DELTA_PERC_MEAN_SENTENCE_LENGTH : float
        Percentage change of sentence length (mean number of words per sentence) between
        the last available report and the previous report of same period and category.

    DELTA_SENTIMENT : float
        The difference of financial sentiment between the last available report and the
        previous report of same period and category.

    DELTA_SCORE_UNCERTAINTY : float
        The difference of percentage of financial domain "uncertainty" language between
        the last available report and the previous report of same period and category.

    DELTA_SCORE_LITIGIOUS : float
        The difference of percentage of financial domain "litigious" language between the
        last available report and the previous report of same period and category.

    DELTA_SCORE_CONSTRAINING : float
        The difference of percentage of financial domain "constraining" language between
        the last available report and the previous report of same period and category.

    DELTA_SCORE_INTERESTING : float
        The difference of percentage of financial domain "interesting" language between
        the last available report and the previous report of same period and category.

    DELTA_READABILITY : float
        The difference of reading grade level between the last available report and the
        previous report of same period and category.

    DELTA_LEXICAL_RICHNESS : float
        The difference of lexical richness between the last available report and the
        previous report of same period and category.

    DELTA_LEXICAL_DENSITY : float
        The difference of lexical density between the last available report and the
        previous report of same period and category.

    DELTA_SPECIFIC_DENSITY : float
        The difference of percentage of words belonging to the specific dictionary used
        for company filings analysis between the last available report and the previous
        report of same period and category.

    SIMILARITY_ALL : float
        The language similarity between the last available report and the previous report
        of same period and category.

    SIMILARITY_POSITIVE : float
        The similarity in terms of financial domain "positive" language between the last
        available report and the previous report of same period and category.

    SIMILARITY_NEGATIVE : float
        The similarity in terms of financial domain "negative" language between the last
        available report and the previous report of same period and category.

    SIMILARITY_UNCERTAINTY : float
        The similarity in terms of financial domain "uncertainty" language between the last
        available report and the previous report of same period and category.

    SIMILARITY_LITIGIOUS : float
        The similarity in terms of financial domain "litigious" language between the last
        available report and the previous report of same period and category.

    SIMILARITY_CONSTRAINING : float
        The similarity in terms of financial domain "constraining" language between the last
        available report and the previous report of same period and category.

    SIMILARITY_INTERESTING : float
        The similarity in terms of financial domain "interesting" language between the last
        available report and the previous report of same period and category.

    RF_DELTA_PERC_N_SENTENCES : float
        Percentage change of the number of sentences in the "Risk Factors" section between
        the last available report and the previous report of same period and category.

    RF_DELTA_PERC_MEAN_SENTENCE_LENGTH : float
        Percentage change of sentence length (mean number of words per sentence) in the
        "Risk Factors" section between the last available report and the previous report
        of same period and category.

    RF_DELTA_SENTIMENT : float
        The difference of financial sentiment in the "Risk Factors" section between the
        last available report and the previous report of same period and category.

    RF_DELTA_SCORE_UNCERTAINTY : float
        The difference of percentage of financial domain "uncertainty" language in the
        "Risk Factors" section between the last available report and the previous report
        of same period and category.

    RF_DELTA_SCORE_LITIGIOUS : float
        The difference of percentage of financial domain "litigious" language in the
        "Risk Factors" section between the last available report and the previous report
        of same period and category.

    RF_DELTA_SCORE_CONSTRAINING : float
        The difference of percentage of financial domain "constraining" language in the
        "Risk Factors" section between the last available report and the previous report
        of same period and category.

    RF_DELTA_SCORE_INTERESTING : float
        The difference of percentage of financial domain "interesting" language in the
        "Risk Factors" section between the last available report and the previous report
        of same period and category.

    RF_DELTA_READABILITY : float
        The difference of reading grade level in the "Risk Factors" section between the
        last available report and the previous report of same period and category.

    RF_DELTA_LEXICAL_RICHNESS : float
        The difference of lexical richness in the "Risk Factors" section between the last
        available report and the previous report of same period and category.

    RF_DELTA_LEXICAL_DENSITY : float
        The difference of lexical density in the "Risk Factors" section between the last
        available report and the previous report of same period and category.

    RF_DELTA_SPECIFIC_DENSITY : float
        The difference of percentage of words belonging to the specific dictionary used for
        company filings analysis in the "Risk Factors" section between the last available
        report and the previous report of same period and category.

    RF_SIMILARITY_ALL : float
        The language similarity in the "Risk Factors" section between the last available
        report and the previous report of same period and category.

    RF_SIMILARITY_POSITIVE : float
        The similarity in terms of financial domain "positive" language in the "Risk Factors"
        section between the last available report and the previous report of same period and
        category.

    RF_SIMILARITY_NEGATIVE : float
        The similarity in terms of financial domain "negative" language in the "Risk Factors"
        section between the last available report and the previous report of same period and
        category.

    MD_DELTA_PERC_N_SENTENCES : float
        Percentage change of the number of sentences in the MD&A section between the last
        available report and the previous report of same period and category.

    MD_DELTA_PERC_MEAN_SENTENCE_LENGTH : float
        Percentage change of sentence length (mean number of words per sentence) in the MD&A
        section between the last available report and the previous report of same period and
        category.

    MD_DELTA_SENTIMENT : float
        The difference of financial sentiment in the MD&A section between the last available
        report and the previous report of same period and category.

    MD_DELTA_SCORE_UNCERTAINTY : float
        The difference of percentage of financial domain "uncertainty" language in the MD&A
        section between the last available report and the previous report of same period and
        category.

    MD_DELTA_SCORE_LITIGIOUS : float
        The difference of percentage of financial domain "litigious" language in the MD&A
        section between the last available report and the previous report of same period and
        category.

    MD_DELTA_SCORE_CONSTRAINING : float
        The difference of percentage of financial domain "constraining" language in the MD&A
        section between the last available report and the previous report of same period and
        category.

    MD_DELTA_SCORE_INTERESTING : float
        The difference of percentage of financial domain "interesting" language in the MD&A
        section between the last available report and the previous report of same period an
        category.

    MD_DELTA_READABILITY : float
        The difference of reading grade level in the MD&A section between the last available
        report and the previous report of same period and category.

    MD_DELTA_LEXICAL_RICHNESS : float
        The difference of lexical richness in the MD&A section between the last available report
        and the previous report of same period and category.

    MD_DELTA_LEXICAL_DENSITY : float
        The difference of lexical density in the MD&A section between the last available report
        and the previous report of same period and category.

    MD_DELTA_SPECIFIC_DENSITY : float
        The difference of percentage of words belonging to the specific dictionary used for
        company filings analysis in the MD&A section between the last available report and the
        previous report of same period and category.

    MD_SIMILARITY_ALL : float
        The language similarity in the MD&A section between the last available report and the
        previous report of same period and category.

    MD_SIMILARITY_POSITIVE : float
        The similarity in terms of financial domain "positive" language in the MD&A section
        between the last available report and the previous report of same period and category.

    MD_SIMILARITY_NEGATIVE : float
        The similarity in terms of financial domain "negative" language in the MD&A section
        between the last available report and the previous report of same period and category.

    Notes
    -----
    Usage Guide:

    * Brain Language Metrics on Company Filings: https://qrok.it/dl/z/pipeline-brain-blmcf
    * Pipeline data concepts: https://qrok.it/dl/z/pipeline-data-concepts

    Examples
    --------
    Select the top 100 stocks by sentiment score of the latest company filing::

        top_sentiment = brain.BLMCF.slice().SENTIMENT.latest.top(100)

    Select the top 100 stocks by sentiment score of the latest 10-K filing::

        top_sentiment = brain.BLMCF.slice(report_category='10-K').SENTIMENT.latest.top(100)
    """

    extra_dims = [
        ('report_category', {'10-K', '10-Q', None}, None),
    ]

    domain: Domain = US_EQUITIES

    LAST_REPORT_CATEGORY: 'BoundObjectColumn' = Column(object_dtype)
    """The category of the last available report. It can be either "10-K" or "10-Q"."""
    LAST_REPORT_DATE: 'BoundDatetimeColumn' = Column(datetime64ns_dtype)
    """The date of last report (with respect to the record's Date) issued by the company in YYYY-MM-DD format."""
    N_SENTENCES: 'BoundFloatColumn' = Column(float64_dtype)
    """Number of sentences extracted from the last available report."""
    MEAN_SENTENCE_LENGTH: 'BoundFloatColumn' = Column(float64_dtype)
    """The mean sentence length measured in terms of the mean number of words per sentence for the last available report."""
    SENTIMENT: 'BoundFloatColumn' = Column(float64_dtype)
    """The financial sentiment of the last available report."""
    SCORE_UNCERTAINTY: 'BoundFloatColumn' = Column(float64_dtype)
    """The percentage of financial domain "uncertainty" language present in the last report."""
    SCORE_LITIGIOUS: 'BoundFloatColumn' = Column(float64_dtype)
    """The percentage of financial domain "litigious" language present in the last report."""
    SCORE_CONSTRAINING: 'BoundFloatColumn' = Column(float64_dtype)
    """The percentage of financial domain "constraining" language present in the last report."""
    SCORE_INTERESTING: 'BoundFloatColumn' = Column(float64_dtype)
    """The percentage of financial domain "interesting" language present in the last report."""
    READABILITY: 'BoundFloatColumn' = Column(float64_dtype)
    """Reading grade level for the the report expressed by a number corresponding to US education grade. The score is obtained from the average of various readability tests to measure how difficult is the text to understand (e.g. Gunning Fog Index)."""
    LEXICAL_RICHNESS: 'BoundFloatColumn' = Column(float64_dtype)
    """Lexical richness measured in terms of the Type-Token Ratio (TTR) which calculates the number of types (total number of words) divided by the number of tokens (number of unique words). The basic logic behind this measure is that if the text is more complex, the author uses a more varied vocabulary"""
    LEXICAL_DENSITY: 'BoundFloatColumn' = Column(float64_dtype)
    """Lexical density to measure the text complexity by computing the ratio between number of lexical words (nouns, adjectives, lexical verbs, adverbs) divided by the total number of words in the document."""
    SPECIFIC_DENSITY: 'BoundFloatColumn' = Column(float64_dtype)
    """Percentage of words belonging to the specific dictionary used for company filings analysis present in the last available report."""
    RF_N_SENTENCES: 'BoundFloatColumn' = Column(float64_dtype)
    """Number of sentences extracted from the "Risk Factors" section of the last available report."""
    RF_MEAN_SENTENCE_LENGTH: 'BoundFloatColumn' = Column(float64_dtype)
    """The mean sentence length measured in terms of the mean number of words per sentence for the "Risk Factors" section of the last available report."""
    RF_SENTIMENT: 'BoundFloatColumn' = Column(float64_dtype)
    """The financial sentiment for the "Risk Factors" section of the last available report."""
    RF_SCORE_UNCERTAINTY: 'BoundFloatColumn' = Column(float64_dtype)
    """The percentage of financial domain "uncertainty" language present in the "Risk Factors" section of the last report."""
    RF_SCORE_LITIGIOUS: 'BoundFloatColumn' = Column(float64_dtype)
    """The percentage of financial domain "litigious" language present in the "Risk Factors" section of the last report."""
    RF_SCORE_CONSTRAINING: 'BoundFloatColumn' = Column(float64_dtype)
    """The percentage of financial domain "constraining" language present in the "Risk Factors" section of the last report."""
    RF_SCORE_INTERESTING: 'BoundFloatColumn' = Column(float64_dtype)
    """The percentage of financial domain "interesting" language present in the "Risk Factors" section of the last report."""
    RF_READABILITY: 'BoundFloatColumn' = Column(float64_dtype)
    """Reading grade level for the "Risk Factors" section of the report expressed by a number corresponding to US education grade. The score is obtained from the average of various readability tests to measure how difficult is the text to understand (e.g. Gunning Fog Index)."""
    RF_LEXICAL_RICHNESS: 'BoundFloatColumn' = Column(float64_dtype)
    """Lexical richness for the "Risk Factors" section of the last available report, measured in terms of the Type-Token Ratio (TTR) which calculates the number of types (total number of words) divided by the number of tokens (number of unique words)."""
    RF_LEXICAL_DENSITY: 'BoundFloatColumn' = Column(float64_dtype)
    """Lexical density for the "Risk Factors" section of the last available report. Measures the text complexity by computing the ratio between number of lexical words (nouns, adjectives, lexical verbs, adverbs) divided by the total number of words in the document."""
    RF_SPECIFIC_DENSITY: 'BoundFloatColumn' = Column(float64_dtype)
    """Percentage of words belonging to the specific dictionary used for company filings analysis present in the "Risk Factors" section of the last available report."""
    MD_N_SENTENCES: 'BoundFloatColumn' = Column(float64_dtype)
    """Number of sentences extracted from the MD&A section of the last available report."""
    MD_MEAN_SENTENCE_LENGTH: 'BoundFloatColumn' = Column(float64_dtype)
    """The mean sentence length measured in terms of the mean number of words per sentence for the MD&A section of the last available report."""
    MD_SENTIMENT: 'BoundFloatColumn' = Column(float64_dtype)
    """The financial sentiment for the MD&A section of the last available report."""
    MD_SCORE_UNCERTAINTY: 'BoundFloatColumn' = Column(float64_dtype)
    """The percentage of financial domain "uncertainty" language present in the MD&A section of the last report."""
    MD_SCORE_LITIGIOUS: 'BoundFloatColumn' = Column(float64_dtype)
    """The percentage of financial domain "litigious" language present in the MD&A section of the last report."""
    MD_SCORE_CONSTRAINING: 'BoundFloatColumn' = Column(float64_dtype)
    """The percentage of financial domain "constraining" language present in the MD&A section of the last report."""
    MD_SCORE_INTERESTING: 'BoundFloatColumn' = Column(float64_dtype)
    """The percentage of financial domain "interesting" language present in the MD&A section of the last report."""
    MD_READABILITY: 'BoundFloatColumn' = Column(float64_dtype)
    """Reading grade level for the MD&A section of the report expressed by a number corresponding to US education grade. The score is obtained from the average of various readability tests to measure how difficult is the text to understand (e.g. Gunning Fog Index)."""
    MD_LEXICAL_RICHNESS: 'BoundFloatColumn' = Column(float64_dtype)
    """Lexical richness for the MD&A section of the last available report, measured in terms of the Type-Token Ratio (TTR) which calculates the number of types (total number of words) divided by the number of tokens (number of unique words)."""
    MD_LEXICAL_DENSITY: 'BoundFloatColumn' = Column(float64_dtype)
    """Lexical density for the MD&A section of the last available report. Measures the text complexity by computing the ratio between number of lexical words (nouns, adjectives, lexical verbs, adverbs) divided by the total number of words in the document."""
    MD_SPECIFIC_DENSITY: 'BoundFloatColumn' = Column(float64_dtype)
    """Percentage of words belonging to the specific dictionary used for company filings analysis present in the MD&A section of the last available report."""
    LAST_REPORT_PERIOD: 'BoundFloatColumn' = Column(float64_dtype)
    """The period of the last available report. For 10-K annual reports this is an integer number labelling the annual reports. For 10-Q quarterly reports this an integer number from 1 to 3 labelling the period report. This is used to perform differences between reports of the same period."""
    PREV_REPORT_DATE: 'BoundDatetimeColumn' = Column(datetime64ns_dtype)
    """The date of the previous report."""
    PREV_REPORT_CATEGORY: 'BoundObjectColumn' = Column(object_dtype)
    """The category of the previous report. It can be either "10-K" or "10-Q"."""
    PREV_REPORT_PERIOD: 'BoundFloatColumn' = Column(float64_dtype)
    """The period of the previous report. For 10-K annual reports this is an integer number labelling the annual reports. For 10-Q quarterly reports this an integer number from 1 to 3 labelling the period report. This is used to perform differences between reports of the same period."""
    DELTA_PERC_N_SENTENCES: 'BoundFloatColumn' = Column(float64_dtype)
    """Percentage change of the number of sentences between the last available report and the previous report of same period and category."""
    DELTA_PERC_MEAN_SENTENCE_LENGTH: 'BoundFloatColumn' = Column(float64_dtype)
    """Percentage change of sentence length (mean number of words per sentence) between the last available report and the previous report of same period and category."""
    DELTA_SENTIMENT: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of financial sentiment between the last available report and the previous report of same period and category."""
    DELTA_SCORE_UNCERTAINTY: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of percentage of financial domain "uncertainty" language between the last available report and the previous report of same period and category."""
    DELTA_SCORE_LITIGIOUS: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of percentage of financial domain "litigious" language between the last available report and the previous report of same period and category."""
    DELTA_SCORE_CONSTRAINING: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of percentage of financial domain "constraining" language between the last available report and the previous report of same period and category."""
    DELTA_SCORE_INTERESTING: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of percentage of financial domain "interesting" language between the last available report and the previous report of same period and category."""
    DELTA_READABILITY: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of reading grade level between the last available report and the previous report of same period and category."""
    DELTA_LEXICAL_RICHNESS: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of lexical richness between the last available report and the previous report of same period and category."""
    DELTA_LEXICAL_DENSITY: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of lexical density between the last available report and the previous report of same period and category."""
    DELTA_SPECIFIC_DENSITY: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of percentage of words belonging to the specific dictionary used for company filings analysis between the last available report and the previous report of same period and category."""
    SIMILARITY_ALL: 'BoundFloatColumn' = Column(float64_dtype)
    """The language similarity between the last available report and the previous report of same period and category."""
    SIMILARITY_POSITIVE: 'BoundFloatColumn' = Column(float64_dtype)
    """The similarity in terms of financial domain "positive" language between the last available report and the previous report of same period and category."""
    SIMILARITY_NEGATIVE: 'BoundFloatColumn' = Column(float64_dtype)
    """The similarity in terms of financial domain "negative" language between the last available report and the previous report of same period and category."""
    SIMILARITY_UNCERTAINTY: 'BoundFloatColumn' = Column(float64_dtype)
    """The similarity in terms of financial domain "uncertainty" language between the last available report and the previous report of same period and category."""
    SIMILARITY_LITIGIOUS: 'BoundFloatColumn' = Column(float64_dtype)
    """The similarity in terms of financial domain "litigious" language between the last available report and the previous report of same period and category."""
    SIMILARITY_CONSTRAINING: 'BoundFloatColumn' = Column(float64_dtype)
    """The similarity in terms of financial domain "constraining" language between the last available report and the previous report of same period and category."""
    SIMILARITY_INTERESTING: 'BoundFloatColumn' = Column(float64_dtype)
    """The similarity in terms of financial domain "interesting" language between the last available report and the previous report of same period and category."""
    RF_DELTA_PERC_N_SENTENCES: 'BoundFloatColumn' = Column(float64_dtype)
    """Percentage change of the number of sentences in the "Risk Factors" section between the last available report and the previous report of same period and category."""
    RF_DELTA_PERC_MEAN_SENTENCE_LENGTH: 'BoundFloatColumn' = Column(float64_dtype)
    """Percentage change of sentence length (mean number of words per sentence) in the "Risk Factors" section between the last available report and the previous report of same period and category."""
    RF_DELTA_SENTIMENT: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of financial sentiment in the "Risk Factors" section between the last available report and the previous report of same period and category."""
    RF_DELTA_SCORE_UNCERTAINTY: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of percentage of financial domain "uncertainty" language in the "Risk Factors" section between the last available report and the previous report of same period and category."""
    RF_DELTA_SCORE_LITIGIOUS: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of percentage of financial domain "litigious" language in the "Risk Factors" section between the last available report and the previous report of same period and category."""
    RF_DELTA_SCORE_CONSTRAINING: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of percentage of financial domain "constraining" language in the "Risk Factors" section between the last available report and the previous report of same period and category."""
    RF_DELTA_SCORE_INTERESTING: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of percentage of financial domain "interesting" language in the "Risk Factors" section between the last available report and the previous report of same period and category."""
    RF_DELTA_READABILITY: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of reading grade level in the "Risk Factors" section between the last available report and the previous report of same period and category."""
    RF_DELTA_LEXICAL_RICHNESS: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of lexical richness in the "Risk Factors" section between the last available report and the previous report of same period and category."""
    RF_DELTA_LEXICAL_DENSITY: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of lexical density in the "Risk Factors" section between the last available report and the previous report of same period and category."""
    RF_DELTA_SPECIFIC_DENSITY: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of percentage of words belonging to the specific dictionary used for company filings analysis in the "Risk Factors" section between the last available report and the previous report of same period and category."""
    RF_SIMILARITY_ALL: 'BoundFloatColumn' = Column(float64_dtype)
    """The language similarity in the "Risk Factors" section between the last available report and the previous report of same period and category."""
    RF_SIMILARITY_POSITIVE: 'BoundFloatColumn' = Column(float64_dtype)
    """The similarity in terms of financial domain "positive" language in the "Risk Factors" section between the last available report and the previous report of same period and category."""
    RF_SIMILARITY_NEGATIVE: 'BoundFloatColumn' = Column(float64_dtype)
    """The similarity in terms of financial domain "negative" language in the "Risk Factors" section between the last available report and the previous report of same period and category."""
    MD_DELTA_PERC_N_SENTENCES: 'BoundFloatColumn' = Column(float64_dtype)
    """Percentage change of the number of sentences in the MD&A section between the last available report and the previous report of same period and category."""
    MD_DELTA_PERC_MEAN_SENTENCE_LENGTH: 'BoundFloatColumn' = Column(float64_dtype)
    """Percentage change of sentence length (mean number of words per sentence) in the MD&A section between the last available report and the previous report of same period and category."""
    MD_DELTA_SENTIMENT: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of financial sentiment in the MD&A section between the last available report and the previous report of same period and category."""
    MD_DELTA_SCORE_UNCERTAINTY: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of percentage of financial domain "uncertainty" language in the MD&A section between the last available report and the previous report of same period and category."""
    MD_DELTA_SCORE_LITIGIOUS: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of percentage of financial domain "litigious" language in the MD&A section between the last available report and the previous report of same period and category."""
    MD_DELTA_SCORE_CONSTRAINING: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of percentage of financial domain "constraining" language in the MD&A section between the last available report and the previous report of same period and category."""
    MD_DELTA_SCORE_INTERESTING: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of percentage of financial domain "interesting" language in the MD&A section between the last available report and the previous report of same period and category."""
    MD_DELTA_READABILITY: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of reading grade level in the MD&A section between the last available report and the previous report of same period and category."""
    MD_DELTA_LEXICAL_RICHNESS: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of lexical richness in the MD&A section between the last available report and the previous report of same period and category."""
    MD_DELTA_LEXICAL_DENSITY: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of lexical density in the MD&A section between the last available report and the previous report of same period and category."""
    MD_DELTA_SPECIFIC_DENSITY: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference of percentage of words belonging to the specific dictionary used for company filings analysis in the MD&A section between the last available report and the previous report of same period and category."""
    MD_SIMILARITY_ALL: 'BoundFloatColumn' = Column(float64_dtype)
    """The language similarity in the MD&A section between the last available report and the previous report of same period and category."""
    MD_SIMILARITY_POSITIVE: 'BoundFloatColumn' = Column(float64_dtype)
    """The similarity in terms of financial domain "positive" language in the MD&A section between the last available report and the previous report of same period and category."""
    MD_SIMILARITY_NEGATIVE: 'BoundFloatColumn' = Column(float64_dtype)
    """The similarity in terms of financial domain "negative" language in the MD&A section between the last available report and the previous report of same period and category."""

    @classmethod
    def slice(
        cls,
        report_category: Literal['10-K', '10-Q', None] = None,
        ) -> 'BLMCF':
        """
        Return a Brain Language Metrics on Company Filings (BLMCF) tied to a
        particular report category (10-K, 10-Q, or both).

        Parameters
        ----------
        report_category : str, required
            the report category, either '10-K', '10-Q', or None to include both.

        Returns
        -------
        DataSet
            Brain Language Metrics on Company Filings (BLMCF) DataSet with the
            specified report_category.

        Notes
        -----
        Usage Guide:

        * Brain Language Metrics on Company Filings: https://qrok.it/dl/z/pipeline-brain-blmcf
        * Pipeline data concepts: https://qrok.it/dl/z/pipeline-data-concepts

        Examples
        --------
        Select the top 100 stocks by sentiment score of the latest company filing::

            top_sentiment = brain.BLMCF.slice().SENTIMENT.latest.top(100)

        Select the top 100 stocks by sentiment score of the latest 10-K filing::

            top_sentiment = brain.BLMCF.slice(report_category='10-K').SENTIMENT.latest.top(100)
        """
        return super().slice(report_category=report_category)

class BLMECT(DataSet):
    """
    DataSet representing Brain Earnings Call Transcripts (BLMECT) data.

    This dataset provides sentiment scores and other language metrics for
    earnings call transcripts for US stocks, with history back to January 1,
    2012.

    Columns are organized into three sections, corresponding to three sections
    of the earnings call transcripts: "Management Discussion" (MD), "Analyst
    Questions" (AQ), and "Management Answers" (MA). Columns containing
    "DELTA" or "SIMILARITY" in the name compare the current earnings call
    transcript to the previous earnings call transcript.

    Attributes
    ----------
    LAST_TRANSCRIPT_DATE : datetime
        The date of last earnings call transcript (with respect to the record's
        Date) issued by the company in YYYY-MM-DD format

    LAST_TRANSCRIPT_QUARTER : float
        Reference quarter of last earnings call transcript

    LAST_TRANSCRIPT_YEAR : float
        Reference year of last earnings call transcript

    MD_N_CHARACTERS : float
        The length of the "Management Discussion" section measured in number of
        characters.

    MD_SENTIMENT : float
        The financial sentiment for the "Management Discussion" section of the
        last available transcript.

    MD_SCORE_UNCERTAINTY : float
        The percentage of financial domain "uncertainty" language in the
        "Management Discussion" section of the last available transcript.

    MD_SCORE_LITIGIOUS : float
        The percentage of financial domain "litigious" language in the
        "Management Discussion" section of the last available transcript.

    MD_SCORE_CONSTRAINING : float
        The percentage of financial domain "constraining" language in the
        "Management Discussion" section of the last available transcript.

    MD_READABILITY : float
        The reading grade level of the "Management Discussion" section of the
        last available transcript.

    MD_LEXICAL_RICHNESS : float
        The lexical richness of the "Management Discussion" section of the last
        available transcript.

    MD_LEXICAL_DENSITY : float
        The lexical density of the "Management Discussion" section of the last
        available transcript.

    MD_SPECIFIC_DENSITY : float
        Percentage of words belonging to the specific dictionary used for the
        earnings call analysis present in the "Management Discussion" section
        of the last available transcript.

    AQ_N_CHARACTERS : float
        The length of the "Analyst Questions" section measured in number of
        characters.

    AQ_SENTIMENT : float
        The financial sentiment for the "Analyst Questions" section of the last
        available transcript.

    AQ_SCORE_UNCERTAINTY : float
        The percentage of financial domain "uncertainty" language in the
        "Analyst Questions" section of the last available transcript.

    AQ_SCORE_LITIGIOUS : float
        The percentage of financial domain "litigious" language in the
        "Analyst Questions" section of the last available transcript.

    AQ_SCORE_CONSTRAINING : float
        The percentage of financial domain "constraining" language in the
        "Analyst Questions" section of the last available transcript.

    MA_N_CHARACTERS : float
        The length of the "Management Answers" section measured in number of
        characters.

    MA_SENTIMENT : float
        The financial sentiment for the "Management Answers" section of the
        last available transcript.

    MA_SCORE_UNCERTAINTY : float
        The percentage of financial domain "uncertainty" language in the
        "Management Answers" section of the last available transcript.

    MA_SCORE_LITIGIOUS : float
        The percentage of financial domain "litigious" language in the
        "Management Answers" section of the last available transcript.

    MA_SCORE_CONSTRAINING : float
        The percentage of financial domain "constraining" language in the
        "Management Answers" section of the last available transcript.

    MA_READABILITY : float
        The reading grade level of the "Management Answers" section of the last
        available transcript.

    MA_LEXICAL_RICHNESS : float
        The lexical richness of the "Management Answers" section of the last
        available transcript.

    MA_LEXICAL_DENSITY : float
        The lexical density of the "Management Answers" section of the last
        available transcript.

    MA_SPECIFIC_DENSITY : float
        Percentage of words belonging to the specific dictionary used for the
        earnings call analysis present in the "Management Answers" section of
        the last available transcript.

    PREV_TRANSCRIPT_DATE : datetime
        Date of the previous earnings call transcript

    PREV_TRANSCRIPT_QUARTER : float
        Reference quarter of the previous earnings call transcript

    PREV_TRANSCRIPT_YEAR : float
        Reference year of the previous earnings call transcript

    MD_DELTA_PERC_N_CHARACTERS : float
        The percentage change in the length (measured in number of characters)
        of the "Management Discussion" section between the last and previous
        available transcripts.

    MD_DELTA_SENTIMENT : float
        The difference in financial sentiment for the "Management Discussion"
        section between the last and previous available transcripts.

    MD_DELTA_SCORE_UNCERTAINTY : float
        The difference in the percentage of financial domain "uncertainty"
        language in the "Management Discussion" section between the last and
        previous available transcripts.

    MD_DELTA_SCORE_LITIGIOUS : float
        The difference in the percentage of financial domain "litigious"
        language in the "Management Discussion" section between the last and
        previous available transcripts.

    MD_DELTA_SCORE_CONSTRAINING : float
        The difference in the percentage of financial domain "constraining"
        language in the "Management Discussion" section between the last and
        previous available transcripts.

    MD_DELTA_READABILITY : float
        The difference in the reading grade level of the "Management Discussion"
        section between the last and previous available transcripts.

    MD_DELTA_LEXICAL_RICHNESS : float
        The difference in the lexical richness of the "Management Discussion"
        section between the last and previous available transcripts.

    MD_DELTA_LEXICAL_DENSITY : float
        The difference in the lexical density of the "Management Discussion"
        section between the last and previous available transcripts.

    MD_DELTA_SPECIFIC_DENSITY : float
        The difference in the percentage of words belonging to the specific
        dictionary used for the earnings call analysis present in the
        "Management Discussion" section between the last and previous available
        transcripts.

    MD_SIMILARITY_ALL : float
        The language similarity between the "Management Discussion" sections of
        the last and previous available transcripts.

    MD_SIMILARITY_POSITIVE : float
        The similarity in terms of financial domain "positive" language between
        the "Management Discussion" sections of the last and previous available
        transcripts.

    MD_SIMILARITY_NEGATIVE : float
        The similarity in terms of financial domain "negative" language between
        the "Management Discussion" sections of the last and previous available
        transcripts.

    MD_SIMILARITY_UNCERTAINTY : float
        The similarity in terms of financial domain "uncertainty" language
        between the "Management Discussion" sections of the last and previous
        available transcripts.

    MD_SIMILARITY_LITIGIOUS : float
        The similarity in terms of financial domain "litigious" language
        between the "Management Discussion" sections of the last and previous
        available transcripts.

    MD_SIMILARITY_CONSTRAINING : float
        The similarity in terms of financial domain "constraining" language
        between the "Management Discussion" sections of the last and previous
        available transcripts.

    AQ_DELTA_PERC_N_CHARACTERS : float
        The percentage change in the length (measured in number of characters)
        of the "Analyst Questions" section between the last and previous
        available transcripts.

    AQ_DELTA_SENTIMENT : float
        The difference in financial sentiment for the "Analyst Questions"
        section between the last and previous available transcripts.

    AQ_DELTA_SCORE_UNCERTAINTY : float
        The difference in the percentage of financial domain "uncertainty"
        language in the "Analyst Questions" section between the last and
        previous available transcripts.

    AQ_DELTA_SCORE_LITIGIOUS : float
        The difference in the percentage of financial domain "litigious"
        language in the "Analyst Questions" section between the last and
        previous available transcripts.

    AQ_DELTA_SCORE_CONSTRAINING : float
        The difference in the percentage of financial domain "constraining"
        language in the "Analyst Questions" section between the last and
        previous available transcripts.

    AQ_SIMILARITY_ALL : float
        The language similarity between the "Analyst Questions" sections of the
        last and previous available transcripts.

    AQ_SIMILARITY_POSITIVE : float
        The similarity in terms of financial domain "positive" language between
        the "Analyst Questions" sections of the last and previous available
        transcripts.

    AQ_SIMILARITY_NEGATIVE : float
        The similarity in terms of financial domain "negative" language between
        the "Analyst Questions" sections of the last and previous available
        transcripts.

    MA_DELTA_PERC_N_CHARACTERS : float
        The percentage change in the length (measured in number of characters)
        of the "Management Answers" section between the last and previous
        available transcripts.

    MA_DELTA_SENTIMENT : float
        The difference in financial sentiment for the "Management Answers"
        section between the last and previous available transcripts.

    MA_DELTA_SCORE_UNCERTAINTY : float
        The difference in the percentage of financial domain "uncertainty"
        language in the "Management Answers" section between the last and
        previous available transcripts.

    MA_DELTA_SCORE_LITIGIOUS : float
        The difference in the percentage of financial domain "litigious"
        language in the "Management Answers" section between the last and
        previous available transcripts.

    MA_DELTA_SCORE_CONSTRAINING : float
        The difference in the percentage of financial domain "constraining"
        language in the "Management Answers" section between the last and
        previous available transcripts.

    MA_DELTA_READABILITY : float
        The difference in the reading grade level of the "Management Answers"
        section between the last and previous available transcripts.

    MA_DELTA_LEXICAL_RICHNESS : float
        The difference in the lexical richness of the "Management Answers"
        section between the last and previous available transcripts.

    MA_DELTA_LEXICAL_DENSITY : float
        The difference in the lexical density of the "Management Answers"
        section between the last and previous available transcripts.

    MA_DELTA_SPECIFIC_DENSITY : float
        The difference in the percentage of words belonging to the specific
        dictionary used for the earnings call analysis present in the
        "Management Answers" section between the last and previous available
        transcripts.

    MA_SIMILARITY_ALL : float
        The language similarity between the "Management Answers" sections of
        the last and previous available transcripts.

    MA_SIMILARITY_POSITIVE : float
        The similarity in terms of financial domain "positive" language between
        the "Management Answers" sections of the last and previous available
        transcripts.

    MA_SIMILARITY_NEGATIVE : float
        The similarity in terms of financial domain "negative" language between
        the "Management Answers" sections of the last and previous available
        transcripts.

    MA_SIMILARITY_UNCERTAINTY : float
        The similarity in terms of financial domain "uncertainty" language
        between the "Management Answers" sections of the last and previous
        available transcripts.

    MA_SIMILARITY_LITIGIOUS : float
        The similarity in terms of financial domain "litigious" language
        between the "Management Answers" sections of the last and previous
        available transcripts.

    MA_SIMILARITY_CONSTRAINING : float
        The similarity in terms of financial domain "constraining" language
        between the "Management Answers" sections of the last and previous
        available transcripts.

    Notes
    -----
    Usage Guide:

    * Brain Language Metrics on Earnings Call Transcripts: https://qrok.it/dl/z/pipeline-brain-blmect
    * Pipeline data concepts: https://qrok.it/dl/z/pipeline-data-concepts

    Examples
    --------
    Select the top 100 stocks by sentiment score in the Management Discussion section of
    the latest earnings call transcript::

        top_sentiment = brain.BLMECT.MD_SENTIMENT.latest.top(100)
    """
    domain: Domain = US_EQUITIES

    LAST_TRANSCRIPT_DATE: 'BoundDatetimeColumn' = Column(datetime64ns_dtype)
    """The date of last earnings call transcript (with respect to the record's Date) issued by the company in YYYY-MM-DD format"""
    LAST_TRANSCRIPT_QUARTER: 'BoundFloatColumn' = Column(float64_dtype)
    """Reference quarter of last earnings call transcript"""
    LAST_TRANSCRIPT_YEAR: 'BoundFloatColumn' = Column(float64_dtype)
    """Reference year of last earnings call transcript"""
    MD_N_CHARACTERS: 'BoundFloatColumn' = Column(float64_dtype)
    """The length of the "Management Discussion" section measured in number of characters."""
    MD_SENTIMENT: 'BoundFloatColumn' = Column(float64_dtype)
    """The financial sentiment for the "Management Discussion" section of the last available transcript."""
    MD_SCORE_UNCERTAINTY: 'BoundFloatColumn' = Column(float64_dtype)
    """The percentage of financial domain "uncertainty" language in the "Management Discussion" section of the last available transcript."""
    MD_SCORE_LITIGIOUS: 'BoundFloatColumn' = Column(float64_dtype)
    """The percentage of financial domain "litigious" language in the "Management Discussion" section of the last available transcript."""
    MD_SCORE_CONSTRAINING: 'BoundFloatColumn' = Column(float64_dtype)
    """The percentage of financial domain "constraining" language in the "Management Discussion" section of the last available transcript."""
    MD_READABILITY: 'BoundFloatColumn' = Column(float64_dtype)
    """The reading grade level of the "Management Discussion" section of the last available transcript."""
    MD_LEXICAL_RICHNESS: 'BoundFloatColumn' = Column(float64_dtype)
    """The lexical richness of the "Management Discussion" section of the last available transcript."""
    MD_LEXICAL_DENSITY: 'BoundFloatColumn' = Column(float64_dtype)
    """The lexical density of the "Management Discussion" section of the last available transcript."""
    MD_SPECIFIC_DENSITY: 'BoundFloatColumn' = Column(float64_dtype)
    """Percentage of words belonging to the specific dictionary used for the earnings call analysis present in the "Management Discussion" section of the last available transcript."""
    AQ_N_CHARACTERS: 'BoundFloatColumn' = Column(float64_dtype)
    """The length of the "Analyst Questions" section measured in number of characters."""
    AQ_SENTIMENT: 'BoundFloatColumn' = Column(float64_dtype)
    """The financial sentiment for the "Analyst Questions" section of the last available transcript."""
    AQ_SCORE_UNCERTAINTY: 'BoundFloatColumn' = Column(float64_dtype)
    """The percentage of financial domain "uncertainty" language in the "Analyst Questions" section of the last available transcript."""
    AQ_SCORE_LITIGIOUS: 'BoundFloatColumn' = Column(float64_dtype)
    """The percentage of financial domain "litigious" language in the "Analyst Questions" section of the last available transcript."""
    AQ_SCORE_CONSTRAINING: 'BoundFloatColumn' = Column(float64_dtype)
    """The percentage of financial domain "constraining" language in the "Analyst Questions" section of the last available transcript."""
    MA_N_CHARACTERS: 'BoundFloatColumn' = Column(float64_dtype)
    """The length of the "Management Answers" section measured in number of characters."""
    MA_SENTIMENT: 'BoundFloatColumn' = Column(float64_dtype)
    """The financial sentiment for the "Management Answers" section of the last available transcript."""
    MA_SCORE_UNCERTAINTY: 'BoundFloatColumn' = Column(float64_dtype)
    """The percentage of financial domain "uncertainty" language in the "Management Answers" section of the last available transcript."""
    MA_SCORE_LITIGIOUS: 'BoundFloatColumn' = Column(float64_dtype)
    """The percentage of financial domain "litigious" language in the "Management Answers" section of the last available transcript."""
    MA_SCORE_CONSTRAINING: 'BoundFloatColumn' = Column(float64_dtype)
    """The percentage of financial domain "constraining" language in the "Management Answers" section of the last available transcript."""
    MA_READABILITY: 'BoundFloatColumn' = Column(float64_dtype)
    """The reading grade level of the "Management Answers" section of the last available transcript."""
    MA_LEXICAL_RICHNESS: 'BoundFloatColumn' = Column(float64_dtype)
    """The lexical richness of the "Management Answers" section of the last available transcript."""
    MA_LEXICAL_DENSITY: 'BoundFloatColumn' = Column(float64_dtype)
    """The lexical density of the "Management Answers" section of the last available transcript."""
    MA_SPECIFIC_DENSITY: 'BoundFloatColumn' = Column(float64_dtype)
    """Percentage of words belonging to the specific dictionary used for the earnings call analysis present in the "Management Answers" section of the last available transcript."""
    PREV_TRANSCRIPT_DATE: 'BoundDatetimeColumn' = Column(datetime64ns_dtype)
    """Date of the previous earnings call transcript"""
    PREV_TRANSCRIPT_QUARTER: 'BoundFloatColumn' = Column(float64_dtype)
    """Reference quarter of the previous earnings call transcript"""
    PREV_TRANSCRIPT_YEAR: 'BoundFloatColumn' = Column(float64_dtype)
    """Reference year of the previous earnings call transcript"""
    MD_DELTA_PERC_N_CHARACTERS: 'BoundFloatColumn' = Column(float64_dtype)
    """The percentage change in the length (measured in number of characters) of the "Management Discussion" section between the last and previous available transcripts."""
    MD_DELTA_SENTIMENT: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference in financial sentiment for the "Management Discussion" section between the last and previous available transcripts."""
    MD_DELTA_SCORE_UNCERTAINTY: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference in the percentage of financial domain "uncertainty" language in the "Management Discussion" section between the last and previous available transcripts."""
    MD_DELTA_SCORE_LITIGIOUS: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference in the percentage of financial domain "litigious" language in the "Management Discussion" section between the last and previous available transcripts."""
    MD_DELTA_SCORE_CONSTRAINING: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference in the percentage of financial domain "constraining" language in the "Management Discussion" section between the last and previous available transcripts."""
    MD_DELTA_READABILITY: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference in the reading grade level of the "Management Discussion" section between the last and previous available transcripts."""
    MD_DELTA_LEXICAL_RICHNESS: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference in the lexical richness of the "Management Discussion" section between the last and previous available transcripts."""
    MD_DELTA_LEXICAL_DENSITY: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference in the lexical density of the "Management Discussion" section between the last and previous available transcripts."""
    MD_DELTA_SPECIFIC_DENSITY: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference in the percentage of words belonging to the specific dictionary used for the earnings call analysis present in the "Management Discussion" section between the last and previous available transcripts."""
    MD_SIMILARITY_ALL: 'BoundFloatColumn' = Column(float64_dtype)
    """The language similarity between the "Management Discussion" sections of the last and previous available transcripts."""
    MD_SIMILARITY_POSITIVE: 'BoundFloatColumn' = Column(float64_dtype)
    """The similarity in terms of financial domain "positive" language between the "Management Discussion" sections of the last and previous available transcripts."""
    MD_SIMILARITY_NEGATIVE: 'BoundFloatColumn' = Column(float64_dtype)
    """The similarity in terms of financial domain "negative" language between the "Management Discussion" sections of the last and previous available transcripts."""
    MD_SIMILARITY_UNCERTAINTY: 'BoundFloatColumn' = Column(float64_dtype)
    """The similarity in terms of financial domain "uncertainty" language between the "Management Discussion" sections of the last and previous available transcripts."""
    MD_SIMILARITY_LITIGIOUS: 'BoundFloatColumn' = Column(float64_dtype)
    """The similarity in terms of financial domain "litigious" language between the "Management Discussion" sections of the last and previous available transcripts."""
    MD_SIMILARITY_CONSTRAINING: 'BoundFloatColumn' = Column(float64_dtype)
    """The similarity in terms of financial domain "constraining" language between the "Management Discussion" sections of the last and previous available transcripts."""
    AQ_DELTA_PERC_N_CHARACTERS: 'BoundFloatColumn' = Column(float64_dtype)
    """The percentage change in the length (measured in number of characters) of the "Analyst Questions" section between the last and previous available transcripts."""
    AQ_DELTA_SENTIMENT: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference in financial sentiment for the "Analyst Questions" section between the last and previous available transcripts."""
    AQ_DELTA_SCORE_UNCERTAINTY: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference in the percentage of financial domain "uncertainty" language in the "Analyst Questions" section between the last and previous available transcripts."""
    AQ_DELTA_SCORE_LITIGIOUS: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference in the percentage of financial domain "litigious" language in the "Analyst Questions" section between the last and previous available transcripts."""
    AQ_DELTA_SCORE_CONSTRAINING: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference in the percentage of financial domain "constraining" language in the "Analyst Questions" section between the last and previous available transcripts."""
    AQ_SIMILARITY_ALL: 'BoundFloatColumn' = Column(float64_dtype)
    """The language similarity between the "Analyst Questions" sections of the last and previous available transcripts."""
    AQ_SIMILARITY_POSITIVE: 'BoundFloatColumn' = Column(float64_dtype)
    """The similarity in terms of financial domain "positive" language between the "Analyst Questions" sections of the last and previous available transcripts."""
    AQ_SIMILARITY_NEGATIVE: 'BoundFloatColumn' = Column(float64_dtype)
    """The similarity in terms of financial domain "negative" language between the "Analyst Questions" sections of the last and previous available transcripts."""
    MA_DELTA_PERC_N_CHARACTERS: 'BoundFloatColumn' = Column(float64_dtype)
    """The percentage change in the length (measured in number of characters) of the "Management Answers" section between the last and previous available transcripts."""
    MA_DELTA_SENTIMENT: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference in financial sentiment for the "Management Answers" section between the last and previous available transcripts."""
    MA_DELTA_SCORE_UNCERTAINTY: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference in the percentage of financial domain "uncertainty" language in the "Management Answers" section between the last and previous available transcripts."""
    MA_DELTA_SCORE_LITIGIOUS: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference in the percentage of financial domain "litigious" language in the "Management Answers" section between the last and previous available transcripts."""
    MA_DELTA_SCORE_CONSTRAINING: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference in the percentage of financial domain "constraining" language in the "Management Answers" section between the last and previous available transcripts."""
    MA_DELTA_READABILITY: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference in the reading grade level of the "Management Answers" section between the last and previous available transcripts."""
    MA_DELTA_LEXICAL_RICHNESS: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference in the lexical richness of the "Management Answers" section between the last and previous available transcripts."""
    MA_DELTA_LEXICAL_DENSITY: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference in the lexical density of the "Management Answers" section between the last and previous available transcripts."""
    MA_DELTA_SPECIFIC_DENSITY: 'BoundFloatColumn' = Column(float64_dtype)
    """The difference in the percentage of words belonging to the specific dictionary used for the earnings call analysis present in the "Management Answers" section between the last and previous available transcripts."""
    MA_SIMILARITY_ALL: 'BoundFloatColumn' = Column(float64_dtype)
    """The language similarity between the "Management Answers" sections of the last and previous available transcripts."""
    MA_SIMILARITY_POSITIVE: 'BoundFloatColumn' = Column(float64_dtype)
    """The similarity in terms of financial domain "positive" language between the "Management Answers" sections of the last and previous available transcripts."""
    MA_SIMILARITY_NEGATIVE: 'BoundFloatColumn' = Column(float64_dtype)
    """The similarity in terms of financial domain "negative" language between the "Management Answers" sections of the last and previous available transcripts."""
    MA_SIMILARITY_UNCERTAINTY: 'BoundFloatColumn' = Column(float64_dtype)
    """The similarity in terms of financial domain "uncertainty" language between the "Management Answers" sections of the last and previous available transcripts."""
    MA_SIMILARITY_LITIGIOUS: 'BoundFloatColumn' = Column(float64_dtype)
    """The similarity in terms of financial domain "litigious" language between the "Management Answers" sections of the last and previous available transcripts."""
    MA_SIMILARITY_CONSTRAINING: 'BoundFloatColumn' = Column(float64_dtype)
    """The similarity in terms of financial domain "constraining" language between the "Management Answers" sections of the last and previous available transcripts."""
