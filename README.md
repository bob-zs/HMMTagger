Inside is a primitive Hidden Markov Model Part of Speech tagger.

To run:
$ python HMMTagger.py <.pos file to base tables from> <token-per-line txt file to tag>

The program needs at least 2 files, the pos file to base the tables from and the txt file to tag. The program will output "sys.pos" file which will show the tags of the txt file. However, if you provide an additional 3rd file name, the output file will be that name.

Thus,

$ python HMMTagger training.pos development.txt myOutput.pos

will output a tagged version of "development.txt" called "myOutput.pos".