#!/usr/bin/python
"""
 inspired from /usr/share/doc/python-dns/examples/test5.py
 - SOA to get ref serial and primary ns
 - get NS list (don't use the primary to verify the list)
 - query each NS (except the primary !) and verify the serial returned
 TODO: use get_soa first and to detect the master (save one dns query !) :
"""

from __future__ import print_function
import sys
from optparse import OptionParser
try:
    import DNS
except ImportError:
    print("Error importing DNS, is pydns installed ? (python-dns on Debian)")
    sys.exit(4)

# initialize resolvers
DNS.ParseResolvConf()

def error_msg(mesg):
    """ simple error message managment """
    print(sys.argv[0], "ERROR:", mesg)
    sys.exit(2)

def main():
    """ main prog """
    usage = "Usage: %prog domain [options]"
    version_print = "0.4"
    description = "Check serial in a dns domain name SOA record, " \
                  "no output if ok by default."
    parser = OptionParser(usage,
                          description=description,
                          version=version_print)

    parser.add_option("-v", "--verbose",
                      action="store_true",
                      dest="verbose",
                      default=False,
                      help="Verbose output (default: %default)")
    # Set timeout for queries (pydns default: 30)
    parser.add_option("-t", "--timeout",
                      action="store",
                      type="int",
                      dest="timeout",
                      help="Timeout in seconds for each request " \
                           "(1 for SOA and 1 for each NS, default: %default)",
                      default=3)

    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        sys.exit(1)

    domain = args[0]
    nslist = get_ns(domain, options.verbose, options.timeout)
    if nslist:
        if options.verbose is True:
            print("According to the primary, nameservers are:")
    else:
        sys.exit(1)

    # used to compare serials
    serial1 = ""
    for nameserver in nslist:

        serial = get_soa(nameserver, domain, options.timeout)
        if options.verbose is True:
            print("  ", nameserver)
            print("      NS has serial", serial)

        # FIXME: suppose the first ns is the master
        # if serial1 is empty, first loop
        if not serial1:
            serial1 = serial
        else:
            if serial1 != serial:
                print("Warning: serials are different for %s:" % domain)
                print("Expected %s, found %s on %s" % \
                        (serial1, serial, nameserver))

def get_ns(domain, verbose, timeout):
    """ return NS servers for a given domain """
    # hm. this might fail if a server is off the air.
    request = DNS.Request(domain, qtype='SOA', timeout=timeout).req()
    if request.header['status'] != 'NOERROR':
        error_msg("received status of %s when attempting to look up SOA for %s" % \
                (request.header['status'], domain))
    primary, email, serial, refresh, retry, expire, minimum = \
            request.answers[0]['data']
    if verbose is True:
        print("Primary nameserver for domain %s is: %s" % (domain, primary))
    try:
        request = DNS.Request(domain, qtype='NS', server=primary, aa=1, timeout=timeout).req()
        if request.header['status'] != 'NOERROR':
            error_msg("received status of %s when attempting to query %s for %s NS" % \
                (request.header['status'], primary, domain))
        if request.header['aa'] != 1:
            error_msg("primary NS %s of %s doesn't believe that it's authoritative for %s!" % \
                domain, primary, domain)
        nslist = [x['data'] for x in request.answers]
        return nslist
    #pylint: disable=broad-except
    except Exception as error:
        error_msg("Problem getting NS on %s for %s: %s" % (primary, domain, error))
        return []


def get_soa(nameserver, domain, timeout):
    """ return SOA serial for a given nameserver """
    try:
        request = DNS.Request(domain,
                              qtype='SOA',
                              server=nameserver,
                              aa=1,
                              timeout=timeout).req()
        if request.header['status'] != 'NOERROR':
            error_msg("received status of %s when attempting to query %s for %s NS" % \
                (request.header['status'], nameserver, domain))
        if request.header['aa'] != 1:
            error_msg("NS %s doesn't believe that it's authoritative for %s!" % \
		nameserver, domain)
        primary, email, serial, refresh, retry, expire, minimum = \
            request.answers[0]['data']
        return serial[1]
    #pylint: disable=broad-except
    except Exception as error:
        error_msg("Problem using %s for %s domain: %s" % (nameserver, domain, error))

if __name__ == "__main__":
    main()
