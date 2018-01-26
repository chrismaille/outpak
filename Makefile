test:
	nosetests --with-coverage --cover-package=outpak

break:
	nosetests -v --nocapture --ipdb

coverage:
	coverage report -m