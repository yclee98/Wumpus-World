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
    agent_loc/2,
    hasarrow/0,
    wumpus_alive/0,
    agent_alive/0,
    has_gold/0,
    initial_stench/0,
    next_direction/1,
    list_of_actions/1,
    relative_current/3,

    %explore path
    path/2,
    visitedPath/2,
    pathCompleted/1.


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
    retractall(wall(_,_)),

    % when reborn, agent loses gold coin
    retractall(has_gold),

    % Set wumpus back alive
    asserta(wumpus_alive),
    asserta(initial_stench),
    asserta(agent_alive),
    asserta(has_gold),
    asserta(hasarrow),
    asserta(initial_stench),
    asserta(current(0, 0, rnorth)),
    asserta(visited(0,0)).


        reposition([Confounded, Stench, Tingle, _, _, _]):-
    write("repositioning "),
    retractall(current(_, _, _)),
    retractall(visited(_, _)),
    retractall(wumpus(_, _)),
    retractall(confoundus(_, _)),
    retractall(tingle(_, _)),
    retractall(glitter(_, _)),
    retractall(stench(_, _)),
    retractall(safe(_, _)),
    retractall(wall(_,_)),

    asserta(current(0,0,rnorth)),
    asserta(visited(0,0)),

    update_portal(Confounded, indicator),
    update_wumpus(Stench),
    update_portal(Tingle),
    update_safe().


        % A = Forward, TurnLeft, TurnRight
    % D = rnorth, rsouth, reast, rwest
    % L = [Confounded, Stench, Tingle, Glitter, Bump, Scream]
    % 1 = on, 0 = off
    % sensory is received after making the move on the python side so need to update_action first before responsing to the sensory
    move(A, [Confounded, Stench, Tingle, Glitter, Bump, Scream]):-
    update_bump(Bump), %if there is a bump then will not run the code below

    update_action(A), %for turnleft, turnright there is no need to run code below so they will return false
    update_portal(Confounded, indicator), %update the confounded indicator
    update_wumpus(Stench),
    update_portal(Tingle),
    update_coin(Glitter),
    update_scream(Scream),
    update_safe().


        update_bump(0):- write("bump0 "),true.

    %assert current position to be the same to indicate a bump resulting in being same room
    %remove the room from safe as it is not accessible
    %return false when there is bump
    update_bump(1):-
    write("bump1 "),
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
    (retract(wumpus(X,Y))->true; true),
(retract(confoundus(X,Y))->true; true),
(retract(safe(X,Y))->true; true),
asserta(wall(X,Y)).

    update_action(turnleft):-
    write("turnleft "),
    once(current(X, Y, D)),
    (D == rnorth -> asserta(current(X, Y, rwest));
D == rsouth -> asserta(current(X, Y, reast));
D == reast -> asserta(current(X, Y, rnorth));
D == rwest -> asserta(current(X, Y, rsouth))),
false.


    update_action(turnright):-
    write("turnright "),
    once(current(X, Y, D)),
    (D == rnorth -> asserta(current(X, Y, reast));
D == rsouth -> asserta(current(X, Y, rwest));
D == reast -> asserta(current(X, Y, rsouth));
D == rwest -> asserta(current(X, Y, rnorth))),
false.


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

update_action(shoot):-
    write("shoot "),
    %once(current(X, Y, D)),
    %asserta(current(X,Y,D)),
    retractall(hasarrow()).

        update_action(pickup):-
    write("pickup "),
    retractall(has_gold),
    retractall(glitter(_,_)).

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
    write("confoundus0 "),
    true.


update_portal(1, indicator):-
    write("confoundus1 "),
    once(current(X,Y,_)),
    (\+confoundus(X,Y)
        -> asserta(confoundus(X, Y))
        ; true).

update_scream(0):-
    write("scream0 "),
    true.

update_scream(1):-
    write("scream1 "),
    retractall(wumpus_alive()),
    retractall(wumpus(_,_)).

update_coin(0):-
    write("glitter0 "),
    true.


% if percieve glitter, cell is inhabited by coin
update_coin(1):-
    write("glitter1 "),
    once(current(X,Y,_)),
    asserta(glitter(X,Y)).


% update safe rooms
update_safe():-
    write("safe "),
    once(current(X,Y,_)),

    Z1 is Y + 1, (determine_safe(X, Z1) ->true; true),
    Z2 is Y - 1, (determine_safe(X, Z2) ->true; true),
    Z3 is X + 1, (determine_safe(Z3, Y) ->true; true),
    Z4 is X - 1, (determine_safe(Z4, Y) ->true; true).


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


determine_safe(X,Y):-
    %cell is safe if it there is no possible wumpus and confoundus and not visited
    \+visited(X,Y),
    \+wumpus(X,Y),
    \+confoundus(X,Y),
    \+wall(X,Y),
    (\+safe(X,Y)
        -> asserta(safe(X,Y))
        ; true).


%explore(L):-
    %(retractall(list_of_actions(_)) -> true; true),
    % Focus on rooms adjacent to the agent room. if there is a safe unvisited room, go to it.
    % else, go to a safe visited room. repeat process.

    %once(current(X,Y,_)),
    %Z1 is Y + 1,
    %Z2 is Y - 1,
    %Z3 is X + 1,
    %Z4 is X - 1,

    % shoot and pickup action implemetation to be added here

    % Find any safe unvisited rooms
    %(safe(X,Z1) -> goto(X,Z1,L); false),
    %(safe(X,Z2) -> goto(X,Z2,L); false),
    %(safe(Z3,Y) -> goto(Z3,Y,L); false),
    %(safe(Z4,Y) -> goto(Z4,Y,L); false),

    % if no safe unvisited rooms go to a safe visited room
    %(visited(X,Z1) -> goto(X,Z1,L); false),
    %(visited(X,Z2) -> goto(X,Z2,L); false),
    %(visited(Z3,Y) -> goto(Z3,Y,L); false),
    %(visited(Z4,Y) -> goto(Z4,Y,L); false),

%goto(X,Y,L):-
%    once(A,B,D),

%test out plan path
test_plan_path():-
    retractall(visited(_,_)),
	retractall(path(_,_)),
	asserta(current(4,2,rnorth)),
    asserta(visited(1,1)),
    asserta(visited(1,3)),

    asserta(visited(2,1)),
    asserta(visited(2,2)),
    asserta(visited(2,3)),
    asserta(visited(2,4)),

    asserta(visited(3,1)),
    %asserta(visited(3,3)),

    asserta(visited(4,1)),
    asserta(visited(4,2)),

    %plan a path to a unvisited room
    plan_path(4,2, 3,4),
    determine_start_action().

%test2():-
	%retractall(path(_,_)),
    %asserta(current(3,3,rwest)),
    %assertz(path(3,2)),
	%assertz(path(2,2)),
	%assertz(path(1,2)),
	%determine_start_action().

determine_start_action():-
	retractall(next_direction(_)),
	retractall(list_of_actions(_)),
	once(current(X,Y,D)),
	(determine_action(X,Y,D) -> true ; true).

determine_action(X,Y,D):-
    % get current direction number D2 for comparison
    ((D == rnorth -> D2 is 1);
     (D == reast -> D2 is 2);
     (D == rsouth -> D2 is 3);
     (D == rwest -> D2 is 4)
    ),
    once(path(X2,Y2)),
    Z1 is Y + 1,
    Z2 is Y - 1,
    Z3 is X + 1,
    Z4 is X - 1,
    % get the direction of the next room in the path
    % rnorth = 1, reast = 2, rsouth = 3, rwest = 4
    (Y2 =:= Y+1, X2 =:= X -> asserta(next_direction(1));
     Y2 =:= Y-1, X2 =:= X -> asserta(next_direction(3));
     Y2 =:= Y, X2 =:= X+1 -> asserta(next_direction(2));
     Y2 =:= Y, X2 =:= X-1 -> asserta(next_direction(4))),
     % D3 = expected direction number.
     once(next_direction(D3)),
    (D2 =:= D3 -> assertz(list_of_actions(forward));
    change_directions(D2, D3), true),
	retract(path(X2,Y2)),
	((D3 =:= 1 -> New_D = rnorth);
     (D3 =:= 2 -> New_D = reast);
     (D3 =:= 3 -> New_D = rsouth);
     (D3 =:= 4 -> New_D = rwest)
    ),
	determine_action(X2,Y2,New_D).

change_directions(D2, D3):-
    % if this function is done, that means agent not facing correct direction -> assertz change of direction
    % turnright (clkwise direction change) and increment D1(next direction number)
    D0 is D2 + 1,
	assertz(list_of_actions(turnright)),
    % direction number cannot be more than 4, if D1 = 5, (inital direction = rwest), set back to 1 (rnorth)
    (D0 =:= 5 -> D1 is 1; D1 is D0),
    % change directions in clockwise fashion
    (D1 =\= D3 -> change_directions(D1, D3); assertz(list_of_actions(forward)), true).


%plan a path from xy to Xd yd (safe location)
%path store in path(X,Y)
plan_path(X, Y, Xd, Yd):-
    %as we use visited to get a list of connected path need the destination location to be inside
    %as safe room is not inside visited, put it in visited and remove at the end of search
    (\+visited(Xd,Yd) -> asserta(visited(Xd,Yd)); true),

    retractall(path(_,_)), %to keep track the path from start to destination
    retractall(pathVisited(_,_)), %to keep track all visited path from this search
    retractall(pathCompleted(_)), %to stop searching when a path is found

    asserta(pathVisited(X, Y)),
    find_path(X,Y,Xd,Yd),

    retract(visited(Xd, Yd)).

%when x y == xd yd mean a path is found
find_path(X, Y, Xd, Yd):-
    (X =:= Xd, Y =:= Yd),
    write("Path found"),
    asserta(pathCompleted(1)),
    !.

% recursively search for a room that is adjacent and visited by agent 
find_path(X, Y, Xd, Yd):-
    \+pathCompleted(1),

    %get next room from visited which is adjacent and not yet visited by this path search 
    visited(XV, YV), 
    \+pathVisited(XV,YV),
    is_adjacent(X, Y, XV, YV),

    \+pathCompleted(1),
    
    write("path "), write(XV) , write(" ") ,  write(YV), nl,
    (\+pathVisited(XV,YV) -> assertz(pathVisited(XV,YV)); true),
    (\+path(XV,YV) -> assertz(path(XV,YV)); true),
    
    %find a path from the visited room taken from visited to destination 
    find_path(XV, YV, Xd, Yd).

%when there is no path ahead, retract this path
find_path(X,Y,_,_):-
    \+pathCompleted(1),
    retract(path(X,Y)).


% check if x y is adjacent to xt yt
is_adjacent(X,Y,Xd,Yd) :-
    ((X =:= Xd, Y =:= Yd+1);
    (X =:= Xd, Y =:= Yd-1);
    (X =:= Xd+1, Y =:= Yd);
    (X =:= Xd-1, Y =:= Yd)), !.
