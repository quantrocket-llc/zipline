
ADJUSTMENT_STYLES = ...

class ContinuousFuture:
    """
    Represents a specifier for a chain of future contracts, where the
    coordinates for the chain are:
    root_symbol : str
        The root symbol of the contracts.
    offset : int
        The distance from the primary chain.
        e.g. 0 specifies the primary chain, 1 the secondary, etc.
    roll_style : str
        How rolls from contract to contract should be calculated.
        Currently supports 'calendar'.

    Instances of this class are exposed to the algorithm.
    """
    ...
    def from_dict(cls, dict_):
        """
        Build an ContinuousFuture instance from a dict.
        """
        ...

    def is_alive_for_session(self, session_label):
        """
        Returns whether the continuous future is alive at the given dt.

        Parameters
        ----------
        session_label: pd.Timestamp
            The desired session label to check. (midnight UTC)

        Returns
        -------
        boolean: whether the continuous is alive at the given dt.
        """
        ...

    def is_exchange_open(self, dt_minute):
        """
        Parameters
        ----------
        dt_minute: pd.Timestamp (UTC, tz-aware)
            The minute to check.

        Returns
        -------
        boolean: whether the continuous futures's exchange is open at the
        given minute.
        """
        ...

class ContractNode(object):
    ...

class OrderedContracts(object):
    """
    A container for aligned values of a future contract chain, in sorted order
    of their occurrence.
    Used to get answers about contracts in relation to their auto close
    dates and start dates.

    Members
    -------
    root_symbol : str
        The root symbol of the future contract chain.
    contracts : deque
        The contracts in the chain in order of occurrence.
    start_dates : long[:]
        The start dates of the contracts in the chain.
        Corresponds by index with contract_sids.
    auto_close_dates : long[:]
        The auto close dates of the contracts in the chain.
        Corresponds by index with contract_sids.
    future_chain_predicates : dict
        A dict mapping root symbol to a predicate function which accepts a contract
    as a parameter and returns whether or not the contract should be included in the
    chain.

    Instances of this class are used by the simulation engine, but not
    exposed to the algorithm.
    """
    ...

    def contract_before_auto_close(self, dt_value):
        """
        Get the contract with next upcoming auto close date.
        """
        ...

    def contract_at_offset(self, sid, offset, start_cap):
        """
        Get the sid which is the given sid plus the offset distance.
        An offset of 0 should be reflexive.
        """
        ...

    def active_chain(self, starting_sid, dt_value):
        ...
