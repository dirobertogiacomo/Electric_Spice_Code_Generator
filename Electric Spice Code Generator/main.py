import functions

# Input logic function and variables
logic_function = "((NOT S1) AND A) OR (S1  AND (NOT A))"
input_variables = ["A", "S1"]
output_variable = 'nS1'

functions.print_everything(logic_function, input_variables, output_variable)