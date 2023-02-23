from pysm.pysm import State, StateMachine


executor = StateMachine("executor")
starting = State("starting")
initialising = State("initialising")
resetting = State("resetting")
off = State("off")

on = StateMachine("on")
waiting_connection = State("waiting_connection")
sending_configuration = State("sending_configuration")
aborted = State("aborted")
idle = State("idle")

on.add_states([waiting_connection,
               sending_configuration,
               aborted,
               idle])
on.set_initial_state(waiting_connection)

running_action = StateMachine("running_action")
writing_digital = State("writing_digital")
writing_analogue = State("writing_analogue")
setting_nr_reps = State("setting_nr_reps")
setting_rep_duration = State("setting_rep_duration")
setting_digital_table = State("setting_digital_table")
setting_analogues_table = State("setting_analogues_table")
running_experiment = State("running_experiment")
running_sequence = State("running_sequence")

running_action.add_states([writing_digital,
                           writing_analogue,
                           setting_nr_reps,
                           setting_rep_duration,
                           setting_digital_table,
                           setting_analogues_table,
                           running_experiment,
                           running_sequence])

executor.add_states([starting,
                     initialising,
                     resetting,
                     on,
                     off,
                     running_action])
executor.set_initial_state(starting)


def initialize(state, event):
    print("initializing...")


