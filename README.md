Finite-state machine Builder
============================
Program helps to create algorithm and then generate VHDL code for it.

Main features
-------------
  - algorithm editing and validation
  - chart visualization
  - algorithm analyze
  - Mealy graph of state machine
  - trigger and signal functions minimisation
  - generation of VHDL code
  
Algorithm editor
----------------
Use toolbar or ``Shif+key`` hotkeys to change algorithm.
  - ``Shift+arrows`` for navigation
  - ``Shift+x`` add condition block next to the cursor
  - ``Sift+y`` add operation block next to the cursor
  - ``Sift+backspace`` delete block under cursor

![algorithm](screenshots/alg.png "Editing the algorithm")

Flowchart visualization
-----------------------
Next tab has flowchart of entered algorithm.

![chart](screenshots/chart.png "Flowchart of the algorithm")

Tables
------
*Table* tab include two tables:
  - connections table (2 means connection by ``false``)
  - definitions table

![tables](screenshots/tables.png "Tables")

Algorithm analysis
------------------
*Analysis* tab contains all paths and loops.

![paths](screenshots/paths.png "Paths and loops")

Graph
-----
Next tab has Mealy graph of generated finite-state machine.
Dashed nodes - additional ones for neighboring coding.

![graph](screenshots/graph.png "Mealy graph")

Transition table and functions
------------------------------
Last tab contains complete transition table and both origin and minimized functions of output signals and triggers.
![funcs and transition table](screenshots/funcs.png "Transition table and functions")

VHDL code generation
--------------------
Use ``File->Export VHDL`` to get code of your finite-state machine.

Program generates all minimized signal and trigger functions.
