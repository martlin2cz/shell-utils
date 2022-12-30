# photos classifier

An python tool which classifies the photos by the date taken.

## Installation/building

    $ python3.8 -m pip install .

## Basic usage
Run `$ ./classify-by-date.py testing-images/` to get the _histo_ output:


     70-01-01 : |
     21-10-30 : |
     21-12-15 : ||
     22-02-16 : |
     22-06-19 : ||

Specify the flag `--action` to configure whether to output the _histo_, just list the files or output them into directory structure (either by copiing or moving), like:

````
$ ./classify-by-date.py testing-images/
$ ls -R /tmp/classified-photos/
/tmp/classified-photos/:
21-10-30-unknown  21-12-15-unknown  22-02-16-unknown  22-06-19-unknown  70-01-01-unknown

/tmp/classified-photos/21-10-30-unknown:
dablovy-prdele.jpg

/tmp/classified-photos/21-12-15-unknown:
detaily-o-zasilce.jpg  zasilku-jsme-dorucili.jpg

/tmp/classified-photos/22-02-16-unknown:
kus-qeerka.jpg

/tmp/classified-photos/22-06-19-unknown:
kilobity.jpg  photos.jpg

/tmp/classified-photos/70-01-01-unknown:
empty-text-file.txt
````

## Further options
Use `--verbose` to more verbose output, and `--debug` for full debug logging.

Use standart `--help` or `-h` for full help.


