from pysm.pysm import State, StateMachine

starting = State("starting")
initialising = State("initialising")
resetting = State("resetting")
off = State("off")

on = StateMachine("on")
waiting_connection = State("waiting_connection")
sending_connection = State("sending_connection")
aborted = State("aborted")
idle = State("idle")

running_action = StateMachine("running_action")
writing_digital = State("writing_digital")
writing_analogue = State("writing_analogue")
setting_nr_reps = State("setting_nr_reps")
setting_rep_duration = State("setting_rep_duration")
setting_digital_table = State("setting_digital_table")
setting_analogues_table = State("setting_analogues_table")
running_experiment = State("running_experiment")
running_sequence = State("running_sequence")




