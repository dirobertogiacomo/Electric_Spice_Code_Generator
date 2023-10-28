import functions

# Input logic function and variables
logic_function = "(S0 AND ( ((NOT S1) AND (NOT A)) OR (S1 AND A)) )"
input_variables = ["A", "S0", "S1"]
output_variable = 'Y'

functions.print_everything(logic_function, input_variables, output_variable)