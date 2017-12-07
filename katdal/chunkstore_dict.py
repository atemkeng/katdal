################################################################################
# Copyright (c) 2017-2018, National Research Foundation (Square Kilometre Array)
#
# Licensed under the BSD 3-Clause License (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy
# of the License at
#
#   https://opensource.org/licenses/BSD-3-Clause
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

"""A store of chunks (i.e. N-dimensional arrays) based on a dict of arrays."""

from .chunkstore import ChunkStore, ChunkNotFound, BadChunk


class DictChunkStore(ChunkStore):
    """A store of chunks (i.e. N-dimensional arrays) based on a dict of arrays.

    This interprets all keyword arguments as NumPy arrays and stores them in
    an `arrays` dict. Each array is identified by its corresponding keyword.
    New arrays cannot be added via :meth:`put` - they all need to be in place
    at store initialisation (or can be added afterwards via direct insertion
    into the `arrays` dict). The `put` method is only useful for in-place
    modification of existing arrays.
    """

    def __init__(self, **kwargs):
        error_map = {KeyError: ChunkNotFound, IndexError: ChunkNotFound}
        super(DictChunkStore, self).__init__(error_map)
        self.arrays = kwargs

    def get(self, array_name, slices, dtype):
        """See the docstring of :meth:`ChunkStore.get`."""
        chunk_name, shape = self.chunk_metadata(array_name, slices, dtype=dtype)
        with self._standard_errors(chunk_name):
            chunk = self.arrays[array_name][slices]
        if dtype != chunk.dtype:
            raise BadChunk('Chunk {!r}: requested dtype {} differs from '
                           'actual dtype {}'
                           .format(chunk_name, dtype, chunk.dtype))
        return chunk

    def put(self, array_name, slices, chunk):
        """See the docstring of :meth:`ChunkStore.put`."""
        self.chunk_metadata(array_name, slices, chunk=chunk)
        self.get(array_name, slices, chunk.dtype)[:] = chunk

    get.__doc__ = ChunkStore.get.__doc__
    put.__doc__ = ChunkStore.put.__doc__
