#!/bin/bash
# test check_soa.py return codes
# use sudo and iptables to simulate unreachable ns
# flush all iptables rules at the end

which sudo > /dev/null 2>&1 || exit 1
which iptables > /dev/null 2>&1 || exit 1

stderr=$(mktemp --suffix=.test_check_soa.py)

./check_soa.py iroqwa.org --verbose > $stderr 2>&1
if [ $? -ne 0 ]
then
	echo "TEST FAILED: existent domain don't return 0, output:"
	cat $stderr
	rm --force $stderr
	exit 1
else
	echo "OK: existent domain return 0"
fi

./check_soa.py nonexistentdomain.tld --verbose > $stderr 2>&1
if [ $? -ne 2 ]
then
	echo "TEST FAILED: nonexistent domain don't return 1, output:"
	cat $stderr
	rm --force $stderr
	exit 1
else
	echo "OK: nonexistent domain return 1"
fi

echo "Simulate broken ns (thanks 'sudo iptables')"
sudo iptables --flush
sudo iptables --append OUTPUT --destination ns2.iroqwa.org --jump DROP

./check_soa.py iroqwa.org --verbose > $stderr 2>&1
if [ $? -ne 2 ]
then
	echo "TEST FAILED: existent domain with unreachable ns don't return 1, output:"
	cat $stderr
	rm --force $stderr
	exit 1
else
	echo "OK: existent domain with unreachable ns return 1"
fi

rm --force $stderr
echo "Flushing iptables "
sudo iptables --flush
