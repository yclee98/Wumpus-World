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
    wall/2,
    hasarrow/0,
    wumpus_alive/0,
    has_gold/0,
    initial_stench/0,
    next_direction/1,
    list_of_actions/1,

    %explore path
    path/2,
    visited_path/2,
    path_completed/1.


reborn():-
    retractall(current(_, _, _)),
    retractall(visited(_, _)),
    retractall(wumpus(_, _)),
    retractall(confoundus(_, _)),
    retractall(tingle(_, _)),
    retractall(glitter(_, _)),
    retractall(stench(_, _)),
    retractall(safe(_, _)),
    retractall(wall(_,_)),
    retractall(hasarrow()),
    retractall(wumpus_alive()),
    retractall(has_gold),
    retractall(initial_stench()),
    retractall(next_direction(_)),
    retractall(list_of_actions(_)),
    retractall(path(_,_)),
    retractall(visited_path(_,_)),
    retractall(path_completed(_)),


    % Set wumpus back alive
    asserta(wumpus_alive),
    asserta(initial_stench),
    asserta(agent_alive),
    asserta(has_gold),
    asserta(hasarrow),
    %asserta(initial_stench),
    asserta(current(0, 0, rnorth)),
    asserta(visited(0,0)).


reposition([Confounded, Stench, Tingle, _, _, _]):-
    retractall(current(_, _, _)),
    retractall(visited(_, _)),
    retractall(wumpus(_, _)),
    retractall(confoundus(_, _)),
    retractall(tingle(_, _)),
    retractall(glitter(_, _)),
    retractall(stench(_, _)),
    retractall(safe(_, _)),
    retractall(wall(_,_)),

    asserta(initial_stench),

    asserta(current(0,0,rnorth)),
    asserta(visited(0,0)),

    update_confounded(Confounded),
    update_stench(Stench),
    update_tingle(Tingle),
    update_safe().


% A = Forward, TurnLeft, TurnRight
% D = rnorth, rsouth, reast, rwest
% L = [Confounded, Stench, Tingle, Glitter, Bump, Scream]
% 1 = on, 0 = off
% sensory is received after making the move on the python side so need to update_action first before responsing to the sensory
move(A, [Confounded, Stench, Tingle, Glitter, Bump, Scream]):-
    update_bump(Bump), %if there is a bump then will not run the code below

    update_action(A), %for turnleft, turnright there is no need to run code below so they will return false

    update_confounded(Confounded), 
    update_stench(Stench),
    update_tingle(Tingle),
    update_glitter(Glitter),
    update_scream(Scream),
    update_safe().


update_action(turnleft):-
    once(current(X, Y, D)),
    (D == rnorth -> asserta(current(X, Y, rwest));
    D == rsouth -> asserta(current(X, Y, reast));
    D == reast -> asserta(current(X, Y, rnorth));
    D == rwest -> asserta(current(X, Y, rsouth))),
    false.

update_action(turnright):-
    once(current(X, Y, D)),
    (D == rnorth -> asserta(current(X, Y, reast));
    D == rsouth -> asserta(current(X, Y, rwest));
    D == reast -> asserta(current(X, Y, rsouth));
    D == rwest -> asserta(current(X, Y, rnorth))),
    false.

update_action(moveforward):-
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

    %keep track of latest visited at the top, 
    %for room that has been revisited it will remove previous and assert new at the top
    (once(retract(visited(X1,Y1))) -> true; true),
    asserta(visited(X1,Y1)),

    (retract(wumpus(X1,Y1))->true; true),
    %(retract(confoundus(X1,Y1))->true; true),
    retract_confoundus(X1, Y1),
    (retract(safe(X1,Y1))->true; true).

update_action(shoot):-
    %once(current(X, Y, D)),
    %asserta(current(X,Y,D)),
    retractall(hasarrow()).

update_action(pickup):-
    retractall(has_gold),
    retractall(glitter(_,_)).

% to update confoundus indicator
update_confounded(0):-
    true.

update_confounded(1):-
    once(current(X,Y,_)),
    (\+confoundus(X,Y)
        -> asserta(confoundus(X, Y))
        ; true).

update_stench(0):-
    once(current(X,Y,_)),

    % if stench is not perceived, wumpus cannot be in adj rooms
    % "is" to evaluate mathematical expressions
    Z1 is Y + 1, (retract(wumpus(X, Z1)) ->true; true),
    Z2 is Y - 1, (retract(wumpus(X, Z2)) ->true; true),
    Z3 is X + 1, (retract(wumpus(Z3, Y)) ->true; true),
    Z4 is X - 1, (retract(wumpus(Z4, Y)) ->true; true).


update_stench(1):-
    once(current(X,Y,_)),
    asserta(stench(X,Y)),

    % if percieved stench, update KB that wumpus MAY be in one of the adj rooms
    Z1 is Y + 1, (determine_wumpus(X, Z1) ->true; true),
    Z2 is Y - 1, (determine_wumpus(X, Z2) ->true; true),
    Z3 is X + 1, (determine_wumpus(Z3, Y) ->true; true),
    Z4 is X - 1, (determine_wumpus(Z4, Y) ->true; true).


update_tingle(0):-
    once(current(X,Y,_)),
    Z1 is Y + 1, (retract_confoundus(X,Z1)),
    Z2 is Y - 1, (retract_confoundus(X,Z2)),
    Z3 is X + 1, (retract_confoundus(Z3,Y)),
    Z4 is X - 1, (retract_confoundus(Z4,Y)).


% if perceived tingle, update KB that portal MAY be in one of the adj rooms
update_tingle(1):-
    once(current(X,Y,_)),
    asserta(tingle(X,Y)),

    % if tingle is perceived, portal MAY be in adj rooms
    Z1 is Y + 1, (determine_confoundus(X, Z1) ->true; true),
    Z2 is Y - 1, (determine_confoundus(X, Z2) ->true; true),
    Z3 is X + 1, (determine_confoundus(Z3, Y) ->true; true),
    Z4 is X - 1, (determine_confoundus(Z4, Y) ->true; true).

% dont retract the confoundus at 0,0 so that the origin always have a confoundus indicator on
retract_confoundus(X,Y):-
    \+((X =:= 0, Y =:=0)),
    retract(confoundus(X, Y)).

retract_confoundus(X,Y):- true.


update_glitter(0):-
    true.

% if percieve glitter, cell is inhabited by coin
update_glitter(1):-
    once(current(X,Y,_)),
    asserta(glitter(X,Y)).

update_bump(0):- true.

%assert current position to be the same to indicate a bump resulting in being same room
%remove the room from safe as it is not accessible
%return false when there is bump
update_bump(1):-
    once(current(X, Y, D)),
    asserta(current(X,Y,D)),

    Z1 is Y + 1,
    Z2 is Y - 1, 
    Z3 is X + 1, 
    Z4 is X - 1, 
    (D == rnorth -> update_bump(X, Z1);
     D == rsouth -> update_bump(X, Z2);
     D == reast -> update_bump(Z3, Y);
     D == rwest -> update_bump(Z4, Y)),

    false. 

update_bump(X,Y):-
    %there cannot be wumpus, confoundus and safe if experience bump infront
    %assert a wall 
    (retract(wumpus(X,Y))->true; true),
    (retract(confoundus(X,Y))->true; true),
    (retract(safe(X,Y))->true; true),
    asserta(wall(X,Y)).

update_scream(0):-
    true.

update_scream(1):-
    retractall(wumpus_alive()),
    retractall(wumpus(_,_)),
    retractall(stench(_,_)).

% update safe rooms
update_safe():-
    once(current(X,Y,_)),

    Z1 is Y + 1, (determine_safe(X, Z1) ->true; true),
    Z2 is Y - 1, (determine_safe(X, Z2) ->true; true),
    Z3 is X + 1, (determine_safe(Z3, Y) ->true; true),
    Z4 is X - 1, (determine_safe(Z4, Y) ->true; true).

determine_safe(X,Y):-
    %cell is safe if it there is no possible wumpus and confoundus and not visited
    \+visited(X,Y),
    \+wumpus(X,Y),
    \+confoundus(X,Y),
    \+wall(X,Y),
    (\+safe(X,Y)
        -> asserta(safe(X,Y))
        ; true).

% find overlapping wumpus(X,Y) rooms in KB (previously existed), wumpus may be in those overlapping rooms
determine_wumpus(X,Y):-
    % SYNTAX: (cond -> if-func ; else-func), \+ : Negation
    % if: there is prev wumpus(X,Y) entry with the exact same coords, More likely wumpus is in that room(s) -> already recorded
    % else: if there is no prior entry, add the new entry

    % wumpus cannot be in a cell that has been visited or mark as safe
    \+visited(X,Y),
    \+safe(X,Y),

    % before marking a room as possible wumpus inhabited, check its adj rooms if there is a stench.
    (\+wumpus(X,Y) -> check_wumpus_adj_rm_stench(X, Y), retract(initial_stench), true ; true).

% check if the adj rooms have stench
check_wumpus_adj_rm_stench(X,Y):-
    once(current(A, B, _)),

    Z1 is Y + 1,
    Z2 is Y - 1,
    Z3 is X + 1,
    Z4 is X - 1,

    % DO NOT COMPARE WITH LATEST CURRENT POSITION!!!
    % main room: room that is being considered to be marked with suspected wumpus.
    % adj room: rooms adjacent to the main room

    % if adj room not visited, and main room wumpus(X,Y) = false(avoid dups) -> mark main room with wumpus, continue comparison.
    (( Z1 =\= B, \+visited(X, Z1), \+wumpus(X,Y), initial_stench) -> asserta(wumpus(X, Y)) ; true),
    (( Z2 =\= B, \+visited(X, Z2), \+wumpus(X,Y), initial_stench) -> asserta(wumpus(X, Y)) ; true),
    (( Z3 =\= A, \+visited(Z3, Y), \+wumpus(X,Y), initial_stench) -> asserta(wumpus(X, Y)) ; true),
    (( Z4 =\= A, \+visited(Z4, Y), \+wumpus(X,Y), initial_stench) -> asserta(wumpus(X, Y)) ; true),

    % if adj room is visited & no stench -> main room no wumpus(retract), stop comparison.
    (( Z1 =\= B, visited(X, Z1), \+stench(x, Z1)) -> retract(wumpus(X,Y)), false ; true),
    (( Z2 =\= B, visited(X, Z2), \+stench(x, Z2)) -> retract(wumpus(X,Y)), false ; true),
    (( Z3 =\= A, visited(Z3, Y), \+stench(Z3, Y)) -> retract(wumpus(X,Y)), false ; true),
    (( Z4 =\= A, visited(Z4, Y), \+stench(Z4, Y)) -> retract(wumpus(X,Y)), false ; true),

    % if adj room is visited, has stench & main room wumpus(X,Y) = false(avoid dups) -> mark main room with wumpus, stop comparison.
    (( Z1 =\= B, visited(X, Z1), stench(x, Z1), \+wumpus(X,Y)) -> asserta(wumpus(X,Y)), false ; true),
    (( Z2 =\= B, visited(X, Z2), stench(x, Z2), \+wumpus(X,Y)) -> asserta(wumpus(X,Y)), false ; true),
    (( Z3 =\= A, visited(Z3, Y), stench(Z3, Y), \+wumpus(X,Y)) -> asserta(wumpus(X,Y)), false ; true),
    (( Z4 =\= A, visited(Z4, Y), stench(Z4, Y), \+wumpus(X,Y)) -> asserta(wumpus(X,Y)), false ; true).

determine_confoundus(X,Y):-
    % confoundus cannot be in a cell that has been visited or mark as safe
    \+visited(X,Y),
    \+safe(X,Y),

    (\+confoundus(X,Y) -> check_portal_adj_rm_tingle(X, Y), true ; true).

check_portal_adj_rm_tingle(X,Y):-
    once(current(A, B, _)),

    Z1 is Y + 1,
    Z2 is Y - 1,
    Z3 is X + 1,
    Z4 is X - 1,

    % DO NOT COMPARE WITH LATEST CURRENT POSITION!!!
    % main room: room that is being considered to be marked with suspected confoundus portal.
    % adj room: rooms adjacent to the main room

    % if adj room not visited, and main room confoundus(X,Y) = false(avoid dups) -> mark main room with confoundus, continue comparison.
    (( Z1 =\= B, \+visited(X, Z1), \+confoundus(X,Y)) -> asserta(confoundus(X, Y)) ; true),
    (( Z2 =\= B, \+visited(X, Z2), \+confoundus(X,Y)) -> asserta(confoundus(X, Y)) ; true),
    (( Z3 =\= A, \+visited(Z3, Y), \+confoundus(X,Y)) -> asserta(confoundus(X, Y)) ; true),
    (( Z4 =\= A, \+visited(Z4, Y), \+confoundus(X,Y)) -> asserta(confoundus(X, Y)) ; true),

    % if adj room is visited & no tingle -> main room has no confoundus(retract).
    (( Z1 =\= B, visited(X, Z1), \+tingle(x, Z1)) -> retract(confoundus(X,Y)), true ; true),
    (( Z2 =\= B, visited(X, Z2), \+tingle(x, Z2)) -> retract(confoundus(X,Y)), true ; true),
    (( Z3 =\= A, visited(Z3, Y), \+tingle(Z3, Y)) -> retract(confoundus(X,Y)), true ; true),
    (( Z4 =\= A, visited(Z4, Y), \+tingle(Z4, Y)) -> retract(confoundus(X,Y)), true ; true),

    % if adj room is visited, has tingle & main room confoundus(X,Y) = false(avoid dups) -> mark main room with confoundus.
    (( Z1 =\= B, visited(X, Z1), tingle(x, Z1), \+confoundus(X,Y)) -> asserta(confoundus(X,Y)), true ; true),
    (( Z2 =\= B, visited(X, Z2), tingle(x, Z2), \+confoundus(X,Y)) -> asserta(confoundus(X,Y)), true ; true),
    (( Z3 =\= A, visited(Z3, Y), tingle(Z3, Y), \+confoundus(X,Y)) -> asserta(confoundus(X,Y)), true ; true),
    (( Z4 =\= A, visited(Z4, Y), tingle(Z4, Y), \+confoundus(X,Y)) -> asserta(confoundus(X,Y)), true ; true).


%when there is coin to pickup then go to that location to pickup
explore(L):-
    glitter(X,Y),

    find_path_start(X, Y),
    determine_start_action(),
    assertz(list_of_actions(pickup)),
    findall(A, list_of_actions(A), L),
    write("explore pickup"),nl,
    !.

%when confirm wumpus location then action is shoot
%only shoot when we are certain of wumpus locatin which is when count of wumpus() is 1
%explore(L):-
    %aggregate_all(count, wumpus(_,_), Count),
    %Count == 1,
    %once(wumpus(X,Y)),

    %find a room that is adjacent to wumpus that is visited
    %visited(XV,YV),
    %is_adjacent(X,Y,XV,YV),

    %assertz(list_of_actions(shoot)),
    %findall(A, list_of_actions(A), L),
    %write("explore shoot"),nl,
    %!.

%when there is no glitter to pickup or wumpus to shoot then go to a safe location
explore(L):-
    once(safe(Xs,Ys)),
    has_gold(),
    find_path_start(Xs, Ys),
    determine_start_action(),
    findall(A, list_of_actions(A), L),
    write("explore safe"),nl,
    !.

%when there is no safe location but there is still gold left then go to confoundus portal
explore(L):-
    confoundus(X,Y),
    \+visited(X,Y),
    has_gold(),
    find_path_start(X, Y),
    determine_start_action(),
    findall(A, list_of_actions(A), L),
    write("explore confoundus"),nl,
    !.

%if there is no safe location then go back to origin 0,0
explore(L):-
    find_path_start(0, 0),
    determine_start_action(),
    findall(A, list_of_actions(A), L),
    write("explore origin"),nl,
    !.

determine_start_action():-
	retractall(next_direction(_)),
	retractall(list_of_actions(_)),
	once(current(X,Y,D)),
	(determine_action(X,Y,D) -> true ; true).

determine_action(X,Y,D):-
    once(path(PX, PY)),
	((D == rnorth -> NX is X, NY is Y+1);
	 (D == rsouth -> NX is X, NY is Y-1);
	 (D == reast -> NX is X+1, NY is Y);
	 (D == rwest -> NX is X-1, NY is Y)),
	X_diff is NX - PX,
	Y_diff is NY - PY,
	((Y_diff =:= 2, D == rnorth) -> asserta(next_direction(rsouth)), true; true),
	((Y_diff =:= -2, D == rsouth) -> asserta(next_direction(rnorth)), true; true),
	((X_diff =:= 2, D == reast) -> asserta(next_direction(rwest)), true; true),
	((X_diff =:= -2, D == rwest) -> asserta(next_direction(reast)), true; true),
	((X_diff =:= 2; X_diff =:= -2) -> assertz(list_of_actions(turnright)), assertz(list_of_actions(turnright)), assertz(list_of_actions(moveforward)), true ; true),
	((Y_diff =:= 2; Y_diff =:= -2) -> assertz(list_of_actions(turnright)), assertz(list_of_actions(turnright)), assertz(list_of_actions(moveforward)), true ; true),
	((X_diff =:= 0, Y_diff =:= 0) -> assertz(list_of_actions(moveforward)); true),
	((D == rnorth ; D == rsouth) -> flip_axis_Y(X_diff, Y_diff), true; true),
	((D == reast ; D == rwest) -> flip_axis_X(X_diff, Y_diff), true; true),
	once(next_direction(ND)),

    % if room adjacent to next path room has wumpus, add additional actions to determine whether or not to shoot it.
	(determine_path_adj_wumpus(PX, PY, ND) -> true;true),

	retract(path(PX, PY)),
	determine_action(PX,PY,ND).


flip_axis_X(X_diff, Y_diff):-
	(X_diff  =:= 1 -> (Y_diff =:= 1 -> asserta(next_direction(rsouth)), assertz(list_of_actions(turnright)), true; asserta(next_direction(rnorth)), assertz(list_of_actions(turnleft)), true) ; true),
	(X_diff  =:= -1 -> (Y_diff =:= 1 -> asserta(next_direction(rsouth)), assertz(list_of_actions(turnleft)), true; asserta(next_direction(rnorth)), assertz(list_of_actions(turnright)), true) ; true),
	((X_diff  =:= 1 ; X_diff  =:= -1) -> assertz(list_of_actions(moveforward)), true; true).


flip_axis_Y(X_diff, Y_diff):-
	(Y_diff  =:= 1 -> (X_diff =:= 1 -> asserta(next_direction(rwest)), assertz(list_of_actions(turnleft)), true; asserta(next_direction(reast)), assertz(list_of_actions(turnright)), true) ; true),
	(Y_diff  =:= -1 -> (X_diff =:= 1 -> asserta(next_direction(rwest)), assertz(list_of_actions(turnright)), true; asserta(next_direction(reast)), assertz(list_of_actions(turnleft)), true) ; true),
    ((Y_diff  =:= 1 ; Y_diff  =:= -1) -> assertz(list_of_actions(moveforward)), true; true).

determine_path_adj_wumpus(X, Y, D):-
	% check if the wumpus is in one of the rooms adjacent to the next path room.
	Z1 is Y + 1,
    Z2 is Y - 1,
    Z3 is X + 1,
    Z4 is X - 1,

	(wumpus(X,Z1) -> shoot_wumpus(X,Z1,D);true),
	(wumpus(X,Z2) -> shoot_wumpus(X,Z2,D);true),
	(wumpus(Z3,Y) -> shoot_wumpus(Z3,Y,D);true),
	(wumpus(Z4,Y) -> shoot_wumpus(Z4,Y,D);true).

shoot_wumpus(WX,WY,D):-
	% find total num of recorded wumpus room assumptions
	aggregate_all(count, wumpus(_,_), Wumpus_count),

	% if more than 1 wumpus room count, then agent is unsure where the wumpus is. -> dont shoot, stop function here.
	(Wumpus_count > 2 -> false;true),

	once(path(NX, NY)),
	((D == rnorth -> AX is NX, AY is NY+1);
	 (D == rsouth -> AX is NX, AY is NY-1);
	 (D == reast -> AX is NX+1, AY is NY);
	 (D == rwest -> AX is NX-1, AY is NY)),
	X_diff is AX - WX,
	Y_diff is AY - WY,
	((X_diff =:= 2; X_diff =:= -2), Wumpus_count =< 2, hasarrow -> assertz(list_of_actions(turnright)), assertz(list_of_actions(turnright)), assertz(list_of_actions(shoot)), list_of_actions(turnleft), assertz(list_of_actions(turnleft)), true ; true),
	((Y_diff =:= 2; Y_diff =:= -2), Wumpus_count =< 2, hasarrow -> assertz(list_of_actions(turnright)), assertz(list_of_actions(turnright)), assertz(list_of_actions(shoot)), list_of_actions(turnleft), assertz(list_of_actions(turnleft)), true ; true),
	((X_diff =:= 0, Y_diff =:= 0), Wumpus_count =< 2, hasarrow -> assertz(list_of_actions(shoot)); true),

	((D == rnorth ; D == rsouth) -> flip_axis_Y(X_diff, Y_diff, Wumpus_count), true; true),
	((D == reast ; D == rwest) -> flip_axis_X(X_diff, Y_diff, Wumpus_count), true; true).


flip_axis_X(X_diff, Y_diff, Wumpus_count):-
	% turn and shoot wumpus
	((X_diff  =:= 1, Wumpus_count =< 2, hasarrow) -> (Y_diff =:= 1 -> assertz(list_of_actions(turnright)), true; assertz(list_of_actions(turnleft)), true) ; true),
	((X_diff  =:= -1, Wumpus_count =< 2, hasarrow) -> (Y_diff =:= 1 -> assertz(list_of_actions(turnleft)), true; assertz(list_of_actions(turnright)), true) ; true),
	(((X_diff  =:= 1 ; X_diff  =:= -1), Wumpus_count =< 2, hasarrow) -> assertz(list_of_actions(shoot)), true; true),
	% return to original direction
	((X_diff  =:= 1, Wumpus_count =< 2, hasarrow) -> (Y_diff =:= 1 -> assertz(list_of_actions(turnleft)), true; assertz(list_of_actions(turnright)), true) ; true),
	((X_diff  =:= -1, Wumpus_count =< 2, hasarrow)  -> (Y_diff =:= 1 -> assertz(list_of_actions(turnright)), true; assertz(list_of_actions(turnleft)), true) ; true).


flip_axis_Y(X_diff, Y_diff, Wumpus_count):-
	% turn and shoot wumpus
	((Y_diff  =:= 1, Wumpus_count =< 2, hasarrow) -> (X_diff =:= 1 -> assertz(list_of_actions(turnleft)), true; assertz(list_of_actions(turnright)), true) ; true),
	((Y_diff  =:= -1, Wumpus_count =< 2, hasarrow)-> (X_diff =:= 1 -> assertz(list_of_actions(turnright)), true; assertz(list_of_actions(turnleft)), true) ; true),
    (((Y_diff  =:= 1;  Y_diff  =:= -1), Wumpus_count =< 2, hasarrow) -> assertz(list_of_actions(shoot)), true; true),
	% return to original direction
	(Y_diff  =:= 1, Wumpus_count =< 2, hasarrow -> (X_diff =:= 1 -> assertz(list_of_actions(turnright)), true; assertz(list_of_actions(turnleft)), true) ; true),
	(Y_diff  =:= -1, Wumpus_count =< 2, hasarrow -> (X_diff =:= 1 -> assertz(list_of_actions(turnleft)), true; assertz(list_of_actions(turnright)), true) ; true).


%plan a path from current to Xd yd (safe location)
%path store in path(X,Y)
find_path_start(Xd, Yd):-
    once(current(X,Y,_)),
    %as we use visited to get a list of connected path need the destination location to be inside
    %as safe room is not inside visited, put it in visited and remove at the end of search
    asserta(visited(Xd,Yd)),

    retractall(path(_,_)), %to keep track the path to destination
    retractall(visited_path(_,_)), %to keep track all visited path from this search
    retractall(path_completed(_)), %to stop searching when a path is found

    asserta(visited_path(X, Y)),
    find_path(X,Y,Xd,Yd),

    path_completed(1),
    once(retract(visited(Xd, Yd))).

%when x y == xd yd mean a path is found
find_path(X, Y, Xd, Yd):-
    (X =:= Xd, Y =:= Yd),
    write("Path found "),
    asserta(path_completed(1)),
    !.

% recursively search for a room that is adjacent and visited by agent 
find_path(X, Y, Xd, Yd):-
    \+path_completed(1),

    %get next room from visited which is adjacent and not yet visited by this path search 
    visited(XV, YV), 
    \+visited_path(XV,YV),
    is_adjacent(X, Y, XV, YV),
    \+path_completed(1),
    
    %write("path "), write(XV) , write(" ") ,  write(YV), nl,
    (\+visited_path(XV,YV) -> assertz(visited_path(XV,YV)); true),
    (\+path(XV,YV) -> assertz(path(XV,YV)); true),
    
    %find a path from the visited room taken from visited to destination 
    find_path(XV, YV, Xd, Yd).

%when there is no path ahead, retract this path
find_path(X,Y,_,_):-
    \+path_completed(1),
    retract(path(X,Y)).


% check if x y is adjacent to xd yd
is_adjacent(X,Y,Xd,Yd) :-
    ((X =:= Xd, Y =:= Yd+1);
    (X =:= Xd, Y =:= Yd-1);
    (X =:= Xd+1, Y =:= Yd);
    (X =:= Xd-1, Y =:= Yd)), !.



