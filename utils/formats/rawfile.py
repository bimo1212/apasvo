# encoding: utf-8
'''
@author:     Jose Emilio Romero Lopez

@copyright:  2013 organization_name. All rights reserved.

@license:    LGPL

@contact:    jemromerol@gmail.com

  This file is part of AMPAPicker.

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU Lesser General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import numpy as np

from utils import futils


class RawFile(object):
    """An abstract class representing a binary or plain text file."""

    datatypes = {'float16': 'f2', 'float32': 'f4', 'float64': 'f8'}
    byteorders = {'little-endian': '<', 'big-endian': '>', 'native': '='}

    def __init__(self):
        super(RawFile, self).__init__()

    def read(self):
        raise NotImplementedError

    def read_in_blocks(self, block_size):
        raise NotImplementedError

    def write(self, array):
        raise NotImplementedError


class BinFile(RawFile):
    """A binary file.

    Data type and byte-order info must be known in advance in order
        to read the data correctly.
    Attributes:
        dtype: Type of the data stored in the file.
        filename: Name of the file.
    """

    def __init__(self, filename, dtype='float64', byteorder='native'):
        """Inits a BinFile object.

        Args:
            filename: Name of the file.
            dtype: Data-type of the data stored in the file.
                Possible values are: 'float16', 'float32' and 'float64'.
                Default value is 'float64'.
            byteorder: Byte-order of the data stored in the file.
                Possible values are: 'little-endian', 'big-endian' and 'native'.
                Default value is 'native'.
        """
        super(BinFile, self).__init__()
        self.dtype = np.dtype(self.byteorders[byteorder] + self.datatypes[dtype])
        self.filename = filename

    def read(self):
        """Constructs a numpy array from the data stored in the file.

        Data-type and byte-order of the returned array are the object's same.
        """
        return np.fromfile(self.filename, dtype=self.dtype)

    def read_in_blocks(self, block_size=1024):
        """Lazy function (generator) that reads a binary file in chunks.

        Default chunk size is 1k.
        Data-type and byte-order of the returned data are the object's same.
        """
        with open(self.filename, 'rb') as f:
            chunk_size = block_size * self.dtype.itemsize
            for data in futils.read_in_chunks(f, chunk_size):
                yield np.frombuffer(data, dtype=self.dtype)

    def write(self, array):
        """Stores an array into the binary file."""
        return array.tofile(self.filename)


class TextFile(RawFile):
    """A plain text file containing numeric data.

    Attributes:
        dtype: Once data is read from file, this will be the data type
            of the resulting array.
        filename: Name of the file.
    """

    def __init__(self, filename, dtype='float64', byteorder='native'):
        """Inits a TextFile object.

        Args:
            filename: Name of the file.
            dtype: Data-type of the array data returned.
                Possible values are: 'float16', 'float32' and 'float64'.
                Default value is 'float64'.
            byteorder: Byte-order of the array data returned.
                Possible values are: 'little-endian', 'big-endian' and 'native'.
                Default value is 'native'.
        """
        super(TextFile, self).__init__()
        self.dtype = np.dtype(self.byteorders[byteorder] + self.datatypes[dtype])
        self.filename = filename

    def read(self, **kwargs):
        """Constructs a numpy array from the data stored in the file.

        Data-type and byte-order of the returned array are the object's same.

        The following arguments are taken from the documentation
        of the numpy function 'loadtxt'.
        Args:
            dtype: Data-type of the resulting array.
            comments: String indicating the start of a comment.
                Default: '#'.
            delimiter: String used to separate values.
                Default: ' '.
        """
        return np.loadtxt(self.filename, dtype=self.dtype, **kwargs)

    def read_in_blocks(self, block_size=1024):
        """Lazy function (generator) that reads a text file in chunks.

        Default chunk size is 1k characters.
        Data-type and byte-order of the returned data are the object's same.
        """
        with open(self.filename, 'r') as f:
            for data in futils.read_txt_in_chunks(f, block_size):
                yield np.array(data, dtype=self.dtype)

    def write(self, array, **kwargs):
        """Stores an array into the text file.

        The following arguments are taken from the
        documentation of the numpy function 'savetxt'.
        Args:
            fmt: A string format.
                Default value is '%.18e'.
            delimiter: Character separating columns.
                Default: ' '.
            newline: Character separating lines.
                Default: '\n'.
            header: String that will be written at the beginning
                of the file. Default: ''.
            footer: String that will be written at the end of the file.
                Default: ''.
            comments: String that will be prepended to header and footer
                to mark them as comments. Default: '# '.
        """
        return np.savetxt(self.filename, array, **kwargs)


def get_file_handler(filename, fmt='', dtype='float64', byteorder='native', **kwargs):
    """Gets a handler for a binary or text file.

    Args:
        filename: name of the file.
        fmt: The format of the data file to read.
            Possible values are 'binary', 'text' or ''.
            If '' is selected, the function will detect whether the file
            is a binary or a text file.
        dtype: Data-type of the numeric data stored in the file.
            Possible values are 'float16', 'float32' and 'float64'.
            Default value is 'float64'.
        byteorder: Byte-order of the numeric data stored in the file.
            Possible values are 'little-endian', 'big-endian' and 'native'.
            Default value is 'native'.

    Returns:
        A BinFile or TextFile object, depending of 'fmt'.
    """
    if isinstance(filename, file):
        filename = filename.name
    formats = ['binary', 'text']
    if fmt not in formats:
        fmt = 'text' if futils.istextfile(filename) else 'binary'
    if fmt == 'text':
        return TextFile(filename, dtype=dtype, byteorder=byteorder)
    else:
        return BinFile(filename, dtype=dtype, byteorder=byteorder)
