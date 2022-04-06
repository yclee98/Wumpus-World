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
    agent_loc/2.
    hasarrow/0.
    wumpus_alive/0.
    agent_alive/0.
    has_gold/0.


% initialize the status of the objectives and assets of the agent
assertz(wumpus_alive)
assertz(agent_alive)
assertz(has_gold)
assertz(hasarrow)

reborn():-
    retractall(current(_, _, _)),
    retractall(visited(_, _)),
    retractall(wumpus(_, _)),
    retractall(confoundus(_, _)),
    retractall(tingle(_, _)),
    retractall(glitter(_, _)),
    retractall(stench(_, _)),
    retractall(safe(_, _)),
    retractall(hasarrow()),

    % when reborn, agent loses gold coin
    retractall(has_gold(agent)),

    % Set wumpus back alive
    assertz(wumpus_alive).

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


% L = [Confounded, Stench, Tingle, Glitter, Bump, Scream]
% 1 = on, 0 = off
move(A, [Confounded, Stench, Tingle, Glitter, Bump, Scream]):-
    update_wumpus(Stench),
    update_portal(Tingle),
    update_coin(Glitter).


update_wumpus(0):-
    current(X,Y,D),

    % if stench is not perceived, wumpus cannot be in adj rooms
    % "is" to evaluate mathematical expressions
    Y2 is Y + 1, retract(wumpus(X, Y2)),
    Y2 is Y - 1, retract(wumpus(X, Y2)),
    X2 is X + 1, retract(wumpus(X2, Y)),
    X2 is X - 1, retract(wumpus(X2, Y)).


update_wumpus(1):-
    current(X,Y,D),
    stench(X,Y),

    % if percieved smelly, update KB that wumpus MAY be in one of the adj rooms
    Y2 is Y + 1, assertz(wumpus(X, Y2)),
    Y2 is Y - 1, assertz(wumpus(X, Y2)),
    X2 is X + 1, assertz(wumpus(X2, Y)),
    X2 is X - 1, assertz(wumpus(X2, Y)).


update_portal(0):-
    current(X,Y,D),

    % if tingle is not perceived, portal cannot be in adj rooms
    Y2 is Y + 1, retract(confoundus(X, Y2)),
    Y2 is Y - 1, retract(confoundus(X, Y2)),
    X2 is X + 1, retract(confoundus(X2, Y)),
    X2 is X - 1, retract(confoundus(X2, Y)).


% if percieved tingle, update KB that portal MAY be in one of the adj rooms
update_portal(1):-
    current(X,Y,D),
    tingle(X,Y),

    % if tingle is perceived, portal MAY be in adj rooms
    Y2 is Y + 1, assertz(confoundus(X, Y2)),
    Y2 is Y - 1, assertz(confoundus(X, Y2)),
    X2 is X + 1, assertz(confoundus(X2, Y)),
    X2 is X - 1, assertz(confoundus(X2, Y)).


% if percieve glitter, cell is inhabited by coin
update_coin(1):-
    current(X,Y,D),
    glitter(X,Y).

explore(L):-

