.PHONY: test
.PHONY: clean
test: 
	./run_tests
	
clean:
	find . -name "*.py[c|o]" | xargs rm -v 
