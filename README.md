# Interview BMW


## My Chosen Approach for the Interview

Two options

1. Traditional technical interview preparation
2. What gives the best picture of my profile
    * Story with Lyft and William

I decided to take option 2, because
1. This time, I have very little time to prepare
2. Too ambitious work at AID, toughest timelines I ever hard -> take my work home
    * A bit of CS problem solving prep: https://auth.geeksforgeeks.org/user/Jad%20Nohra/practice/
    * Big O 
        * Versus notes on asymptotic notation in GK
        * Database of integer sequences (know from 'The Cauchy-Schwarz Masterclass')
3. There are way too many topics that would need de-rusting
    * example: smart pointers were a topic 8 years ago (see date)
    * https://gitlab.com/jadnohra/jad-pre-2015-dabblings/blob/master/Labs/Bigeye/src/BE/smart_ptr.h
4. Option 2 worked at AID, partially due to the offline tech task
    1. Fits my 'French system' historical way of working
    2. But I am now working on improving this
        * Take chances at work for live deep thinking & collaboration
    3. AID offline tech task (this is OK because it has been leaked, and we are changing it)
        * https://gitlab.com/jadnohra/test_AID
        * TODO: notes, and other preps

Note: Option 1 works great with profiles and personalities such as Jacobo

__I take the responsibility upon myself to spend interview time taking my approach__. In the worst case it will be deemed a no-pass, but that's life.


## Problem Solving Approach

1. I have too many topics that I care about
2. In the past, I had the luxury to focus one at a time, since some year, I cannot afford this anymore
3. Stack keeps growing bigger
4. Tried many techniques to mitigate this
    1. Physical notebooks
        * Show GK notes and paper
            1. https://gitlab.com/jadnohra/project_gk/blob/master/simp-hing-analyt/simp-hing-analyt.pdf
                * https://arxiv.org/pdf/1605.08221.pdf
            2. https://gitlab.com/jadnohra/project_gk/blob/master/Code/hinge_nlsq_simul.py
            3. https://gitlab.com/jadnohra/project_gk/blob/master/Code/plot_tool.py
            4. https://gitlab.com/jadnohra/project_gk/blob/master/Code/plot_tool_repo.txt
            5. Terminal: 
                 ```python hinges_py2.py -scene chain -help -fancy -wobble_body -fwd_euler -control```
        * Show MLCP
            1. Preliminary: https://www.dropbox.com/preview/LibraryLive/TheNotes/Notes%20on%20the%20Linear%20Complementarity%20Problem.pdf?role=personal
            2. Show Notebook
            3. Show Videos
                * Titan Arm: https://www.dropbox.com/home/Business/HifiSolver?preview=arm.mp4
                * Digger: https://www.dropbox.com/home/Business/HifiSolver?preview=digger.mp4
            4. Cannot show code
    2. Large single-topic latex documents
        1. show PL/QL printed book
    3. Currently: combination of physical notes, latex summaries, and gitlab project management
        1. https://gitlab.com/jadnohra/study/issues/17
        2. https://gitlab.com/jadnohra/study/issues/7
        3. https://gitlab.com/jadnohra/study/issues/13 -> https://gitlab.com/jadnohra/study/issues/15
        4. I also use this for developing all the high-level knowledge I need about SIM & L4+, but cannot show
        5. The biggest challenge is still memorization, I do not do it actively anymore, except when I really have to
            * I try to work more as a 'processing machine', I open my notes, switch context for a while, and process for results
            * The older the topic, the longer the lead time, can take from a couple of hours to a couple of weeks

## Technical tidbits

### At Havok

Figures at: https://www.dropbox.com/home/Business/Hvk/short_history?preview=short_history.pdf

1. Nintendo WiiU math library
    1. Instruction-level ARM (handicapped two-float SIMD)
    2. Buggy compiler in terms of performance optimization
    3. Very tight deadline, with failed attempts, and important business deal, on Christmas
    4. Figure 17
2. Physics-2014 contact solver perfromance
    1. Outdated expert mental models of CPUs
    2. Benchmarking ignoring real data
    3. Research (lead time) -> branch prediction as main actor in this context
    4. Proof using counter example
    5. New (intrusive) optimization : couplign geometry processing to solver using data rearrangement
    6. Also, wrote whole new contact solver, critical component in all games shipped since ~2014
        * No bugs ever reported
        * Defensive code (tunable defensiveness -> math library only has INFTY and NAN warnings)
        * Found bugs in other pieces of code, including hard to find bugs due to slow accumulation of wrong calculation
        * tunable per-platform using a very carefully configured set of macros (> 10 options -> code path combinations)
    7. Example of pyramid at Figure 12
3. Deterministic scaling of cores (Intel many-core CPU R&D)
4. Network physics R&D
    1. Research report and proposed designs
    2. Prototype
5. Guerrila Games
    1. AI environment-aware physical behavior: https://www.youtube.com/watch?v=_mXYAPUIAqg
    2. Automatic region generation
        1. Porting of recast 'ugly and cryptic' code
            * Improvements of corner cases that other companies presented as challenges during GDC
        2. Research sekeltonization algorithms
        3. Choose and implement
        4. Modify to fit our application (stray edges): http://scikit-image.org/docs/0.7.0/auto_examples/plot_medial_transform.html
    3. Vehicle AI



TODO
Youtube videos


Appendix

References
https://gitlab.com/jadnohra/test_AID
 https://auth.geeksforgeeks.org/user/Jad%20Nohra/practice/
More notes
https://www.dropbox.com/home/LibraryLive/TheNotes2
https://www.dropbox.com/home/LibraryLive/TheNotes2?preview=pointillistic.pdf
TODO notes of interest
https://www.dropbox.com/home/LibraryLive/TheNotes
TODO notes of interest

OTHER
https://gitlab.com/jadnohra/BlackRiceLabs/blob/master/VehicleTest/RandomizedFlowFieldPlanner2.h
https://gitlab.com/jadnohra/BlackRiceLabs/blob/master/VehicleTest/RandomizedFlowFieldPlanner.h
https://gitlab.com/jadnohra/jad-pre-2015-dabblings/blob/master/Lab2015/mlcp2.0/lp_jad.jl
https://gitlab.com/jadnohra/jad-pre-2015-dabblings/blob/master/Lab2015/asinus_salutem/scripts/gk_notes_p45.txt
https://gitlab.com/jadnohra/jad-pre-2015-dabblings/blob/master/Lab2015/asinus_salutem/scripts/test_df.txt
https://gitlab.com/jadnohra/jad-pre-2015-dabblings/tree/master/Labs/Numerical/nics
https://gitlab.com/jadnohra/jad-pre-2015-dabblings/blob/master/Labs/Bigeye/src/BE/smart_ptr.h
https://gitlab.com/jadnohra/jad-pre-2015-dabblings/tree/master/Labs/Bigeye/src/BE
https://www.youtube.com/watch?v=SEntMI6s6RQ&t=0s&list=PL753A83C4444A2486&index=2

https://www.youtube.com/watch?v=lDNY4-mupf0&list=PL5ED86276C6DB1347&t=0s&index=2
https://www.youtube.com/watch?v=zBxg_Mp3md0&list=PL5ED86276C6DB1347&index=2
https://github.com/jadnohra/World-Of-Football



