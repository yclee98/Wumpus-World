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
    current(Y,X,D),

    % if stench is not perceived, wumpus cannot be in adj rooms
    % "is" to evaluate mathematical expressions
    Z1 is Y + 1, retract(wumpus(Z1, X)),
    Z2 is Y - 1, retract(wumpus(Z2, X)),
    Z3 is X + 1, retract(wumpus(Y, Z3)),
    Z4 is X - 1, retract(wumpus(Y, Z4)).


update_wumpus(1):-
    current(Y,X,D),
    stench(Y,X),

    % if percieved smelly, update KB that wumpus MAY be in one of the adj rooms
    Z1 is Y + 1, determine_wumpus(Z1, X),
    Z2 is Y - 1, determine_wumpus(Z2, X),
    Z3 is X + 1, determine_wumpus(Y, Z3),
    Z4 is X - 1, determine_wumpus(Y, Z4).


update_portal(0):-
    current(Y,X,D),

    % if tingle is not perceived, portal cannot be in adj rooms
    Z1 is Y + 1, retract(confoundus(Z1, X)),
    Z2 is Y - 1, retract(confoundus(Z2, X)),
    Z3 is X + 1, retract(confoundus(Z3, Y)),
    Z4 is X - 1, retract(confoundus(Z4, Y)).


% if perceived tingle, update KB that portal MAY be in one of the adj rooms
update_portal(1):-
    current(Y,X,D),
    tingle(Y,X),

    % if tingle is perceived, portal MAY be in adj rooms
    Z1 is Y + 1, assertz(confoundus(Z1, X)),
    Z2 is Y - 1, assertz(confoundus(Z2, X)),
    Z3 is X + 1, assertz(confoundus(Z3, Y)),
    Z4 is X - 1, assertz(confoundus(Z4, Y)).


% if percieve glitter, cell is inhabited by coin
update_coin(1):-
    current(Y,X,D),
    glitter(X,Y).


% find overlapping wumpus(X,Y) rooms in KB (previously existed), wumpus may be in those overlapping rooms
determine_wumpus(X,Y):-
    % SYNTAX: (cond -> if-func ; else-func), \+ : Negation
    % if: there is prev wumpus(X,Y) entry with the exact same coords, More likely wumpus is in that room(s) -> already recorded
    % else: if there is no prior entry, add the new entry

    (\+wumpus(X,Y) -> assertz(wumpus(X, Y)) : ).

explore(L):-

