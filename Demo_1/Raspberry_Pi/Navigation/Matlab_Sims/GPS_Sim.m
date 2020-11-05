clear;
close;
%Setup World:
t0 = [1;    1;  1];
t1 = [5;    4;  2];
t2 = [7;    -2; 6];
t3 = [-5;   -3; 1];

Twx = [t0(1); t1(1); t2(1); t3(1)];
Twy = [t0(2); t1(2); t2(2); t3(2)];

n = length(Twx);

%Setup Kalman filter parameters:
Ppk1 = [1 0 0 0;
        0 1 0 0;
        0 0 1 0
        0 0 0 1];
Ppk1 = [0.910838127593087,0.00174721850217674,0.00174721850217674,0.00174721850217674;
        0.00174721850217676,0.910838127593085,0.00174721850217669,0.00174721850217670;
        0.00174721850217675,0.00174721850217676,0.910838127593085,0.00174721850217672;
        0.00174721850217675,0.00174721850217674,0.00174721850217675,0.910838127593087];

Q = [0 0 0 0;
     0 10 0 0
     0 0 10 0
     0 0 0 10];
 
R = [1 0 0 0
     0 1 0 0
     0 0 1 0
     0 0 0 1];

%Monte Carlo Simulations
sims = 1000;
Twxkps = zeros(n, sims);
Twxmks = zeros(n, sims);
Twys = zeros(n, sims);
Twxs = zeros(n, sims);

Twxpk1 = Twx;
Twypk1 = Twy;

speed = 0.05;

for i = 1:sims
    %Equivalent to taking a measurment where Node 0 is the robot.
    T0x = [t0(1) - t0(1); t1(1)-t0(1); t2(1)-t0(1); t3(1)-t0(1)] + randn(n, 1)/10;
    
    t0(1) = t0(1) + speed;
    Twx = [t0(1); t1(1); t2(1); t3(1)];
    
    T0x = repmat(T0x, 1, n);

    %Make predictions
    Tnx = transpose(T0x) - T0x ;
    Twxmk = 1/n*ones(n)*Twxpk1 - 1/n*Tnx*ones(n,1);
    Pmk = 1/n*ones(n)*Ppk1*transpose(1/n*ones(n)) + Q;

    %Update phase
    %Assume nodes don't move
    ykx = Twxpk1 - Twxmk;
    Kkx = Pmk/(R + Pmk);
    
    %Update measurment
    Twxkp = Twxmk + Kkx*ykx;
    Ppk1 = (eye(n) - Kkx)*Pmk;
    
    Twxpk1 = Twxkp;
    
    Twxmks(:, i) = Twxmk;
    Twxkps(:, i) = Twxkp;
    Twxs(:, i) = Twx;
end

figure(1)
hold on
plot(Twxkps(1,:))
plot(Twxs(1,:))
plot(Twxmks(1,:))
