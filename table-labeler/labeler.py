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
    LOGGER.info("Saving output table to file %s", filename)
    
    table.to_csv(filename, sep=";")
    LOGGER.info("Saved output table.")
    
###############################################################################

def check_and_apply(rules, table, column_name, allow_override, rewrite_strategy):
    if column_name not in table.columns:
        position = len(table.columns)

        LOGGER.info("Creating the new column of name: %s", column_name)
        table.insert(position, column_name, NO_LABEL)

    apply(rules, table, column_name, allow_override, rewrite_strategy)

def apply(rules, table, column_name, allow_override, rewrite_strategy):

    new_labels_count = 0

    values = []
    for row_index, row in table.iterrows():
        original_label = row[column_name]
        current_label = None
        the_chosen_rule = None
        
        LOGGER.debug(">>> Computing label for row %d: %s", row_index, dict(row))
        for rule_index, rule in enumerate(rules):
            resolution = compute_resolution(rule, rewrite_strategy, allow_override, row, original_label, current_label)
            LOGGER.debug("Rule %d: %s", rule_index, resolution)
            #TODO log error instead of debug if error

            applicable = resolution in [SET_NEW_LABEL, REPLACE_BY_NEW_LABEL, OVERRIDE_PREVIOUS_RULE]

            if applicable:
                the_chosen_rule = rule
                current_label = rule.label

        new_label = None
        if the_chosen_rule:
            new_label = the_chosen_rule.label
            LOGGER.debug("<<< Computed new label by rule %d, %s", rule_index, rule)
            LOGGER.info("Label for row %d computed as %s", row_index, new_label)
            new_labels_count = new_labels_count + 1
        else:
            new_label = ""
            LOGGER.info("No matching rule found for row %d: %s", row_index, dict(row))
                    
        values.append(new_label)
        current_label = new_label

    table[column_name] = values
    LOGGER.info("Labels computed. %d out of %d rows got new label computed", new_labels_count, len(values))

 
NOT_MATCHING                      = "Not matching, SKIPPING"
SET_NEW_LABEL                     = "Matching, SETTING new label"
IGNORE_ALREADY_HAD_LABEL          = "Matching, but NOT SETTING new label because already had one"
REPLACE_BY_NEW_LABEL              = "Mathing  and REPLACING existing label by new one"
CONDITION_CHECK_FAILED            = "Condition evaluation FAILED, skipping"
SKIP_ANOTHER_RULE_ALREADY_APPLIED = "Matching, but SKIPPING because another rule already matched"
OVERRIDE_PREVIOUS_RULE            = "Matching  and REPLACING label from previous matched rule"
FAIL_ANOTHER_RULE_ALREADY_APPLIED = "Matching, and FAILING, some previous rule already applied the label, this would be another."

def compute_resolution(rule, rewrite_strategy, allow_override, row, original_label, current_label):
    try:
        matching = matches_condition(rule.condition, row)
        already_had_label = bool(original_label)
        already_has_label = bool(current_label)

        # is it matching?
        if not matching:
            return NOT_MATCHING
        
        # it's matching, does it already HAD label?
        if already_had_label:
            # it had label, can we override it?
            if allow_override:
                # we can override, but didn't another rule already do it?
                return check_current_label(rule, rewrite_strategy, allow_override, row, already_has_label, REPLACE_BY_NEW_LABEL)
            else:
                # override is denined
                return IGNORE_ALREADY_HAD_LABEL
        else:
            # it doesn't had label yet, we can add one, but didn't another rule already do it?
            return check_current_label(rule, rewrite_strategy, allow_override, row, already_has_label, SET_NEW_LABEL)

    except Exception as ex:
        LOGGER.error("Fail:     cannot indentify whether it's allowed to set label or not: %s", ex)
        return CONDITION_CHECK_FAILED

def check_current_label(rule, rewrite_strategy, allow_override, row, already_has_label, resolution_if_ok):
    # did some of the previous rules compute the label?
    if not already_has_label: 
        return resolution_if_ok

    # it already has a label, should we keep the current one?
    if rewrite_strategy == "first":
         return SKIP_ANOTHER_RULE_ALREADY_APPLIED

    # or should we override it by this one?
    if rewrite_strategy == "last":
         return OVERRIDE_PREVIOUS_RULE

    # or should we use none of this and just report failure?
    if rewrite_strategy == "fail":
         #LOGGER.debug("Fail:    row matches rule conditions, has already label and the rewrite is set to fail");
         return FAIL_ANOTHER_RULE_ALREADY_APPLIED
#         raise ValueError("The row already has a label added by some of the previous rules.");

    raise ValueError("Uknown rewrite_strategy: " + rewrite_strategy)
    

def matches_condition(condition, row):
    try:
        if condition.column not in row:
            raise ValueError(f"The row doesn't have {condition.column} column") 
        column_value = row[condition.column]
    
        return matches(column_value, condition.operator, condition.value)
    except Exception as ex:
        LOGGER.error("Rule condition check of row failed: %s", ex)
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


def run(infile, rules_file, column_name, allow_override, rewrite_strategy, dry_run, outfile):
    rules = load_rules(rules_file)
    table = load_table(infile)

    check_and_apply(rules, table, column_name, allow_override, rewrite_strategy)

    if not dry_run:
        save_table(table, outfile)
