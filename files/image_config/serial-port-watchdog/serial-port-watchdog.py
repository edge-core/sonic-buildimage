#!/usr/bin/env python

from __future__ import print_function, with_statement

import argparse
import logging
import logging.handlers
import os
import time
import signal
import socket
import sys

from collections import namedtuple

PRGNAME = 'serial-port-watchdog'

DEVFS_PATH = '/dev'
PROCFS_PATH = '/proc'

# According to procfs(5)
ProcStat = namedtuple( 'ProcStat', [
    'pid', 'comm', 'state', 'ppid', 'pgrp', 'session', 'tty_nr', 'tpgid',
    'flags', 'minflt', 'cminflt', 'majflt', 'cmajflt', 'utime', 'stime',
    'cutime', 'cstime', 'priority', 'nice', 'num_threads', 'itrealvalue',
    'starttime', 'vsize', 'rss', 'rsslim', 'startcode', 'endcode',
    'startstack', 'kstkesp', 'kstkeip', 'signal', 'blocked', 'sigignore',
    'sigcatch', 'wchan', 'nswap', 'cnswap', 'exit_signal', 'processor',
    'rt_priority', 'policy', 'delayacct_blkio_ticks', 'guest_time',
    'cguest_time', 'start_data', 'end_data', 'start_brk', 'arg_start',
    'arg_end', 'env_start', 'env_end', 'exit_code'
] )

# According to procfs(5)
ProcIo = namedtuple( 'ProcIo', [
    'rchar', 'wchar', 'syscr', 'syscw', 'read_bytes', 'write_bytes',
    'cancelled_write_bytes'
] )

class Process( object ):
    def __init__( self, pid, path=PROCFS_PATH ):
        self.pid = pid
        self.path = os.path.join( path, str( pid ) )
        self.childs = []
        self.parent = None

        self.stat = None

        self.io = None
        self.stack = None
        self.stackStartTime = None

    def refresh( self ):
        with open( os.path.join( self.path, 'stat' ) ) as f:
            data = f.read().rstrip().split()
            self.stat = ProcStat( *data )

    def getStat( self, key=None ):
        self.refresh()
        return self.stat

    def uid( self ):
        return '%s/%s' % ( self.pid, self.stat.starttime )

    def ppid( self ):
        return self.stat.ppid

    def name( self ):
        with open( os.path.join( self.path, 'comm' ) ) as f:
            return f.read().rstrip()

    def getTtyForFd( self, fd ):
        path = os.path.join( self.path, 'fd', str( fd ) )
        if not os.path.exists( path ):
            return ''
        return os.readlink( path )

    def getStack( self ):
        with open( os.path.join( self.path, 'stack' ) ) as f:
            return f.read()

    def getIo( self ):
        with open( os.path.join( self.path, 'io' ) ) as f:
            data = [ int( l.split( ': ' )[ 1 ] ) for l in f.readlines() ]
            return ProcIo( *data )

    def isUsingTty( self, tty ):
        return self.getTtyForFd( 0 ).endswith( tty )

    def checkStuck( self, content ):
        stack = self.getStack()

        found = False
        for match in content:
            if match in stack:
                found = True
                break

        if not found:
            self.io = None
            self.stack = None
            self.stackStartTime = None
            return 0

        io = self.getIo()

        if self.stack != stack or self.io != io:
            self.io = io
            self.stack = stack
            self.stackStartTime = time.time()
            return 0

        return time.time() - self.stackStartTime

    def __repr__( self ):
        return '<Process uid=%s>' % self.uid()

class ProcessMonitor( object ):
    def __init__( self, path=PROCFS_PATH ):
        self.path = path
        self.procs = {}
        self.filters = []
        self.checkers = []
        self.whitelist = []

    def addProcessFilter( self, func, *args ):
        self.filters.append( ( func, args ) )

    def addStuckChecker( self, func, *args ):
        self.checkers.append( ( func, args ) )

    def setWhitelist( self, whitelist ):
        self.whitelist = whitelist

    def shouldHandleProcess( self, proc ):
        matched = False
        for func, args in self.filters:
            if func( proc, *args ):
                matched = True
                break

        if not matched:
            return False

        name = proc.name()
        for item in self.whitelist:
            if item in name:
                return False

        return True

    def getRunningPids( self ):
        pids = []
        for entry in os.listdir( self.path ):
            if not entry.isdigit():
                continue
            pids.append( int( entry ) )
        return pids

    def killStuckProcess( self, proc, elapsed, kill, timeout ):
        if not elapsed:
            return

        if elapsed < timeout:
            if elapsed > timeout / 2:
                logging.info( 'process %d seems stuck, idle for %ds, waiting '
                              'some more time', proc.pid, elapsed )
            return

        logging.warning( 'process %d has been stuck for %d seconds, killing...',
                         proc.pid, elapsed )
        logging.info( 'process %d kernel stack\n%s', proc.pid, proc.stack )
        if kill:
            # XXX: SIGTERM sleep then if alive SIGKILL ?
            os.kill( proc.pid, signal.SIGKILL )

    def killStuckProcesses( self, kill, timeout ):
        for proc in self.procs.values():
            for checker, args in self.checkers:
                elapsed = checker( proc, *args )
                self.killStuckProcess( proc, elapsed, kill, timeout )

    def updatePid( self, pid ):
        p = Process( pid )

        # if the process is already monitored (previously running)
        r = self.procs.get( pid, None )
        if r:
            p.refresh()
            # if the process is still running
            if p.uid() == r.uid():
                logging.debug( 'process %d still running', pid )
                return
            # or the pid was reused but the process is different
            logging.debug( 'pid %d reused for another process', pid )
            del self.procs[ pid ]

        # check if the process is relevant for monitoring
        if not self.shouldHandleProcess( p ):
            return

        logging.debug( 'watching process %d', pid )
        p.refresh()
        self.procs[ pid ] = p

    def updateParenting( self ):
        # clear parent and childs for monitored processes
        for proc in self.procs.values():
            del proc.childs[:]
            proc.parent = None

        # set parent and childs for monitored processes
        for proc in self.procs.values():
            ppid = proc.ppid()
            parent = self.procs.get( ppid, None )
            if parent:
                proc.parent = parent
                parent.childs.append( proc )

    def update( self ):
        pids = self.getRunningPids()

        # remove defunct processes
        for pid in list(self.procs.keys()):
            if pid not in pids:
                logging.debug( 'process %d is defunct', pid )
                del self.procs[ pid ]

        # create or update running processes information
        for pid in pids:
            try:
                self.updatePid( pid )
            except:
                logging.warning( 'An issue occured whileupdating process %s',
                                 pid )
                raise

        #self.updateParenting()

def checkRootPermissions():
    if os.geteuid() != 0:
        logging.error( 'You must be root to use this feature' )
        sys.exit( 1 )

def getHostname():
    try:
        return socket.gethostname()
    except:
        return 'localhost'

def setupLogging( verbose=False ):
    loglevel = logging.DEBUG if verbose else logging.INFO
    dateFmt = '%Y-%m-%d %H:%M:%S'

    log = logging.getLogger()
    log.setLevel( logging.DEBUG )

    logOut = logging.StreamHandler( sys.stdout )
    logOut.setFormatter( logging.Formatter( '%(levelname)s: %(message)s' ) )
    logOut.setLevel( loglevel )
    log.addHandler( logOut )

    logSys = logging.handlers.SysLogHandler()
    # format to rfc5424 format
    fmt = '{} {}: %(message)s'.format( getHostname(), PRGNAME )
    logSys.setFormatter( logging.Formatter( fmt ) )
    logSys.setLevel( logging.WARNING )
    log.addHandler( logSys )
    try:
        # the connection to the syslog socket happens with the first message
        log.info( 'Attaching to syslog' )
    except:
        log.warning( 'Failed open syslog' )

def listParser( value ):
    if not value.strip():
        return []
    return value.split( ',' )

def ttyParser( dev, path=DEVFS_PATH ):
    if not dev.startswith( DEVFS_PATH ):
        dev = os.path.join( DEVFS_PATH, dev )
    if not os.path.exists( dev ):
        raise argparse.ArgumentTypeError( '%s is not a device' % dev )
    return dev

def parseArgs( args ):
    parser = argparse.ArgumentParser()

    parser.add_argument( '-d', '--dry-run', action='store_true',
        help='only print processes that would be killed' )
    parser.add_argument( '-f', '--funcs', default=[ 'tty_' ], type=listParser,
        help='functions to look for in the stack trace' )
    parser.add_argument( '-i', '--interval', default=60, type=float,
        help='interval at which to check the procfs' )
    parser.add_argument( '-k', '--timeout', default=3600, type=float,
        help='timeout for which a process gets killed' )
    parser.add_argument( '-t', '--tty', default='ttyS0', type=ttyParser,
        help='tty to check for stuck process' )
    parser.add_argument( '-v', '--verbose', action='store_true',
        help='print all debug messages' )
    parser.add_argument( '-w', '--whitelist', default=[ 'agetty' ], type=listParser,
        help='whitelist programs that should never be killed' )

    return parser.parse_args( args )

def main( args ):
    args = parseArgs( args )

    setupLogging( args.verbose )
    checkRootPermissions()

    m = ProcessMonitor()
    m.addProcessFilter( Process.isUsingTty, args.tty )
    m.addStuckChecker( Process.checkStuck, args.funcs )
    m.setWhitelist( args.whitelist )

    while True:
        logging.debug( 'updating processes' )
        m.update()
        m.killStuckProcesses( kill=( not args.dry_run ), timeout=args.timeout )
        time.sleep( args.interval )

    return 0

if __name__ == '__main__':
    sys.exit( main( sys.argv[ 1: ] ) )

