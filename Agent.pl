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
    asserta(current(0, 0, rnorth)),
    asserta(visited(0,0)).


reposition([Confounded, Stench, Tingle, _, _, _]):- 
    retractall(current(_, _, _)),
    retractall(visited(_, _)),
    retractall(confoundus(_, _)),
    retractall(tingle(_, _)),
    retractall(glitter(_, _)),
    retractall(stench(_, _)),
    retractall(safe(_, _)),

    asserta(current(0,0,rnorth)),
    asserta(visited(0,0)),

    once(current(X, Y, _)),
    (Confounded == 1 -> (\+confoundus(X,Y) -> asserta(confoundus(X, Y))));

    update_wumpus(Stench),
    update_portal(Tingle),
    update_safe().
    


% A = Forward, TurnLeft, TurnRight
% D = rnorth, rsouth, reast, rwest
% L = [Confounded, Stench, Tingle, Glitter, Bump, Scream]
% 1 = on, 0 = off
% sensory is received after making the move on the python side so need to update_action first before responsing to the sensory
move(A, [Confounded, Stench, Tingle, Glitter, Bump, Scream]):-
    %if bump occur dont do an action   
    (Bump \= 1 -> 
        update_action(A); 
        update_bump(); true
    ),

    update_portal(Confounded, indicator), %update the confounded indicator    
    update_wumpus(Stench),
    update_portal(Tingle),
    update_coin(Glitter),
    update_safe(). 

%assert current position to be the same to indicate a bump resulting in being same room
%remove the room from safe as it is not accessible
update_bump():-
    once(current(X, Y, D)),
    asserta(current(X,Y,D)),

    Z1 is Y + 1,
    Z2 is Y - 1, 
    Z3 is X + 1, 
    Z4 is X - 1, 
    (D == rnorth -> retract(safe(X, Z1));
     D == rsouth -> retract(safe(X, Z2));
     D == reast -> retract(safe(Z3, Y));
     D == rwest -> retract(safe(Z4, Y))).


update_action(turnleft):-
    write("turnleft "),
    once(current(X, Y, D)),
    (D == rnorth -> asserta(current(X, Y, rwest));
     D == rsouth -> asserta(current(X, Y, reast));
     D == reast -> asserta(current(X, Y, rnorth));
     D == rwest -> asserta(current(X, Y, rsouth))).


update_action(turnright):-
    write("turnright "),
    once(current(X, Y, D)),
    (D == rnorth -> asserta(current(X, Y, reast));
     D == rsouth -> asserta(current(X, Y, rwest));
     D == reast -> asserta(current(X, Y, rsouth));
     D == rwest -> asserta(current(X, Y, rnorth))).


update_action(moveforward):-
    write("forward "),
    once(current(X, Y, D)),

    Z1 is Y + 1,
    Z2 is Y - 1, 
    Z3 is X + 1, 
    Z4 is X - 1, 
    
    (D == rnorth -> asserta(current(X, Z1, D));
     D == rsouth -> asserta(current(X, Z2, D));
     D == reast -> asserta(current(Z3, Y, D));
     D == rwest -> asserta(current(Z4, Y, D))),

    %get new current to update visited
    %retract safe, wumpus and confoundus, since visited they not possible be there
    once(current(X1,Y1,_)),
    (\+visited(X1,Y1) 
        -> asserta(visited(X1, Y1))
        ; true),
    (retract(wumpus(X1,Y1))->true; true),
    (retract(confoundus(X1,Y1))->true; true),
    (retract(safe(X1,Y1))->true; true).


update_wumpus(0):-
    write("stench0 "),
    once(current(X,Y,_)),

    % if stench is not perceived, wumpus cannot be in adj rooms
    % "is" to evaluate mathematical expressions
    Z1 is Y + 1, (retract(wumpus(X, Z1)) ->true; true),
    Z2 is Y - 1, (retract(wumpus(X, Z2)) ->true; true),
    Z3 is X + 1, (retract(wumpus(Z3, Y)) ->true; true),
    Z4 is X - 1, (retract(wumpus(Z4, Y)) ->true; true).


update_wumpus(1):-
    write("stench1 "),
    once(current(X,Y,_)),
    asserta(stench(X,Y)),
    
    % if percieved stench, update KB that wumpus MAY be in one of the adj rooms
    Z1 is Y + 1, (determine_wumpus(X, Z1) ->true; true),
    Z2 is Y - 1, (determine_wumpus(X, Z2) ->true; true),
    Z3 is X + 1, (determine_wumpus(Z3, Y) ->true; true),
    Z4 is X - 1, (determine_wumpus(Z4, Y) ->true; true).


update_portal(0):-
    write("tingle0 "),
    once(current(X,Y,_)),

    % if tingle is not perceived, portal cannot be in adj rooms
    Z1 is Y + 1, (retract(confoundus(X, Z1))->true; true),
    Z2 is Y - 1, (retract(confoundus(X, Z2))->true; true),
    Z3 is X + 1, (retract(confoundus(Z3, Y))->true; true),
    Z4 is X - 1, (retract(confoundus(Z4, Y))->true; true).


% if perceived tingle, update KB that portal MAY be in one of the adj rooms
update_portal(1):-
    write("tingle1 "),
    once(current(X,Y,_)),
    asserta(tingle(X,Y)),

    % if tingle is perceived, portal MAY be in adj rooms
    Z1 is Y + 1, (determine_confoundus(X, Z1) ->true; true),
    Z2 is Y - 1, (determine_confoundus(X, Z2) ->true; true),
    Z3 is X + 1, (determine_confoundus(Z3, Y) ->true; true),
    Z4 is X - 1, (determine_confoundus(Z4, Y) ->true; true).

% to update confoundus indicator
update_portal(0, indicator):-
    true.

update_portal(1, indicator):-
    write("update portal indicator "),
    once(current(X,Y,_)),
    (\+confoundus(X,Y) 
        -> asserta(confoundus(X, Y))
        ; true).

% update safe rooms
update_safe():-
    write("safe "),
    once(current(X,Y,_)),

    Z1 is Y + 1, (determine_safe(X, Z1) ->true; true),
    Z2 is Y - 1, (determine_safe(X, Z2) ->true; true),
    Z3 is X + 1, (determine_safe(Z3, Y) ->true; true),
    Z4 is X - 1, (determine_safe(Z4, Y) ->true; true).


update_coin(0):-
    true.

% if percieve glitter, cell is inhabited by coin
update_coin(1):-
    write("glitter1 "),
    once(current(X,Y,_)),
    asserta(glitter(X,Y)),
    true.


% find overlapping wumpus(X,Y) rooms in KB (previously existed), wumpus may be in those overlapping rooms
determine_wumpus(X,Y):-
    write("determine wumpus "),
    % SYNTAX: (cond -> if-func ; else-func), \+ : Negation
    % if: there is prev wumpus(X,Y) entry with the exact same coords, More likely wumpus is in that room(s) -> already recorded
    % else: if there is no prior entry, add the new entry

    % wumpus cannot be in a cell that has been visited
    \+visited(X,Y),

    % if the cell not yet visited then ppossible wumpus
    (\+wumpus(X,Y) 
        -> asserta(wumpus(X, Y))
        ; true).

determine_confoundus(X,Y):-
    write("determine confoundus "),

    % confoundus cannot be in a cell that has been visited
    \+visited(X,Y),

    % if the cell not yet visited then ppossible confoundus
    (\+confoundus(X,Y) 
        -> asserta(confoundus(X, Y))
        ; true).

determine_safe(X,Y):-
    write("determine safe "),
    %cell is safe if it there is no possible wumpus or confoundus and not visited
    \+visited(X,Y),
    \+wumpus(X,Y),
    \+confoundus(X,Y),
    (\+safe(X,Y) 
        -> asserta(safe(X,Y))
        ; true).

%explore(L):-

