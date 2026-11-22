# Define the possible operations
operations = {
    "Simple Cell Lookup": ["<init>", "select_row","select_column", "<END>"],
    "Unknown":["<init>","select_column", "select_row", "<END>"],
    "Filter + Lookup (WHERE Condition)": ["<init>","select_column", "select_row", "<END>"],
    "Aggregation (COUNT)": ["<init>","select_row","select_column",  "<END>"],
    "Superlative / Argmax": ["<init>","select_row","select_column",  "<END>"],
    "Comparison Between Two Companies": ["<init>","select_row", "select_column", "<END>"],
    "Arithmetic Operations over Table Cells": ["<init>","select_column", "select_row", "<END>"],
    "Multi-Step and Compositional WikiTQ-Style Questions": ["<init>","select_column", "select_row", "<END>"]

}


# Main function to get the next operation
def DQTR(last_operation, question_type):


    # Get the sequence of operations for the given question type
    question_operations = operations.get(question_type)

    if not question_operations:
        raise ValueError(f"Unknown question type: {question_type}")

    # Find the index of the last operation in the sequence
    try:
        last_operation_index = question_operations.index(last_operation)
    except ValueError:
        raise ValueError(f"Unknown last operation: {last_operation}")

    # Get the next operation in the sequence
    Q=last_operation_index + 1
    if Q < len(question_operations):

        next_operation = question_operations[last_operation_index + 1]
        current_operation = question_operations[last_operation_index]
        return next_operation
    else:
        print("<END>")  # End of operation sequence
        return "<END>"
