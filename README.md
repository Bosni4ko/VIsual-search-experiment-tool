This repository contains a Python-based application for designing, launching, and managing experiments that explore how emotional stimuli (e.g. positive or negative images) affect attention and visual search performance.
Developed as part of a master's thesis.

**Visual Search Experiments**: Supports configurable grid-based tasks with emotional distractors and targets.
**Experimental Conditions**: Easy creation of experiments with three types of valence stimulus:
  -Positive
  -Negative
  -Neutral
**Session Management**:
  - Participant info entry and session tracking
  - Save data in structured JSON and CSV formats. IMportant data includes reaction time, target presence, participant metadata, number of stimulus, stimulus images position and names.
**Multilingual UI**
  -Build-in UI which supports two languages: English and Latvian

Directory has the following structure:
├── Main.py # Entry point to the application
├── launch_screen.py # Screen for launching experiments
├── experiment_session_start.py # Screen for starting experiment sessions
├── running_session_screen.py # Main experiment runner logic
├── editor_screen.py # Experiment editor
├── stimulus_editor.py # Stimulus selection and configuration
├── text_editor.py # Formatted instruction text components
├── grid.py # Grid rendering logic for visual tasks
├── palette.py # Component palette for timeline editor
├── translations.py # Multilingual text support
├── /experiments/ # Default folder for saving experiment designs
├── /images/ # Default folder with categorized emotional image datasets
├── /session_saves/ # Default folder for saved experiment sessions
├── create_screen_state.json # Saved state of metadata for experiment setup
├── experiment_state.json # Saved state of experiment timeline and logic
├── README.md # Project overview
├── License.txt # Image dataset distribution license
├── TEXT_AND_TAGS.py # Default text and tags for textual components
└── styles.py # UI design
