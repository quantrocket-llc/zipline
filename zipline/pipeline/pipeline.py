import six
from typing import Literal

import pandas as pd
from pydantic import validate_call

from zipline.errors import UnsupportedPipelineOutput

from .domain import Domain, GENERIC, infer_domain
from .graph import ExecutionPlan, TermGraph, SCREEN_NAME
from .filters import (
    Filter,
    SingleAsset,
    StaticAssets,
    StaticSids,
    StaticUniverse,
    ArrayPredicate,
    NumExprFilter,
    Latest as LatestFilter,
    NullFilter,
    NotNullFilter
)
from .classifiers import Latest as LatestClassifier
from .factors import Latest as LatestFactor
from .term import AssetExists, ComputableTerm, Term

def _term_to_prescreen_fielddef(term):
    """
    Tries to convert a term to a prescreen field definition,
    that is, the "fields" key of the prescreen dict.

    Parameters
    ----------
    term : zipline.pipeline.Term

    Returns
    -------
    fielddef : dict or None
    """
    # check if the term is an ArrayPredicate of a SecuritiesMaster column,
    # e.g. SecuritiesMaster.SecType.latest.eq('STK')
    if (isinstance(term, ArrayPredicate)
        and len(term.inputs) == 1
        and isinstance(term.inputs[0], LatestClassifier)
        and len(term.inputs[0].inputs) == 1
        and hasattr(term.inputs[0].inputs[0], "dataset")
        and term.inputs[0].inputs[0].dataset.qualname == "SecuritiesMaster"
        and term.params['op'].__name__ in (
            "eq",
            "isin",
            "ne",
            "has_substring",
            "startswith",
            "endswith",
            "matches",
            )):
        field = term.inputs[0].inputs[0].name
        if term.params['op'].__name__ == "eq":
            op = "eq"
            negate = False
            values = [term.params['opargs'][0]]
        elif term.params['op'].__name__ == "isin":
            op = "eq"
            negate = False
            values = list(term.params['opargs'][0])
        elif term.params['op'].__name__ == "ne":
            op = "eq"
            negate = True
            values = [term.params['opargs'][0]]
        elif term.params['op'].__name__ == "has_substring":
            op = "contains"
            negate = False
            values = term.params['opargs'][0]
        elif term.params['op'].__name__ == "startswith":
            op = "startswith"
            negate = False
            values = term.params['opargs'][0]
        elif term.params['op'].__name__ == "endswith":
            op = "endswith"
            negate = False
            values = term.params['opargs'][0]
        elif term.params['op'].__name__ == "matches":
            op = "match"
            negate = False
            values = term.params['opargs'][0]

        return {"field": field, "op": op, "negate": negate, "values": values}

    # check if the term is a boolean SecuritiesMaster column, e.g.
    # SecuritiesMaster.Etf.latest
    if (isinstance(term, LatestFilter)
        and hasattr(term.inputs[0], "dataset")
        and term.inputs[0].dataset.qualname == "SecuritiesMaster"
        ):
        field = term.inputs[0].name
        op = "eq"
        negate = False
        values = [True]
        return {"field": field, "op": op, "negate": negate, "values": values}

    # check if the term is a NullFilter or NotNullFilter of a SecuritiesMaster
    # column, e.g. SecuritiesMaster.alpaca_AssetId.latest.isnull()
    if (isinstance(term, (NullFilter, NotNullFilter))
        and isinstance(term.inputs[0], (LatestClassifier, LatestFactor))
        and hasattr(term.inputs[0].inputs[0], "dataset")
        and term.inputs[0].inputs[0].dataset.qualname == "SecuritiesMaster"):
        field = term.inputs[0].inputs[0].name
        op = "isnull"
        negate = True if isinstance(term, NotNullFilter) else False
        values = [True]
        return {"field": field, "op": op, "negate": negate, "values": values}

    # isnull() on float columns are handled with a NumExprFilter
    if (isinstance(term, NumExprFilter)
        and term._expr == 'x_0 != x_0'
        and isinstance(term.bindings["x_0"], LatestFactor)
        and len(term.bindings["x_0"].inputs) == 1
        and hasattr(term.bindings["x_0"].inputs[0], "dataset")
        and term.bindings["x_0"].inputs[0].dataset.qualname == "SecuritiesMaster"):
        field = term.bindings["x_0"].inputs[0].name
        op = "isnull"
        negate = False
        values = [True]
        return {"field": field, "op": op, "negate": negate, "values": values}

    return None

def _term_to_prescreen_dict(term, prescreen=None, negate=False):
    """
    Tries to convert a term to a prescreen dict.

    Parameters
    ----------
    term : zipline.pipeline.Term

    prescreen : dict or None
        Existing prescreen dict to update

    negate : bool
        Whether to negate the term. Applies only to fields, not sids.

    Returns
    -------
    prescreen : dict or None

    Notes
    -----
    If a prescreen dict is passed by the new term cannot be converted to a
    prescreen, None is returned.
    """
    prescreen = prescreen or {}

    if isinstance(term, SingleAsset):
        if "sids" not in prescreen:
            prescreen["sids"] = []
        prescreen["sids"].append(term._asset.sid)
        return prescreen

    if isinstance(term, StaticAssets):
        if "sids" not in prescreen:
            prescreen["sids"] = []
        prescreen["sids"].extend(term.params["sids"])
        return prescreen

    # StaticSids and StaticUniverse store real sids in the sids param
    if isinstance(term, (StaticSids, StaticUniverse)):
        if "real_sids" not in prescreen:
            prescreen["real_sids"] = []
        prescreen["real_sids"].extend(term.params["sids"])
        return prescreen

    # check if the term is a negation of a SecuritiesMaster column, e.g.
    # ~SecuritiesMaster.SecType.latest.eq('STK')
    if (
        isinstance(term, NumExprFilter)
        and term._expr == '~x_0'
        ):
        fielddef = _term_to_prescreen_fielddef(term.bindings["x_0"])
        if fielddef is not None:
            # reverse the negate flag since the term has the unary operator
            fielddef["negate"] = True if fielddef["negate"] == False else False
            # negate it back if requested
            if negate:
                fielddef["negate"] = True if fielddef["negate"] == False else False
            if "fields" not in prescreen:
                prescreen["fields"] = []
            prescreen["fields"].append(fielddef)
            return prescreen

    # check if the term is an ArrayPredicate of a SecuritiesMaster column, e.g.
    # SecuritiesMaster.SecType.latest.eq('STK')
    fielddef = _term_to_prescreen_fielddef(term)
    if fielddef is not None:
        # negate if requested
        if negate:
            fielddef["negate"] = True if fielddef["negate"] == False else False
        if "fields" not in prescreen:
            prescreen["fields"] = []
        prescreen["fields"].append(fielddef)
        return prescreen

    return None

class Pipeline(object):
    """
    A Pipeline object represents a collection of named expressions to be
    compiled and executed.

    A Pipeline has three important attributes: 'columns', a dictionary of named
    :class:`~zipline.pipeline.Term` instances, 'screen', a
    :class:`~zipline.pipeline.Filter` representing criteria for
    including an asset in the results of a Pipeline. and 'initial_universe', a
    :class:`~zipline.pipeline.Filter` defining which assets to include in the
    initial universe on which the Pipeline is computed. For the distinction between
    'screen' and 'initial_universe', see the Notes section below.

    To compute a pipeline in the context of a TradingAlgorithm, users must call
    ``attach_pipeline`` in their ``initialize`` function to register that the
    pipeline should be computed each trading day. The most recent outputs of an
    attached pipeline can be retrieved by calling ``pipeline_output`` from
    ``handle_data``, ``before_trading_start``, or a scheduled function.

    Parameters
    ----------
    columns : dict, optional
        Initial columns.
    screen : zipline.pipeline.Filter, optional
        A Filter defining which assets to include in the Pipeline results.
    initial_universe : zipline.pipeline.Filter, optional
        A Filter defining which assets to include in the initial universe
        on which the Pipeline is computed. If provided, the Filter must consist
        exclusively of one or more of the following terms: StaticSids, StaticAssets,
        StaticUniverse, or terms based on columns from the SecuritiesMaster dataset.
        If the Filter includes multiple terms, they must be ANDed together; ORed terms
        are not supported. If omitted, the initial universe is all assets in the bundle.
        Specifying an initial_universe can speed up pipeline computation by limiting
        the set of assets on which computations must be performed. For the distinction
        between 'screen' and 'initial_universe', see the Notes section below.

    Notes
    -----
    The 'screen' and 'initial_universe' attributes are both used to filter the
    assets in a pipeline, but they differ in which kinds of terms they support
    and when they are applied. 'initial_universe' is applied before the pipeline
    runs. This limits the size of the computational universe and speeds up pipeline
    computation. However, because 'initial_universe' is applied before the pipeline
    runs, it cannot include terms that will only be known after the pipeline runs,
    such as an asset's daily price or its dollar volume rank compared to its peers.
    'initial_universe' can only use terms representing static assets or static
    characteristics of assets, specifically StaticSids, StaticAssets, StaticUniverse,
    or terms based on columns from the SecuritiesMaster dataset.

    In contrast, 'screen' is applied after the pipeline runs and filters the results
    that get returned. This means 'screen' can include any term or combination of terms,
    as these terms will have been computed by the time the screen is applied. However,
    because 'screen' is applied after the pipeline runs, it does not limit the size
    of the computational universe and thus does not speed up pipeline computation.

    You can use 'initial_universe' and 'screen' together, limiting the size of
    the computational universe with 'initial_universe' and further filtering the
    results with 'screen'.

    Usage Guide:

    * Pipeline API: https://qrok.it/dl/z/pipeline
    """
    __slots__ = ('_columns', '_prescreen', '_initial_universe', '_screen', '_domain', '__weakref__')

    @validate_call(config=dict(arbitrary_types_allowed=True))
    def __init__(
        self,
        columns: dict[str, Term] | None = None,
        screen: Filter | None = None,
        initial_universe: Filter | None = None,
        domain: Domain = GENERIC
        ):
        if columns is None:
            columns = {}

        validate_column = self.validate_column
        for column_name, term in columns.items():
            validate_column(column_name, term)
            if not isinstance(term, ComputableTerm):
                raise TypeError(
                    "Column {column_name!r} contains an invalid pipeline term "
                    "({term}). Did you mean to append '.latest'?".format(
                        column_name=column_name, term=term,
                    )
                )

        self._columns = columns
        self._initial_universe = initial_universe
        self._prescreen = None
        if initial_universe:
            _prescreen = self._convert_to_prescreen(initial_universe)
            if _prescreen:
                self._prescreen = _prescreen
        self._screen = screen
        self._domain = domain

    def _convert_to_prescreen(self, initial_universe):
        """
        Tries to convert the initial_universe Filter into prescreen parameters.

        The returned prescreen is a dict of asset-level parameters that can be used to
        pre-filter the universe and thus limit the initial workspace size. If
        populated, prescreen is a dict with the following possible keys:
          - sids: list of zipline sids to include
          - real_sids: list of real sids to include
          - fields: list of dicts with the following keys:
              - field: name of securities master field to filter on
              - op: 'eq', 'contains'
              - negate: whether to negate the filter
              - values: list of values to include or exclude
        """
        ERROR_MSG = (
            "The term {term} is invalid for initial_universe. "
            "The initial_universe Filter must consist exclusively of one or more "
            " of the following terms: StaticSids, StaticAssets, StaticUniverse, or "
            "terms based on columns from the SecuritiesMaster dataset. If the Filter "
            "includes multiple terms, they must be ANDed together; ORed terms are not "
            "supported."
        )
        # see if the initial_universe contains a single prescreenable term
        prescreen = _term_to_prescreen_dict(initial_universe)
        if prescreen is not None:
            return prescreen

        # if the screen is a NumExprFilter, see if it is an ANDed conjunction of
        # prescreenable terms (ORed expressions are not supported)
        elif isinstance(initial_universe, NumExprFilter):

            # ignore parantheses, which don't matter for ANDed expressions
            expr = initial_universe._expr.replace("(", "").replace(")", "")
            # split on AND and see if the resulting terms (possibly ignoring ~)
            # match the screen bindings
            terms = expr.split(" & ")
            if set([term.replace("~", "") for term in terms]) == set(initial_universe.bindings):
                prescreen = {}
                for term in terms:
                    negate = "~" in term
                    term = term.replace("~", "")
                    prescreen = _term_to_prescreen_dict(
                        initial_universe.bindings[term],
                        prescreen=prescreen,
                        negate=negate)
                    # if any term cannot be converted to a prescreen, bail out
                    if not prescreen:
                        raise ValueError(ERROR_MSG.format(term=str(initial_universe.bindings[term])))

                else:
                    # didn't break loop, so prescreen is valid
                    return prescreen


        raise ValueError(ERROR_MSG.format(term=str(initial_universe)))

    @property
    def columns(self) -> dict[str, Term]:
        """The output columns of this pipeline.

        Returns
        -------
        columns : dict[str, zipline.pipeline.ComputableTerm]
            Map from column name to expression computing that column's output.
        """
        return self._columns

    @property
    def screen(self) -> Filter:
        """
        The screen of this pipeline.

        Returns
        -------
        screen : zipline.pipeline.Filter or None
            Term defining the screen for this pipeline. If ``screen`` is a
            filter, rows that do not pass the filter (i.e., rows for which the
            filter computed ``False``) will be dropped from the output of this
            pipeline before returning results.

        Notes
        -----
        Setting a screen on a Pipeline does not change the values produced for
        any rows: it only affects whether a given row is returned. Computing a
        pipeline with a screen is logically equivalent to computing the
        pipeline without the screen and then, as a post-processing-step,
        filtering out any rows for which the screen computed ``False``.
        """
        return self._screen

    @property
    def initial_universe(self) -> Filter:
        """
        The initial universe of this pipeline.

        Returns
        -------
        initial_universe : zipline.pipeline.Filter or None
            Term defining which assets to include in the initial universe for
            this pipeline.
        """
        return self._initial_universe

    @validate_call(config=dict(arbitrary_types_allowed=True))
    def add(
        self,
        term: Term,
        name: str,
        overwrite: bool = False
        ) -> None:
        """Add a column.

        The results of computing ``term`` will show up as a column in the
        DataFrame produced by running this pipeline.

        Parameters
        ----------
        column : zipline.pipeline.Term
            A Filter, Factor, or Classifier to add to the pipeline.
        name : str
            Name of the column to add.
        overwrite : bool
            Whether to overwrite the existing entry if we already have a column
            named `name`.
        """
        self.validate_column(name, term)

        columns = self.columns
        if name in columns:
            if overwrite:
                self.remove(name)
            else:
                raise KeyError("Column '{}' already exists.".format(name))

        if not isinstance(term, ComputableTerm):
            raise TypeError(
                "{term} is not a valid pipeline column. Did you mean to "
                "append '.latest'?".format(term=term)
            )

        self._columns[name] = term

    @validate_call
    def remove(self, name: str) -> Term:
        """Remove a column.

        Parameters
        ----------
        name : str
            The name of the column to remove.

        Raises
        ------
        KeyError
            If `name` is not in self.columns.

        Returns
        -------
        removed : zipline.pipeline.Term
            The removed term.
        """
        return self.columns.pop(name)

    @validate_call(config=dict(arbitrary_types_allowed=True))
    def set_screen(
        self,
        screen: Filter,
        overwrite: bool = False
        ) -> None:
        """Set a screen on this Pipeline.

        Parameters
        ----------
        filter : zipline.pipeline.Filter
            The filter to apply as a screen.
        overwrite : bool
            Whether to overwrite any existing screen.  If overwrite is False
            and self.screen is not None, we raise an error.
        """
        if self._screen is not None and not overwrite:
            raise ValueError(
                "set_screen() called with overwrite=False and screen already "
                "set.\n"
                "If you want to apply multiple filters as a screen use "
                "set_screen(filter1 & filter2 & ...).\n"
                "If you want to replace the previous screen with a new one, "
                "use set_screen(new_filter, overwrite=True)."
            )
        self._screen = screen

    def to_execution_plan(
        self,
        domain: Domain,
        default_screen: Filter,
        start_date: pd.Timestamp,
        end_date: pd.Timestamp
        ) -> ExecutionPlan:
        """
        Compile into an ExecutionPlan.

        Parameters
        ----------
        domain : zipline.pipeline.domain.Domain
            Domain on which the pipeline will be executed.
        default_screen : zipline.pipeline.Term
            Term to use as a screen if self.screen is None.
        all_dates : pd.DatetimeIndex
            A calendar of dates to use to calculate starts and ends for each
            term.
        start_date : pd.Timestamp
            The first date of requested output.
        end_date : pd.Timestamp
            The last date of requested output.

        Returns
        -------
        graph : zipline.pipeline.graph.ExecutionPlan
            Graph encoding term dependencies, including metadata about extra
            row requirements.
        """
        if self._domain is not GENERIC and self._domain is not domain:
            raise AssertionError(
                "Attempted to compile Pipeline with domain {} to execution "
                "plan with different domain {}.".format(self._domain, domain)
            )

        return ExecutionPlan(
            domain=domain,
            terms=self._prepare_graph_terms(default_screen),
            start_date=start_date,
            end_date=end_date,
        )

    def to_simple_graph(self, default_screen: Filter) -> TermGraph:
        """
        Compile into a simple TermGraph with no extra row metadata.

        Parameters
        ----------
        default_screen : zipline.pipeline.Term
            Term to use as a screen if self.screen is None.

        Returns
        -------
        graph : zipline.pipeline.graph.TermGraph
            Graph encoding term dependencies.
        """
        return TermGraph(self._prepare_graph_terms(default_screen))

    def _prepare_graph_terms(self, default_screen):
        """Helper for to_graph and to_execution_plan."""
        columns = self.columns.copy()
        screen = self.screen
        if screen is None:
            screen = default_screen
        columns[SCREEN_NAME] = screen
        return columns

    @validate_call
    def show_graph(self, format: Literal['svg', 'png', 'jpeg'] = 'svg'):
        """
        Render this Pipeline as a DAG.

        Parameters
        ----------
        format : {'svg', 'png', 'jpeg'}
            Image format to render with.  Default is 'svg'.
        """
        g = self.to_simple_graph(AssetExists())
        if format == 'svg':
            return g.svg
        elif format == 'png':
            return g.png
        elif format == 'jpeg':
            return g.jpeg
        else:
            # We should never get here because of the validate_call decorator
            # above.
            raise AssertionError("Unknown graph format %r." % format)

    @staticmethod
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def validate_column(column_name: str, term: Term) -> None:
        if term.ndim == 1:
            raise UnsupportedPipelineOutput(column_name=column_name, term=term)

    @property
    def _output_terms(self):
        """
        A list of terms that are outputs of this pipeline.

        Includes all terms registered as data outputs of the pipeline, plus the
        screen, if present.
        """
        terms = list(six.itervalues(self._columns))
        screen = self.screen
        if screen is not None:
            terms.append(screen)
        return terms

    @validate_call(config=dict(arbitrary_types_allowed=True))
    def domain(self, default: Domain) -> Domain:
        """
        Get the domain for this pipeline.

        - If an explicit domain was provided at construction time, use it.
        - Otherwise, infer a domain from the registered columns.
        - If no domain can be inferred, return ``default``.

        Parameters
        ----------
        default : zipline.pipeline.domain.Domain
            Domain to use if no domain can be inferred from this pipeline by
            itself.

        Returns
        -------
        domain : zipline.pipeline.domain.Domain
            The domain for the pipeline.

        Raises
        ------
        AmbiguousDomain
        ValueError
            If the terms in ``self`` conflict with self._domain.
        """
        # Always compute our inferred domain to ensure that it's compatible
        # with our explicit domain.
        inferred = infer_domain(self._output_terms)

        if inferred is GENERIC and self._domain is GENERIC:
            # Both generic. Fall back to default.
            return default
        elif inferred is GENERIC and self._domain is not GENERIC:
            # Use the non-generic domain.
            return self._domain
        elif inferred is not GENERIC and self._domain is GENERIC:
            # Use the non-generic domain.
            return inferred
        else:
            # Both non-generic. They have to match.
            if inferred is not self._domain:
                raise ValueError(
                    "Conflicting domains in Pipeline. Inferred {}, but {} was "
                    "passed at construction.".format(inferred, self._domain)
                )
            return inferred
