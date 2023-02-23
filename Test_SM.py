from pysm.pysm import State, StateMachine


executor = StateMachine("executor")
starting = State("starting")
executor.add_state("starting", initial=True)

initialising = State("initialising")
executor.add_state("initializing")

resetting = State("resetting")
executor.add_state("resetting")

off = State("off")
executor.add_state("off")


on = StateMachine("on")
waiting_connection = State("waiting_connection")
on.add_state("waiting_connection", initial=True)

sending_configuration = State("sending_configuration")
on.add_state("sending_configuration")

aborted = State("aborted")
on.add_state("aborted")

idle = State("idle")
on.add_state("idle")

executor.add_state("on")


running_action = StateMachine("running_action")
writing_digital = State("writing_digital")
running_action.add_state("writing_digital")

writing_analogue = State("writing_analogue")
running_action.add_state("writing_analogue")

setting_nr_reps = State("setting_nr_reps")
running_action.add_state("setting_nr_reps")

setting_rep_duration = State("setting_rep_duration")
running_action.add_state("setting_rep_duration")

setting_digital_table = State("setting_digital_table")
running_action.add_state("setting_digital_table")

setting_analogues_table = State("setting_analogues_table")
running_action.add_state("setting_analogues_table")

running_experiment = State("running_experiment")
running_action.add_state("running_experiment")

running_sequence = State("running_sequence")
running_action.add_state("running_sequence")

executor.add_state("running_action")



