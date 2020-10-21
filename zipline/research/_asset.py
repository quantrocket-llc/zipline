#
# Copyright 2020 QuantRocket LLC
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

# Local cache of {bundle code: AssetFinder}. This is to ensure that
# research functions share the same AssetFinder, which is necessary
# for continuous futures because the AssetFinder that creates the
# continuous future stores it in its asset cache and retrieves it
# from there on queries. If continuous futures are queried using a
# different AssetFinder than the one that created the continuous
# future, it will result in SidsNotFound.
asset_finder_cache = {}
