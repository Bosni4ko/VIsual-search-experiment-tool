This repository contains a Python-based application for designing, launching, and managing experiments that explore how emotional stimuli (e.g. positive or negative images) affect attention and visual search performance.
Developed as part of a master's thesis.

**Visual Search Experiments**: Supports configurable grid-based tasks with emotional distractors and targets.
**Experimental Conditions**: Easy creation of experiments with three types of valence stimulus: <br>
  -Positive <br>
  -Negative <br>
  -Neutral <br>
  
**Session Management**: <br>
  - Participant info entry and session tracking <br>
  - Save data in structured JSON and CSV formats. IMportant data includes reaction time, target presence, participant metadata, number of stimulus, stimulus images position and names. <br>
  
**Multilingual UI** <br>
  -Build-in UI which supports two languages: English and Latvian <br>

Directory has the following structure: <br>
├── Main.py # Entry point to the application <br>
├── launch_screen.py # Screen for launching experiments <br>
├── experiment_session_start.py # Screen for starting experiment sessions <br>
├── running_session_screen.py # Main experiment runner logic <br>
├── editor_screen.py # Experiment editor <br>
├── stimulus_editor.py # Stimulus selection and configuration <br>
├── text_editor.py # Formatted instruction text components <br>
├── grid.py # Grid rendering logic for visual tasks <br>
├── palette.py # Component palette for timeline editor <br>
├── translations.py # Multilingual text support <br>
├── /experiments/ # Default folder for saving experiment designs <br>
├── /images/ # Default folder with categorized emotional image datasets <br>
├── /session_saves/ # Default folder for saved experiment sessions <br>
├── create_screen_state.json # Saved state of metadata for experiment setup <br>
├── experiment_state.json # Saved state of experiment timeline and logic <br>
├── README.md # Project overview <br>
├── License.txt # Image dataset distribution license <br>
├── TEXT_AND_TAGS.py # Default text and tags for textual components <br>
└── styles.py # UI design
