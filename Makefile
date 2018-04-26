test:
	nosetests --with-coverage --cover-package=outpak --cover-min-percentage=80
	pydocstyle --match-dir=outpak
	pycodestyle --max-line-length=120 outpak/

break:
	nosetests -v --nocapture --ipdb

coverage:
	coverage report -m