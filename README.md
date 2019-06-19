# trial-list-generator
Python script to create a pseudo-randomly ordered list of trials

The script generate_trials_lists creates pseudo-randomly ordered lists of experiment trials. 

The paramater `participants` controls the number of trial files.
In `make_files()`, two parameters control the structure of the trial files: `num_trials` determines the number of trials in each file; `max_shared_const` sets the maximum number of constituents that can be shared between consecutive trials.
