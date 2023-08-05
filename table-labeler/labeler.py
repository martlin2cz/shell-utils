import logging
import pandas
from dataclasses import dataclass

###############################################################################

""" The logger. """
LOGGER = logging.getLogger("labeler")

###############################################################################

@dataclass(frozen = True)
class Rule:
    index: int
    label: str
    #TODO conditions

def load_rules(filename):
    rules_csv = pandas.read_csv(filename, delimiter="\t")
    #TODO check header

    rules_list = [ load_rule(i, e) for i,e in rules_csv.iterrows() ]
    return rules_list

def load_rule(index, entry):
    LOGGER.debug("Parsing rule %d: %s", index, entry)
    label = entry["Label"]


    return Rule(index, label)

###############################################################################

###############################################################################

def run(infile, rules_file, column_name, override, dry_run, outfile):
    rules = load_rules(rules_file)
    print(str(rules))

