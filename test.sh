#!/bin/bash
# test check_soa return codes

stderr=$(mktemp --suffix=.test_check_soa)

./check_soa iroqwa.org --verbose > $stderr 2>&1
if [ $? -ne 0 ]
then
	echo "TEST FAILED: existent domain don't return 0, output:"
	cat $stderr
	rm --force $stderr
	exit 1
else
	echo "OK: existent domain return 0"
fi

./check_soa nonexistentdomain.tld --verbose > $stderr 2>&1
if [ $? -ne 1 ]
then
	echo "TEST FAILED: nonexistent domain don't return 1, output:"
	cat $stderr
	rm --force $stderr
	exit 1
else
	echo "OK: nonexistent domain return 1"
fi

# simulate broken ns
sudo iptables --flush
sudo iptables --append OUTPUT --destination ns2.iroqwa.org --jump DROP

./check_soa iroqwa.org --verbose > $stderr 2>&1
if [ $? -ne 1 ]
then
	echo "TEST FAILED: existent domain with unreachable ns don't return 1, output:"
	cat $stderr
	rm --force $stderr
	exit 1
else
	echo "OK: existent domain with unreachable ns return 1"
fi

rm --force $stderr
sudo iptables --flush
