# photos classifier

An python tool which classifies the photos (or videos) by the date taken. Either just outputting in various form, or literally copiing or moving the actual files.

## More detailed description
The tool has three stages. First one loads all the photos and videos ("medias") from specified folders. Second stage classifies, groups, them by the given "groupper". The groupper is either "year", "month", "week", "day" or "hour" of the date the photo was taken or video recorded.

Finally, the collected groups gets outputted/executed. The simplest output is to just list all the files belonging to each group. Alternativelly a table outputting for example medias taken at the month _x_ and day _y_ of the month. Final form of output is to just copy or move the groups into the corresponding subdirectories.

## Installation/building

    $ cd photos_classifier
    $ python3.8 -m pip install .

## Basic usage
You have to allways tell _what_ you want to _do_, and _what_ directories to _look_ the media files _for_. The remaining arguments has configured defaults. Here's the example output of the _list_ format:
````
$ ./classify.py list testing-images/
      Thu 1970-01-01 | |
      Sat 2021-10-30 | |
      Wed 2021-12-15 | ||
      Wed 2022-02-16 | |
      Sun 2022-06-19 | ||
````
(Each `|` character corresponds to one media.)

The _table_ format:
````
$ ./classify.py table testing-images/
                 --- |    0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19  20  21  22  23
      Thu 1970-01-01 |    .
      Sat 2021-10-30 |                                                        .                                        
      Wed 2021-12-15 |                                                                                            ,    
      Wed 2022-02-16 |                                                                                            .    
      Sun 2022-06-19 |                                                ,                                                
````
(Dot character means one media at the given hour of the day, comma character means two.)

The _copy_ and _move_ actions works as follows:
````
$ ./classify.py copy testing-images/
$ ls -r 202*
2022-06-19_having-2-files:
photos.jpg  kilobity.jpg

2022-02-16_having-1-files:
kus-qeerka.jpg

2021-12-15_having-2-files:
zasilku-jsme-dorucili.jpg  detaily-o-zasilce.jpg

2021-10-30_having-1-files:
dablovy-prdele.jpg
````

## Common options
No matter what you want to do, there are some common options to be provided for all the actions.

### Loading the files
Specify one or more directories where to look for the media files. Use `--recurse` or `-r` to walk all of them recursivelly.

### The groupper
You can specify the unit of each group: _year_, _month_, _week_, _day_ or _hour_ by the `--groupper` or `-g` flag like so:
````
$ ./classify.py list --groupper=year testing-images/
                1970 | |
                2021 | |||
                2022 | |||
````
versus:
````
$ ./classify.py list --groupper=day testing-images/
      Thu 1970-01-01 | |
      Sat 2021-10-30 | |
      Wed 2021-12-15 | ||
      Wed 2022-02-16 | |
      Sun 2022-06-19 | ||
````
The default is _day_.

### The output format
When _list_ or _table_, you can choose what format (by flag `--row-format` / `--cell-format` or simply `-f`) you want to have use to output the files (usually their number). The basic one is _count_, which just outputs the number of the files in that group. Alternativelly, it outputs the histogram bar (_histo_) (default for the _list_ action) or the ASCII art scale (going from very blank to very "dark" character) (_scale_) (default for the _table_ action). More info avaiable by the `--help` commands.

Example of the _histo_ and _scale_ (with same _groupper_ and same _input directory_):
````
$ ./classify.py list --row-format=histo --groupper=day $DIRECTORY
      Sat 2021-05-22 | |||||||
      Sun 2021-05-23 | ||||
      Tue 2021-05-25 | |||||||
      Sat 2021-05-29 | ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
      Sat 2021-06-05 | ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
      Sun 2021-06-06 | |||||||||||||||||||||
      Tue 2021-06-08 | |||
      Wed 2021-06-09 | ||
      Sat 2021-06-12 | |
````

````
./classify.py table --cell-format=scale --compact --groupper=day $DIRECTORY
                 --- | 012345678901234567890123
      Sat 2021-05-22 |            . ,;         
      Sun 2021-05-23 |                ;        
      Tue 2021-05-25 |                  i      
      Sat 2021-05-29 |            HI8M!;.      
      Sat 2021-06-05 |        IM@.,!,8L; ;i,   
      Sun 2021-06-06 | Mi.                     
      Tue 2021-06-08 |          .       .  .   
      Wed 2021-06-09 |           .        .    
      Sat 2021-06-12 |                 .       
````

### The quoras and filling
You can limit the size of the group (to be required to have more than specified amount of medias) or oppositelly to consider as a group a date even if there was no medias whatsoever:
````
$ ./classify.py list --groupper=day --row-format=count testing-images/
      Thu 1970-01-01 | 1
      Sat 2021-10-30 | 1
      Wed 2021-12-15 | 2
      Wed 2022-02-16 | 1
      Sun 2022-06-19 | 2
````
Ignoring groups having less than 2 files:
````
$ ./classify.py list --groupper=day --row-format=count --remove-quora=2 testing-images/
      Wed 2021-12-15 | 2
      Sun 2022-06-19 | 2
````
Including even the empties:
````
$ ./classify.py list --groupper=day --row-format=count --include-empty testing-images/
      Sat 2021-10-30 | 1
      Sun 2021-10-31 | 0
      Mon 2021-11-01 | 0
            (...)
      Mon 2021-12-13 | 0
      Tue 2021-12-14 | 0
      Wed 2021-12-15 | 2
      Thu 2021-12-16 | 0
      Fri 2021-12-17 | 0
            (...)
      Fri 2022-06-17 | 0
      Sat 2022-06-18 | 0
      Sun 2022-06-19 | 2
````

Keep in mind the including empties and the quora has the exactly opposite effect. When using both, the quora cancels the empties.

### Further options
Use `--verbose` to more verbose output, and `--debug` for full debug logging.

Use standart `--help` or `-h` for full help of the whole script or any of its actions.


