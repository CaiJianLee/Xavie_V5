'''
***
Modified generic daemon class
***
'''

# Core modules
from __future__ import print_function
import atexit
import errno
import os
import sys
import time
import signal
import subprocess
import ctypes
from ee.common import utility
from ee.common import logger

class Daemon(object):
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, process, stdin=os.devnull,
                 stdout=logger.pipe_w, stderr=logger.pipe_w,
                 home_dir='.', umask=0o22, verbose=1,
                 use_gevent=False):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        os.system("mkdir -p %s >/dev/null"%(utility.get_pid_path()))
        self.pidfile = utility.get_pid_path() + "/%s.pid"%(process)
        self.home_dir = home_dir
        self.verbose = verbose
        self.umask = umask
        self.daemon_alive = True
        self.use_gevent = use_gevent
        self.process = process

    def log(self, *args):
        if self.verbose >= 1:
            print(*args)

    def _set_process_name(self):
        argc = ctypes.c_int()
        argv = ctypes.POINTER(ctypes.c_char_p)()
        ctypes.pythonapi.Py_GetArgcArgv(ctypes.byref(argc), ctypes.byref(argv))
        lib_name = utility.get_lib_path() + "/libsgutil.so"
        libutil = ctypes.cdll.LoadLibrary(lib_name)
        libutil.spt_init(argc, argv)
        libutil.setproctitle(self.process)

    def daemonize(self):
        """
        Do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # Exit first parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write(
                "fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # Decouple from parent environment
        os.chdir(self.home_dir)
        os.setsid()
        os.umask(self.umask)

        # Do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # Exit from second parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write(
                "fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
        
        if sys.platform != 'darwin':  # This block breaks on OS X
            # Redirect standard file descriptors
            sys.stdout.flush()
            sys.stderr.flush()
            if (True == isinstance(self.stdin, str)):
                si = open(self.stdin, 'r')
            else:
                si = self.stdin
            if (True == isinstance(self.stdout, str)):
                so = open(self.stdout, 'a+')
            else:
                so = self.stdout
            
            if self.stderr:
                if (True == isinstance(self.stderr, str)):
                    try:
                        se = open(self.stderr, 'a+', 0)
                    except ValueError:
                        # Python 3 can't have unbuffered text I/O
                        se = open(self.stderr, 'a+', 1)
                else:
                    se = self.stderr
            else:
                se = so
            os.dup2(si.fileno(), sys.stdin.fileno())
            os.dup2(so.fileno(), sys.stdout.fileno())
            os.dup2(se.fileno(), sys.stderr.fileno())
        self._set_process_name()


        def sigterm_handler(signum, frame):
            self.daemon_alive = False
            sys.exit()

        '''
        if self.use_gevent:
            import gevent
            gevent.reinit()
            gevent.signal(signal.SIGTERM, sigterm_handler, signal.SIGTERM, None)
            gevent.signal(signal.SIGINT, sigterm_handler, signal.SIGINT, None)
        else:
            signal.signal(signal.SIGTERM, sigterm_handler)
            signal.signal(signal.SIGINT, sigterm_handler)
        '''
        # self.log("Started")

        # Write pidfile
        '''
        atexit.register(
            self.delpid)  # Make sure pid file is removed if we quit
        '''
        atexit.register(lambda: os.remove(self.pidfile))
        pid = str(os.getpid())
        open(self.pidfile, 'w+').write("%s\n" % pid)

    def delpid(self):
        try:
            # the process may fork itself again
            pid = int(open(self.pidfile, 'r').read().strip())
            if pid == os.getpid():
                os.remove(self.pidfile)
        except OSError as e:
            if e.errno == errno.ENOENT:
                pass
            else:
                raise

    def start(self, *args, **kwargs):
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = open(self.pidfile, 'r')
            last_pid = pf.read().strip()
            pf.close()
            pid = int(last_pid)
        except Exception:
            pid = None

        if pid:
            p = subprocess.Popen('ps -ef | grep %d | grep %s | grep -v grep'%(pid, self.process), shell=True,
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for line in p.stdout.readlines():
                sys.stderr.write("%s is already running, pid = %s\n"%(self.process, pid))
                sys.exit(1)
            os.system("rm -rf %s >/dev/null"%(self.pidfile))

        # Start the daemon
        self.daemonize()
        self.run(*args, **kwargs)

    def stop(self):
        """
        Stop the daemon
        """

        if self.verbose >= 1:
            self.log("Stopping...")

        # Get the pid from the pidfile
        pid = self.get_pid()

        if not pid:
            message = "pidfile %s does not exist. Not running?\n"
            sys.stderr.write(message % self.pidfile)

            # Just to be sure. A ValueError might occur if the PID file is
            # empty but does actually exist
            if os.path.exists(self.pidfile):
                os.remove(self.pidfile)

            return  # Not an error in a restart

        # Try killing the daemon process
        try:
            i = 0
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
                i = i + 1
                if i % 10 == 0:
                    os.kill(pid, signal.SIGHUP)
        except OSError as err:
            if err.errno == errno.ESRCH:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(err))
                sys.exit(1)

        self.log("Stopped")

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def get_pid(self):
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        except SystemExit:
            pid = None
        return pid

    def is_running(self):
        pid = self.get_pid()

        if pid is None:
            self.log('Process is stopped')
            return False
        elif os.path.exists('/proc/%d' % pid):
            self.log('Process (pid %d) is running...' % pid)
            return True
        else:
            self.log('Process (pid %d) is killed' % pid)
            return False

    def run(self):
        """
        You should override this method when you subclass Daemon.
        It will be called after the process has been
        daemonized by start() or restart().
        """
        pass
        #raise NotImplementedError