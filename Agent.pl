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
%asserta(wumpus_alive),
%asserta(agent_alive),
%asserta(has_gold),
%asserta(hasarrow),
%asserta(current(0, 0, rnorth)).

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
    retractall(has_gold),

    % Set wumpus back alive
    asserta(wumpus_alive),
    asserta(agent_alive),
    asserta(has_gold),
    asserta(hasarrow),
    asserta(current(0, 0, rnorth)).



reposition([Confounded, Stench, Tingle, Glitter, Bump, Scream]):- 
    retractall(current(_, _, _)),
    retractall(visited(_, _)),
    retractall(confoundus(_, _)),
    retractall(tingle(_, _)),
    retractall(glitter(_, _)),
    retractall(stench(_, _)),
    retractall(safe(_, _)),

    asserta(current(0,0,rnorth)),
    asserta(confoundus(0,0)).


% A = Forward, TurnLeft, TurnRight
% D = rnorth, rsouth, reast, rwest
% L = [Confounded, Stench, Tingle, Glitter, Bump, Scream]
% 1 = on, 0 = off
move(A, [Confounded, Stench, Tingle, Glitter, Bump, Scream]):-
    current(X, Y, _),
    (Confounded == 1 -> asserta(confoundus(X,Y));true),

    update_action(A),
    
    % need to make it true so that if function return false it will still run the code 
    \+ update_wumpus(Stench) -> true,
    \+ update_portal(Tingle) -> true,
    \+ update_coin(Glitter) -> true.

update_action(turnleft):-
    write("turnleft "),
    current(X, Y, D),
    (D == rnorth -> retract(current(X, Y, D)), asserta(current(X, Y, rwest));
     D == rsouth -> retract(current(X, Y, D)), asserta(current(X, Y, reast));
     D == reast -> retract(current(X, Y, D)), asserta(current(X, Y, rnorth));
     D == rwest -> retract(current(X, Y, D)), asserta(current(X, Y, rsouth))).


update_action(turnright):-
    write("turnright "),
    current(X, Y, D),
    (D == rnorth -> retract(current(X, Y, D)), asserta(current(X, Y, reast));
     D == rsouth -> retract(current(X, Y, D)), asserta(current(X, Y, rwest));
     D == reast -> retract(current(X, Y, D)), asserta(current(X, Y, rsouth));
     D == rwest -> retract(current(X, Y, D)), asserta(current(X, Y, rnorth))).


update_action(moveforward):-
    write("forward "),
    current(X, Y, D),
    asserta(visited(X,Y)), %make old position as visited before moving forward
    Z1 is Y + 1,
    Z2 is Y - 1, 
    Z3 is X + 1, 
    Z4 is X - 1, 
    
    (D == rnorth -> retract(current(X, Y, D)), asserta(current(X, Z1, D));
     D == rsouth -> retract(current(X, Y, D)), asserta(current(X, Z2, D));
     D == reast -> retract(current(X, Y, D)), asserta(current(Z3, Y, D));
     D == rwest -> retract(current(X, Y, D)), asserta(current(Z4, Y, D))).


update_wumpus(0):-
    write("stench0 "),
    current(X,Y,D),

    % if stench is not perceived, wumpus cannot be in adj rooms
    % "is" to evaluate mathematical expressions
    Z1 is Y + 1, retract(wumpus(X, Z1)),
    Z2 is Y - 1, retract(wumpus(X, Z2)),
    Z3 is X + 1, retract(wumpus(Z3, Y)),
    Z4 is X - 1, retract(wumpus(Z4, Y)).


update_wumpus(1):-
    write("stench1 "),
    current(X,Y,D),
    asserta(stench(X,Y)),

    % if percieved stench, update KB that wumpus MAY be in one of the adj rooms
    Z1 is Y + 1, determine_wumpus(X, Z1),
    Z2 is Y - 1, determine_wumpus(X, Z2),
    Z3 is X + 1, determine_wumpus(Z3, Y),
    Z4 is X - 1, determine_wumpus(Z4, Y).


update_portal(0):-
    write("tingle0 "),
    current(X,Y,D),

    % if tingle is not perceived, portal cannot be in adj rooms
    Z1 is Y + 1, retract(confoundus(X, Z1)),
    Z2 is Y - 1, retract(confoundus(X, Z2)),
    Z3 is X + 1, retract(confoundus(Z3, Y)),
    Z4 is X - 1, retract(confoundus(Z4, Y)).


% if perceived tingle, update KB that portal MAY be in one of the adj rooms
update_portal(1):-
    write("tingle1 "),
    current(X,Y,D),
    asserta(tingle(X,Y)),

    % if tingle is perceived, portal MAY be in adj rooms
    Z1 is Y + 1, (\+confoundus(X,Z1) -> asserta(confoundus(X, Z1)); true),
    Z2 is Y - 1, (\+confoundus(X,Z2) -> asserta(confoundus(X, Z2)); true),
    Z3 is X + 1, (\+confoundus(Z3,Y) -> asserta(confoundus(Z3, Y)); true),
    Z4 is X - 1, (\+confoundus(Z4,Y) -> asserta(confoundus(Z4, Y)); true).


% if percieve glitter, cell is inhabited by coin
update_coin(1):-
    write("glitter1 "),
    current(X,Y,D),
    asserta(glitter(X,Y)).


% find overlapping wumpus(X,Y) rooms in KB (previously existed), wumpus may be in those overlapping rooms
determine_wumpus(X,Y):-
    write("determine wumpus "),
    % SYNTAX: (cond -> if-func ; else-func), \+ : Negation
    % if: there is prev wumpus(X,Y) entry with the exact same coords, More likely wumpus is in that room(s) -> already recorded
    % else: if there is no prior entry, add the new entry

    (\+wumpus(X,Y) -> asserta(wumpus(X, Y)); true).



%explore(L):-

