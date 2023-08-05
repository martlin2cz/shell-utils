import logging
import pandas
import typing

from dataclasses import dataclass

###############################################################################

""" The logger. """
LOGGER = logging.getLogger("labeler")


""" The value used when the rule doesn't match """
NO_LABEL = ""
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

###############################################################################

def load_rules(filename):
    LOGGER.info("Loading rules from file %s", filename)
    rules_csv = pandas.read_csv(filename, delimiter="\t")
    #TODO check header

    rules_csv_rows = rules_csv.iterrows()
    rules_list = [ load_rule(i, e) for i,e in rules_csv_rows ]

    LOGGER.info("Loaded in total %d rules", len(rules_list))
    return rules_list

def load_rule(index, entry):
    LOGGER.debug("Parsing rule %d: %s", index, dict(entry))
    
    #TODO try-catch
    label = entry["Label"]

    condition = load_condition(entry, 1)

    return Rule(index, label, condition)

def load_condition(entry, condition_index):
    column = entry[f"column-{condition_index}"]
    operator = entry[f"operator-{condition_index}"]
    value = entry[f"value-{condition_index}"]

    return Condition(column, operator, value)

###############################################################################

def load_table(filename):
    LOGGER.info("Loading input table from file %s", filename)
    table = pandas.read_csv(filename, delimiter=";")

    LOGGER.info("Loaded input table of %d rows, %d columns: %s", len(table), len(table.columns), table.columns)
    return table

def save_table(table, filename):
    pandas.save_csv(filename, delimiter="\t")

###############################################################################

def check_and_apply(rules, table, column_name, override):
    if column_name not in table.columns:
        position = len(table.columns)

        LOGGER.info("Creating the new column of name: %s", column_name)
        table.insert(position, column_name, NO_LABEL)

    apply(rules, table, column_name, override)

def apply(rules, table, column_name, override):
    for rule_index, rule in enumerate(rules):
        
        values = [compue_label_column_value(rule_index, rule, column_name, override, row_index, row) for row_index, row in table.iterrows() ]

def compue_label_column_value(rule_index, rule, column_name, override, row_index, row):
    LOGGER.debug("Computing new label of row %d: %s for rule %d:  %s", row_index, dict(row), rule_index, rule)
 
    try:
        matching = matches_condition(rule.condition, row, rule_index, row_index)
        current_value = row[column_name]
        already_has = len(current_value) > 0
        new_value = rule.label

        if not matching:
            LOGGER.debug("Ignoring: row %d: %s doesn't match rule %d condition %s", row_index, dict(row), rule_index, rule.condition)
            return current_value
        else:
            if already_has:
                if override:
                    LOGGER.debug("Keeping: row %d: %s matches rule %d condition %s, but already has a value and override is off", row_index, dict(row), rule_index, rule.condition)
                    return current_value
                else:
                    LOGGER.debug("Replacing: row %d: %s matches rule %d condition %s and already has a value, but override is on", row_index, dict(row), rule_index, rule.condition)
                    return new_value
            else:
                LOGGER.debug("Setting: row %d: %s matches rule %d condition %s and hasnť a value yet", row_index, dict(row), rule_index, rule.condition)
                return new_value

    except Exception as ex:
        LOGGER.error(f"Row %d %s label computation failed: %s", row_index, dict(row), ex)


def matches_condition(condition, row, rule_index, row_index):
    try:
        if condition.column not in row:
            raise ValueError(f"The row {row_index} doesn't have {condition.column} column") 
        column_value = row[condition.column]
    
        return matches(column_value, condition.operator, condition.value)
    except Exception as ex:
        LOGGER.error("Rule %d condition %s check of row %d failed: %s", rule_index, condition, row_index, ex)
        return False

def matches(actual_value, operator, value):
    if operator in ["=", "==", "is", "equal"]:
        return (actual_value == value)

    if operator in ["<"]:
        return (float(actual_value) < float(value))
    
    if operator in [">"]:
        return (float(actual_value) > float(value))



    raise ValueError("Unsupported operator: " + operator)


###############################################################################


def run(infile, rules_file, column_name, override, dry_run, outfile):
    rules = load_rules(rules_file)
    table = load_table(infile)

    check_and_apply(rules, table, column_name, override)

    if not dry_run:
        save_table(table, outfile)
