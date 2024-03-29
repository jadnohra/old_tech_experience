# Table of Contents 

- [0. Currently](#0-currently)
- [1. At Havok](#1-at-havok)
  * [a. Nintendo WiiU math library](#a-nintendo-wiiu-math-library)
  * [b. Physics contact solver perfromance](#b-physics-2014-contact-solver-perfromance)
  * [c. Network physics R&D](#c-network-physics-r-d)
  * [d. Job queue combinatorial delay mode](#d-job-queue-combinatorial-delay-mode)
  * [e. Geometry numerical issues](#e-geometry-numerical-issues)
  * [f. TOI Argument](#f-toi-argument)
  * [g. High fidelity solver](#g-hkds)
  * [h. Misc.](#h-misc)
- [2. At Microsoft](#2-at-microsoft)
- [3. At Guerrila Games](#3-at-guerrila-games)
- [4. Before that](#4-before-that)
- [5. Problem Solving Approach](#5-problem-solving-approach)
- [6. Miscellaneous](#6-miscellaneous)

---
# 0. Currently

 * [CV](./cv/CV_Jad-Nohra_2021-03-05.pdf)
   - https://github.com/jadnohra/daisy, a traffic simulator
   - https://github.com/jadnohra/PaCoS, a concurrency determinism simulator 
   - https://github.com/jadnohra/hinges_py, a rigid-body-dynamics simulator
   - https://github.com/jadnohra/trace, a real-time data plotting tool
   - https://github.com/jadnohra/tag_export
   - https://github.com/jadnohra/TheNotes
 * Scenario language
 * Map search
 * Scenario augmenter design
 * Test validation concept

# 1. At Havok

## a. Nintendo WiiU math library

1. Instruction-level ARM (handicapped two-float SIMD)
2. Buggy compiler in terms of performance optimization
    * <img src="wiiu/wiiu_2.png" width="320"/> <img src="wiiu/wiiu_1.png" width="320"/>

## b. Physics-2014 contact solver perfromance

1. Mental models of CPUs at race with CPU improvements
    * Benchmarking ignoring real data becomes dangerous
3. Research (https://www.agner.org/optimize/#manuals) -> branch prediction as main actor in this context
4. Proof using counter example :  <img src="netw/pyramid_split.png" width="240"/>
5. New (intrusive) optimization : coupling geometry processing to solver using data rearrangement
6. Also, wrote whole new contact solver, critical component in all games shipped since ~2014
    * To get an idea [Bullet solver](https://github.com/bulletphysics/bullet3/blob/cdd56e46411527772711da5357c856a90ad9ea67/src/BulletDynamics/ConstraintSolver/btSequentialImpulseConstraintSolverMt.cpp)
    * Havok's focus: performance
    * No bugs ever reported
    * Defensive code (tunable defensiveness -> math library only has INFTY and NAN warnings)
    * Found bugs in other pieces of code, including hard to find bugs due to slow accumulation of wrong calculation
    * tunable per-platform using a very carefully configured set of macros (> 10 options -> code path combinations)


3. Deterministic scaling of cores (Intel many-core CPU R&D)
    * <img src="hvk_other/sched.png" width="320"/>

## c. Network physics R&D

1. [Research report](netw/csarch1.pdf) and proposed designs
    * <img src="netw/csarch1_screen2.png" width="320"/> <img src="netw/csarch1_screen1.png" width="320"/>
2. Prototype
    * <img src="netw/viewer5.jpeg" width="320"/> <img src="netw/pyramid_split.png" width="320"/>
    * <img src="netw/viewer6.jpeg" width="320"/> <img src="netw/sectors2.jpeg" width="320"/>
3. Including low-level framework
    * <img src="netw/launcher.jpg" width="320"/>

## d. Job queue combinatorial delay mode

* 1/100000 repro -> found in an hour

## e. Geometry numerical issues

* [Jira epsilon](geom_num/JiraEpsilon.pdf)
    * <img src="geom_num/JiraEpsilon_screen1.png" width="320"/>     
* Ray sphere: improvement by intuitive solution
    * <img src="geom_num/RaySphere.png" width="320"/>
* Ray triangle
    * Improvement by analytical solution
        * Books like 'Floating-Point Computation (Strebenz)', resources like '???'
    * Telescoping debugger
    * <img src="geom_num/00-10km_NoToleranceAlgo_CurrAlgo.jpg" width="240"/> <img src="geom_num/04-10km_ZeroToleranceAlgo_CurrAlgo.jpg" width="240"/> 
    * <img src="geom_num/01-30km_NaiveTolerranceAlgo.jpg" width="240"/>	<img src="geom_num/02-30km_ThickEdgeAlgo.jpg" width="240"/>		
    * <img src="geom_num/03-30km_ZoomIn_ThickEdgeAlgo.jpg" width="240"/> <img src="geom_num/05-10km_ZoomIn_ThickEdge.jpg" width="240"/>
    * <img src="geom_num/rt1.jpeg" width="240"/>
* Led to interest about numerical analysis (Studying, etc.)
    * [Sampler prototype (RRT)](https://gitlab.com/jadnohra/jad-pre-2015-dabblings/tree/master/Labs/Numerical/nics)
        * <img src="geom_num/nics_rnn.png" width="320"/> <img src="geom_num/nics_fp754.png" width="320"/> 
    * Interval math library with pessimistic approximate but fast bounds (2x slower than normal arithmetic)
    * Also first steps into numerical analysis for dynamics : [Residuals](hvk_other/respart1.pdf)
        * <img src="hvk_other/respart1_screen.png" width="320"/> 

## f. TOI Argument

* Open problem ever since the 'TOI' engine was abandoned
* Multiple attempts that replaced artifacts with other artifacts
* Proved that the problem is not solvable: [TOI argument](hvk_other/toiarg1.pdf)
    * <img src="hvk_other/toiarg1_screen.png" width="320"/>
* Effect: stop searching for the solution, focus on which artifacts to trade and when

## g. HKDS

* Overview : [HKDS overview](hkds/ds_overview1.pdf)
    * <img src="hkds/overview_screen1.png" width="320"/> <img src="hkds/overview_screen2.png" width="320"/>
* A high level view of the approaches
    * <img src="hkds/ds_simple.png" width="480"/>  
* [More detail](hkds/ds_detail.pdf)
    * <img src="hkds/detail_screen1.png" width="640"/>
* Fast forward: videos of results
    * [Titan arm video](hkds/HifiSolverVid/arm.mp4)
        * <img src="hkds/hkds_titan.png" width="320"/> 
    * [Digger video](hkds/HifiSolverVid/digger.mp4)
        * <img src="hkds/hkds_digger1.png" width="320"/> <img src="hkds/hkds_digger2.png" width="320"/>
* Prerequisites that allowed to even start tackling this
    * [Rotations and Basics](hvk_other/TheMathematicsOfHavoksSolver.pdf)
         * <img src="hvk_other/rot_screen1.png" width="320"/>  <img src="hvk_other/rot_screen2.png" width="320"/> 
         * <img src="hvk_other/hms_varnames.png" width="320"/> 
    * Work on stabilizing certain constraints
    * Notebook notes on 'universal constraint'
    * Substepping algorithm [Report]((hvk_other/substep1.pdf))
        * A stumbling block for others at multiple occasions
        * Local problem: <img src="hvk_other/substep_local.png" width="320"/> 
        * Approximations: <img src="hvk_other/substep_approx.png" width="320"/> 
        * Algorithm: <img src="hvk_other/substep_algo.png" width="280"/> 
* MLCP: Notebook 'MLCP'
* Some code
    * Prototyping using Julia : [Gitlab]( https://gitlab.com/jadnohra/jad-pre-2015-dabblings/blob/master/Lab2015/mlcp2.0/lp_jad.jl)
        *  <img src="hkds/mlcp_chuzro.png" width="320"/> <img src="hkds/mlcp_refs.png" width="320"/>   
    * MLCP->LCP (error in paper) <img src="hkds/mlcp_conv.png" width="320"/> 
    * Co-simulation <img src="hkds/mlcp_cosim.png" width="320"/> 
* Dynamics debugging tool: <img src="hkds/mlcp_trace.png" width="320"/> 
    * Terminal ```python trace.py -test```  
    * [Trace user manual](https://github.com/jadnohra/trace)

## h. Misc.

* <img src="hvk_other/sampler2.PNG" height="220"/>
* <img src="hvk_other/sampler1.PNG" width="320"/> <img src="hvk_other/sampler3.PNG" width="320"/>

# 2. At Microsoft
* <img src="tracking/SFR_VisualPlace_2.JPG" height="320"/>
* <img src="tracking/bendphys2.JPG" width="320"/> 
* <img src="mapping/phys_play.jpg" width="320"/> <img src="mapping/pruning_occup.jpg" width="320"/>

# 3. At Guerrila Games

1. AI environment-aware physical behavior: [Video](https://www.youtube.com/watch?v=_mXYAPUIAqg)
    * <img src="GG/jetpack.png" width="320"/> <img src="GG/owl.png" width="320"/>
2. Automatic region generation
    1. Porting of recast 'ugly and cryptic' code
        * Improvements of corner cases that other companies presented as challenges during GDC
        * <img src="GG/recast.png" width="320"/>
    2. Research sekeltonization algorithms
    3. Choose and implement
        * <img src="GG/areas.png" width="320"/>
    4. Modify to fit our application (stray edges)
        * [<img src="GG/scikit_skel.png" width="320"/>](http://scikit-image.org/docs/0.7.0/auto_examples/plot_medial_transform.html)
3. Vehicle AI : [Video](https://www.youtube.com/watch?v=QjmRA2Obu9I)
    * <img src="GG/vehicle.png" width="320"/>
    * Prototyping [VehicleTest on gitlab](https://gitlab.com/jadnohra/BlackRiceLabs/blob/master/VehicleTest)
    * <img src="GG/vehic_planner1.png" height="320"/> <img src="GG/vehic_planner2.png" height="320"/> 
    * <img src="GG/vehic_planner3.png" width="320"/> 
4. SPU + PS3 multithreading/DMA tricky bug chasing

# 4. Before that
1. World of Football
    * [On github](https://github.com/jadnohra/World-Of-Football)
        * <img src="old/wof_teaser.png" width="320"/>  <img src="old/wof_play.png" width="320"/> 
    * [Youtube videos](https://www.youtube.com/watch?v=lDNY4-mupf0&list=PL5ED86276C6DB1347&t=0s&index=2)
        * <img src="old/wof_coll.png" width="320"/> 
    * [Youtube videos](https://www.youtube.com/watch?v=zBxg_Mp3md0&list=PL5ED86276C6DB1347&index=2)
2. Mocap loader, skelton semantics, footplant detection, UI framework
    * [Bigfoot video](https://www.youtube.com/watch?v=SEntMI6s6RQ&t=0s&list=PL753A83C4444A2486&index=2)
        * <img src="old/bigfoot_1.png" height="240"/> <img src="old/bigfoot_2.png" height="240"/> 
    * [Bigeye on gitlab](https://gitlab.com/jadnohra/jad-pre-2015-dabblings/tree/master/Labs/Bigeye/src/BE)
        * <img src="old/bigeye_1.png" width="320"/>
    * example: smart pointers 10 years ago
        * <img src="old/smart_ptr_1.png" height="240"/> <img src="old/smart_ptr_2.png" height="240"/>     


# 5. Problem Solving Approach

1. I have too many topics that I care about
2. In the past, I had the luxury to focus one at a time, since some years, I cannot afford this anymore
3. Stack keeps growing bigger
4. Tried many techniques to mitigate this
    1. Physical notebooks
        * Show GK notes and paper
            1. https://gitlab.com/jadnohra/project_gk/blob/master/simp-hing-analyt/simp-hing-analyt.pdf
                * [public arxiv.org version: 'Uniqueness of Minima of a Certain Least Squares Problem'](https://arxiv.org/pdf/1605.08221.pdf)
                * <img src="uniq_lsq/screen_1.png" width="320"/> 
                * <img src="uniq_lsq/screen_2.png" width="320"/> <img src="uniq_lsq/screen_3.png" width="320"/> 
            2. https://gitlab.com/jadnohra/project_gk/blob/master/Code/hinge_nlsq_simul.py
            3. https://gitlab.com/jadnohra/project_gk/blob/master/Code/plot_tool.py
            4. https://gitlab.com/jadnohra/project_gk/blob/master/Code/plot_tool_repo.txt
            5. https://gitlab.com/jadnohra/jad-pre-2015-dabblings/blob/master/Lab2015/asinus_salutem/scripts/gk_notes_p45.txt
            6. https://gitlab.com/jadnohra/jad-pre-2015-dabblings/blob/master/Lab2015/asinus_salutem/scripts/test_df.txt
            7. Terminal: 
                 ```python hinges_py2.py -scene chain -help -fancy -wobble_body -fwd_euler -control```
    2. Large single-topic latex documents
        1. show PL/QL printed book
    3. Currently: combination of physical notes, latex summaries, and gitlab project management
        1. https://gitlab.com/jadnohra/study/issues/17
        2. https://gitlab.com/jadnohra/study/issues/7
        3. https://gitlab.com/jadnohra/study/issues/13 -> https://gitlab.com/jadnohra/study/issues/15
        4. I also use this for developing all the high-level knowledge I need about SIM & L4+
        5. The biggest challenge is still memorization, I do not do it actively anymore, except when I really have to
            * I try to work more as a 'processing machine', I open my notes, switch context for a while, and process for results
            * The older the topic, the longer the lead time, can take from a couple of hours to a couple of weeks

# 6. Miscellaneous

* Existing attempts
    * http://chrishecker.com/The_mixed_linear_complementarity_problem 
    * https://github.com/thomasmarsh/ODE/blob/df82c09d967d486822ea1715a09291593ba471a6/ode/src/lcp.cpp
    * Overview: http://box2d.org/files/GDC2014/ErwinCoumans_ExploringMLCPSolversAndFeatherstone.pdf 
* More notes
    * https://www.dropbox.com/home/LibraryLive/TheNotes2
    * https://www.dropbox.com/home/LibraryLive/TheNotes2?preview=pointillistic.pdf
    * https://www.dropbox.com/home/LibraryLive/TheNotes

