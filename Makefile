all:
	cat Makefile

clean:
	rm -rf build dist

egg:
	python2.4 setup.py sdist

dist4:
	python2.6 setup.py sdist upload -r ourbasket
