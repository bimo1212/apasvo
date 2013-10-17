#!/usr/bin/python2.7
# encoding: utf-8
'''
generator

A tool to generate synthetic seismic signal

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

import argparse
import os
import sys

from _version import __version__
from utils import clt, parse, futils
from utils.formats import rawfile
from picking import eqgenerator


def print_settings(args):
    """"""
    sys.stdout.write("\nGeneral settings:\n")
    sys.stdout.write("%30s: %s\n" % ("Signal frequency(Hz)",
                                     args.fs))
    sys.stdout.write("%30s: %s\n" % ("Length(s)",
                                     args.length))
    sys.stdout.write("%30s: %s\n" % ("Start time(s)",
                                     args.t_event))
    sys.stdout.write("%30s: %s\n" % ("Noise power(dB))",
                                     args.P_noise_db))
    if not args.FILEIN:
        sys.stdout.write("%30s: %s\n" % ("Event power(dB)",
                                         args.gen_event_power))
        sys.stdout.write("\nFilter bank settings:\n")
        sys.stdout.write("%30s: %s\n" % ("Start frequency(Hz)",
                                       args.f_low))
        sys.stdout.write("%30s: %s\n" % ("End frequency(Hz)",
                                       args.f_high))
        sys.stdout.write("%30s: %s\n" % ("Subband bandwidth(Hz)",
                                       args.bandwidth))
        sys.stdout.write("%30s: %s\n" % ("Subband overlap(Hz)",
                                       args.overlap))
        sys.stdout.write("%30s: %s\n" % ("Start envelope length(s)",
                                       args.low_period))
        sys.stdout.write("%30s: %s\n" % ("End envelope length(s)",
                                       args.high_period))
        sys.stdout.write("%30s: %s\n" % ("Start amplitude",
                                       args.low_amp))
        sys.stdout.write("%30s: %s\n" % ("End amplitude",
                                       args.high_amp))

    sys.stdout.write("\n")
    sys.stdout.flush()


def generate(FILEIN, length, t_event, output, gen_event_power=5.0, n_events=1,
             gen_noise_coefficients=False, output_format='binary',
             datatype='float64', byteorder='native', **kwargs):
    """"""
    # Configure generator
    clt.print_msg("Configuring generator... ")
    generator = eqgenerator.EarthquakeGenerator(**kwargs)
    clt.print_msg("Done\n")
    # Load noise coefficients
    if gen_noise_coefficients:
        if futils.istextfile(gen_noise_coefficients):
            f = open(gen_noise_coefficients, 'r')
        else:
            f = open(gen_noise_coefficients, 'rb')
        clt.print_msg("Loading noise coefficients from %s... " %
                         f.name)
        generator.load_noise_coefficients(f, dtype=datatype,
                                          byteorder=byteorder)
        clt.print_msg("Done\n")
    # Process input files
    basename, ext = os.path.splitext(output)
    filename_out = output
    if FILEIN:
        fileno = 0
        for f in FILEIN:
            fin_handler = rawfile.get_file_handler(f, dtype=datatype,
                                                   byteorder=byteorder)
            clt.print_msg("Loading seismic signal from %s... " %
                          fin_handler.filename)
            signal = fin_handler.read()
            clt.print_msg("Done\n")
            if len(FILEIN) > 1:
                filename_out = "%s%02.0i%s" % (basename, fileno, ext)
                fileno += 1
            clt.print_msg("Generating artificial signal in %s... " %
                             filename_out)
            eq = generator.generate_earthquake(length, t_event,
                                               gen_event_power, signal)
            if output_format == 'text':
                fout_handler = rawfile.TextFile(filename_out, dtype=datatype,
                                            byteorder=byteorder)
            else:
                fout_handler = rawfile.BinFile(filename_out, dtype=datatype,
                                              byteorder=byteorder)
            fout_handler.write(eq)
            clt.print_msg("Done\n")
    else:
        for i in xrange(n_events):
            if n_events > 1:
                filename_out = "%s%02.0i%s" % (basename, i, ext)
            clt.print_msg("Generating artificial signal in %s... " %
                             filename_out)
            eq = generator.generate_earthquake(length, t_event,
                                               gen_event_power)
            if output_format == 'text':
                fout_handler = rawfile.TextFile(filename_out, dtype=datatype,
                                                byteorder=byteorder)
            else:
                rawfile.BinFile(filename_out, dtype=datatype,
                                byteorder=byteorder)
            fout_handler.write(eq)
            clt.print_msg("Done\n")


def main(argv=None):
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_version_message = '%%(prog)s %s' % program_version
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Jose Emilio Romero Lopez.
  Copyright 2013. All rights reserved.

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

USAGE
''' % program_shortdesc

    try:
        # Setup argument parser
        parser = parse.CustomArgumentParser(description=program_license,
                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                fromfile_prefix_chars='@')
        #Create common arguments for all commands
        parser = argparse.ArgumentParser()
        parser.add_argument('-V', '--version', action='version',
                            version=program_version_message)
        parser.add_argument("--datatype",
                            choices=['float16', 'float32', 'float64'],
                            default='float64',
                            help='''
        If the input files are in binary format this will be
        the datatype used for reading it.
                            ''')
        parser.add_argument("--byteorder",
                                   choices=['little-endian', 'big-endian',
                                            'native'],
                                   default='native',
                                   help='''
        If the input files are in binary format this will be the byte-order
        of the selected datatype. Default choice is hardware native.
                                   ''')
        parser.set_defaults(func=generate)
        # Create arguments for "generate" command
        parser.add_argument("FILEIN", nargs='*',
                                     action=parse.GlobInputFilenames,
                                     help='''
        Binary or text file containing a seismic-like signal. If not specified
        then a synthetic earthquake is generated.
        ''')
        parser.add_argument("-o", "--output",
                                     default='eq.out',
                                     help='''
        Output file. If none is specified will generate an output file
        for each input file.
        ''')
        parser.add_argument("--output-format",
                                     choices=["binary", "text"],
                                     default="binary",
                                     help='''
        Output file format. Default value is 'binary'.
        ''')
        parser.add_argument("-n", "--n-events",
                                     type=parse.positive_int,
                                     default=1,
                                     help='''
        Number of events generated, one file for each event.
        ''')
        parser.add_argument("-f", "--frequency", type=parse.positive_float,
                                     default=50.0,
                                     dest='fs',
                                     help="Signal frequency.")
        parser.add_argument("-l", "--length",
                                     type=parse.positive_int,
                                     default=600.0,
                                     help='''
        Length of the generated sequence. Default value is 600 seconds.
        ''')
        parser.add_argument("-t", "--t-event",
                                     type=parse.positive_float,
                                     required=True,
                                     help='''
        Point in time at which the event will be generated.
        ''')
        parser.add_argument("-p", "--gen-event-power",
                                     type=float,
                                     default=5.0,
                                     help='''
        Power of the generated seismic event. Default value is 5 dB.
        ''')
        parser.add_argument("--gen-noise-power",
                                     type=float,
                                     dest='P_noise_db',
                                     default=0.0,
                                     help='''
        Background noise power. Default value is 0 dB.
        ''')
        parser.add_argument("--gen-noise-coefficients",
                                     type=parse.filein,
                                     help='''
        Binary or text file containing the coefficients that characterize
        the noise. If not specified then unfiltered white noise is used for
        modeling the background noise.
        ''')
        parser.add_argument("--gen-low-period",
                                     type=parse.positive_float,
                                     dest='low_period',
                                     default=50.0,
                                     help='''
        Initial length of the noise envelope for the different bands.
        Default value is 50.
        ''')
        parser.add_argument("--gen-high-period",
                                     type=parse.positive_float,
                                     dest='high_period',
                                     default=10.0,
                                     help='''
        Final length of the noise envelope for the different bands.
        Default value is 10.
        ''')
        parser.add_argument("--gen-bandwidth",
                                     type=parse.positive_float,
                                     dest='bandwidth',
                                     default=4.0,
                                     help='''
        Channel bandwidth of the filter bank used to generate
        the synthetic earthquake. Default value is 4 Hz.
        ''')
        parser.add_argument("--gen-overlap",
                                     type=parse.positive_float,
                                     dest='overlap',
                                     default=1.0,
                                     help='''
        Overlap of the filter bank used to generate the
        synthetic earthquake. Default value is 1 Hz.
        ''')
        parser.add_argument("--gen-f-low",
                                     type=parse.positive_float,
                                     dest='f_low',
                                     default=2.0,
                                     help='''
        Start frequency of the filter bank used to generate
        the synthetic earthquake. Default value is 2Hz.
        ''')
        parser.add_argument("--gen-f-high",
                                     type=parse.positive_float,
                                     dest='f_high',
                                     default=18.0,
                                     help='''
        End frequency of the filter bank used to generate
        the synthetic earthquake. Default value is 18Hz.
        ''')
        parser.add_argument("--gen-low-amp",
                                     type=parse.positive_float,
                                     dest='low_amp',
                                     default=0.2,
                                     help='''
        Start amplitude of the filter bank used to generate
        the synthetic earthquake. Default value is 0.2.
        ''')
        parser.add_argument("--gen-high-amp",
                                     type=parse.positive_float,
                                     dest='high_amp',
                                     default=0.1,
                                     help='''
        End amplitude of the filter bank used to generate
        the synthetic earthquake. Default value is 0.1.
        ''')
        # Parse the args and call whatever function was selected
        args, _ = parser.parse_known_args()
        print_settings(args)

    except Exception, e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help\n")
        return 2

    args.func(**vars(args))

if __name__ == "__main__":
    sys.exit(main())