The script FgTranslator.py converts an XML file exported from the Fantasy Grounds application into a text file that is human readable.

Not all of the data is converted:
  spell lists are skipped
  most descriptions are skipped
  information not necessary for game play is skipped.

Usage:
  python FgTranslator.py fg_char.xml > fg_char.txt