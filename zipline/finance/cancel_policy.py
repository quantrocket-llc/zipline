#
# Copyright 2016 Quantopian, Inc.
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
import abc

from abc import abstractmethod
from six import with_metaclass

from zipline.gens.sim_engine import SESSION_END


class CancelPolicy(with_metaclass(abc.ABCMeta)):
    """Abstract cancellation policy interface.
    """

    @abstractmethod
    def should_cancel(self, event):
        """Should all open orders be cancelled?

        Parameters
        ----------
        event : enum-value
            An event type, one of:
              - :data:`zipline.gens.sim_engine.BAR`
              - :data:`zipline.gens.sim_engine.DAY_START`
              - :data:`zipline.gens.sim_engine.DAY_END`
              - :data:`zipline.gens.sim_engine.MINUTE_END`

        Returns
        -------
        should_cancel : bool
            Should all open orders be cancelled?
        """
        pass


class EODCancel(CancelPolicy):
    """
    This policy cancels open orders at the end of the day. This is the default
    policy and does not need to be explicitly set. In live trading, this cancel
    policy will cause orders to be submitted with a Tif (time-in-force) of DAY.

    Parameters
    ----------
    warn_on_cancel : bool, optional
        Should a warning be raised if this causes an order to be cancelled?
    """
    def __init__(self, warn_on_cancel: bool = True):
        self.warn_on_cancel = warn_on_cancel

    def should_cancel(self, event):
        return event == SESSION_END


class NeverCancel(CancelPolicy):
    """
    With this policy, orders are never automatically canceled. In live trading, this
    cancel policy will cause orders to be submitted with a Tif (time-in-force) of GTC
    (Good-till-canceled).

    Examples
    --------
    Set the cancel policy to NeverCancel::

        from zipline.api import set_cancel_policy, cancel_policy
        def initialize(context):
            set_cancel_policy(cancel_policy.NeverCancel())
    """
    def __init__(self):
        self.warn_on_cancel = False

    def should_cancel(self, event):
        return False
