import logging
import pandas
import typing

from dataclasses import dataclass

###############################################################################

""" The logger. """
LOGGER = logging.getLogger("labeler")

###############################################################################

@dataclass(frozen = True)
class Condition:
    column: str
    operator: str
    value: typing.Any


@dataclass(frozen = True)
class Rule:
    index: int
    label: str
    condition: Condition

def load_rules(filename):
    rules_csv = pandas.read_csv(filename, delimiter="\t")
    #TODO check header

    rules_list = [ load_rule(i, e) for i,e in rules_csv.iterrows() ]
    return rules_list

def load_rule(index, entry):
    LOGGER.debug("Parsing rule %d: %s", index, entry)
    label = entry["Label"]

    condition = load_condition(entry, 1)

    return Rule(index, label, condition)

def load_condition(entry, condition_index):
    column = entry[f"column-{condition_index}"]
    operator = entry[f"operator-{condition_index}"]
    value = entry[f"value-{condition_index}"]

    return Condition(column, operator, value)

###############################################################################

###############################################################################

def run(infile, rules_file, column_name, override, dry_run, outfile):
    rules = load_rules(rules_file)
    print(str(rules))

