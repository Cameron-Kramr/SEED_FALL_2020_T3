clear;
%Setup World:
t0 = [1;    1;  1];
t1 = [5;    4;  2];
t2 = [7;    -2; 6];
t3 = [-5;   -3; 1];

Twx = [t0(1); t1(1); t2(1); t3(1)];
Twy = [t0(2); t1(2); t2(2); t3(2)];

n = length(Twx);

%Monte Carlo Simulations
sims = 100;
Twxs = zeros(n, sims);
Twys = zeros(n, sims);

Twxk1 = Twx;
Twyk1 = Twy;

for i = 1:sims
    %Equivalent to taking a measurment where Node 0 is the robot.
    T0x = [t0(1) - t0(1); t1(1)-t0(1); t2(1)-t0(1); t3(1)-t0(1)] + randn(n, 1);
    T0y = [t0(2) - t0(2); t1(2)-t0(2); t2(2)-t0(2); t3(2)-t0(2)] + randn(n, 1);

    T0x = repmat(T0x, 1, n);
    T0y = repmat(T0y, 1, n);

    Tnx = T0x - transpose(T0x);
    Tny = T0y - transpose(T0y);

    %Reconstruct world vectors for each of the nodes based on new measurements

    Twxk = 1/n*ones(n)*Twxk1 - 1/n*Tnx*ones(n,1);
    Twyk = 1/n*ones(n)*Twyk1 - 1/n*Tny*ones(n,1);
    
    Twxk1 = Twxk;
    Twyk1 = Twyk;
    
    Twxs(:, i) = Twxk;
    Twys(:, i) = Twyk;
end

plot(Twxs(1,:))