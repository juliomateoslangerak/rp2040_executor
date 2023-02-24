from time import sleep

from pysm.pysm import State, StateMachine, Event


def initialize(state, event):
    print("initializing...")


def wait_connection(state, event):
    print("waiting connection...")
    sleep(3)
    print("... connected")
    executor.dispatch(Event("connected"))


def abort(state, event):
    print("Aborting...")
    sleep(1)
    print("... abort condition released")
    executor.dispatch(Event("abort_condition_released"))


def reset(state, event):
    print("resetting...")


# Main state machine
executor = StateMachine("executor")

# main states of the state machine
off = State("off")
on = StateMachine("on")

waiting_connection = State("waiting_connection")
aborted = State("aborted")
idle = State("idle")
active = StateMachine("active")

choosing_action = State("choosing_action")
writing_digital = State("writing_digital")
writing_analogue = State("writing_analogue")
setting_nr_reps = State("setting_nr_reps")
setting_rep_duration = State("setting_rep_duration")
setting_digital_table = State("setting_digital_table")
setting_analogues_table = State("setting_analogues_table")
running_experiment = State("running_experiment")
running_sequence = State("running_sequence")

active.add_states(choosing_action,
                  writing_digital,
                  writing_analogue,
                  setting_nr_reps,
                  setting_rep_duration,
                  setting_digital_table,
                  setting_analogues_table,
                  running_experiment,
                  running_sequence)
active.set_initial_state(choosing_action)

on.add_states(waiting_connection,
              aborted,
              idle,
              active)
on.set_initial_state(waiting_connection)

executor.add_states(on, off)
executor.set_initial_state(off)

# Add transitions
executor.add_transition(off, on,
                        events=["initialize"], after=wait_connection)
executor.add_transition(on, off,
                        events=["reset", "turn_off"], after=initialize)
on.add_transition(waiting_connection, aborted,
                  events={"connected"}, after=abort)
on.add_transition(aborted, idle,
                  events=["abort_condition_released"])
on.add_transition(active, idle,
                  events=["action_finished"])

# Add handlers
on.handlers = {"enter": initialize}


if __name__ == "__main__":
    executor.initialize()
    assert executor.state.name == "off"
    executor.dispatch(Event("initialize"))
    assert executor.root_machine.name == "executor"
    assert executor.state.name == "on"
    assert executor.leaf_state.name == "idle"
