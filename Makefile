.PHONY: test
.PHONY: clean
.PHONY: install

test: 
	./run_tests
	
clean:
	./setup.py clean
	
install:
	./setup.py install
