from time import sleep
from pysm.pysm import State, StateMachine, Event


def initialize(state, event):
    print(f"Now I'm in state {executor.leaf_state.name}")
    print("initializing...")

def wait_connection(state, event):
    print(f"Now I'm in state {executor.leaf_state.name}")
    print("waiting connection...")
    sleep(1)
    print("... connected")
    executor.dispatch(Event("connected"))

def abort(state, event):
    print(f"Now I'm in state {executor.leaf_state.name}")
    print("Aborting...")

def reset(state, event):
    print(f"Now I'm in state {executor.leaf_state.name}")
    print("resetting...")

def _run_action_sim(state, event):
    print(f"Now I'm in state {executor.leaf_state.name}")
    print(f"I'm in state {state.parent.name}")
    print(f"I'm in leaf state {state.name}")
    print(f"I was told to: {event.name}")
    print(f"with input: {event.input}")
    print(f"and using these data: {event.cargo}")

def write_digital(state, event: Event):
    _run_action_sim(state, event)
    executor.dispatch(Event("action_finished"))

def write_analogue(state, event: Event):
    _run_action_sim(state, event)
    executor.dispatch(Event("action_finished"))

def set_nr_reps(state, event: Event):
    _run_action_sim(state, event)
    executor.dispatch(Event("action_finished"))

def set_rep_duration(state, event: Event):
    _run_action_sim(state, event)
    executor.dispatch(Event("action_finished"))

def set_digital_table(state, event: Event):
    _run_action_sim(state, event)
    executor.dispatch(Event("action_finished"))

def set_analogues_table(state, event: Event):
    _run_action_sim(state, event)
    executor.dispatch(Event("action_finished"))

def run_experiment(state, event: Event):
    _run_action_sim(state, event)
    executor.dispatch(Event("action_finished"))

def run_sequence(state, event: Event):
    _run_action_sim(state, event)
    executor.dispatch(Event("action_finished"))


# Main state machine
executor = StateMachine("executor")

# main states of the state machine
off = State("off")
on = StateMachine("on")

waiting_connection = State("waiting_connection")
aborted = State("aborted")
idle = State("idle")
active = StateMachine("active")

trigger_action = State("trigger_action")
writing_digital = State("writing_digital")
writing_analogue = State("writing_analogue")
setting_nr_reps = State("setting_nr_reps")
setting_rep_duration = State("setting_rep_duration")
setting_digital_table = State("setting_digital_table")
setting_analogues_table = State("setting_analogues_table")
running_experiment = State("running_experiment")
running_sequence = State("running_sequence")

active.add_states(trigger_action,
                  writing_digital,
                  writing_analogue,
                  setting_nr_reps,
                  setting_rep_duration,
                  setting_digital_table,
                  setting_analogues_table,
                  running_experiment,
                  running_sequence)
active.set_initial_state(trigger_action)

on.add_states(waiting_connection,
              aborted,
              idle,
              active)
on.set_initial_state(waiting_connection)

executor.add_states(on, off)
executor.set_initial_state(off)

# Add transitions
on.add_transition(waiting_connection, aborted,
                  events=["connected"], action=abort)
on.add_transition(aborted, idle,
                  events=["abort_condition_released"])
on.add_transition(active, idle,
                  events=["action_finished"])
on.add_transition(idle, writing_digital,
                  events=["run_action"], input=["write_digital"], after=write_digital)
on.add_transition(idle, writing_analogue,
                  events=["run_action"], input=["write_analogue"], after=write_analogue)
on.add_transition(idle, setting_nr_reps,
                  events=["run_action"], input=["set_nr_reps"], after=set_nr_reps)
on.add_transition(idle, setting_rep_duration,
                  events=["run_action"], input=["set_rep_duration"], after=set_rep_duration)
on.add_transition(idle, setting_digital_table,
                  events=["run_action"], input=["set_digital_table"], after=set_digital_table)
on.add_transition(idle, setting_analogues_table,
                  events=["run_action"], input=["set_analogues_table"], after=set_analogues_table)
on.add_transition(idle, running_experiment,
                  events=["run_action"], input=["run_experiment"], after=run_experiment)
on.add_transition(idle, running_sequence,
                  events=["run_action"], input=["run_sequence"], after=run_sequence)

executor.add_transition(off, on,
                        events=["initialize"], action=initialize, after=wait_connection)
executor.add_transition(on, off,
                        events=["reset", "turn_off"], after=initialize)

# Add handlers
# on.handlers = {"enter": wait_connection}


if __name__ == "__main__":
    executor.initialize()
    assert executor.state.name == "off"
    executor.dispatch(Event("initialize"))
    assert executor.root_machine.name == "executor"
    assert executor.state.name == "on"
    assert executor.leaf_state.name == "aborted"
    print("... abort condition released")
    executor.dispatch(Event("abort_condition_released"))
    assert executor.root_machine.name == "executor"
    assert executor.state.name == "on"
    assert executor.leaf_state.name == "idle"
    executor.dispatch(Event("run_action", input="write_digital", digitals=42))
    assert executor.root_machine.name == "executor"
    assert executor.state.name == "on"
    assert executor.leaf_state.name == "idle"

