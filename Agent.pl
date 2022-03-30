/*
working_directory(CWD, 'D:/OneDrive - Nanyang Technological University/AY2S2/CZ3005 ArtificialIntelligence/Lab2').
consult('Agent.pl').
reconsult('Agent.pl').
*/

%use asserta to add to beginning and retract to remove
:-dynamic
    current/3,
    visited/2,
    wumpus/2,
    confoundus/2,
    tingle/2,
    glitter/2,
    stench/2,
    safe/2,
    hasarrow/0.

reborn():-
    retractall(current(_, _, _)),
    retractall(visited(_, _)),
    retractall(wumpus(_, _)),
    retractall(confoundus(_, _)),
    retractall(tingle(_, _)),
    retractall(glitter(_, _)),
    retractall(stench(_, _)),
    retractall(safe(_, _)).
    retractall(hasarrow(_, _)),

reposition():- 
    retractall(current(_, _, _)),
    retractall(visited(_, _)),
    retractall(confoundus(_, _)),
    retractall(tingle(_, _)),
    retractall(glitter(_, _)),
    retractall(stench(_, _)),
    retractall(safe(_, _)),

    asserta(current(0,0,rnorth)),
    asserta(confoundus(0,0)).


%move(A, L):-


%explore(L):-







