%% Extracting the experimental data for the motor
% THis matlab script takes the output values from the motor test to find
% the angular velocity of the motor when set to the maximum command
% voltage
%% Plotting Experimental motor outputs
angularVelocity=[0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 4.48 9.54 11.70 12.33 12.96 13.19 13.27 13.31 13.35 13.12 13.43 13.39 13.35 13.43 13.08 13.39 13.39 13.39 13.39]; %% [Rad/s]
time=linspace(0,2,39); % Total time that the motor ran
commandVoltage=[400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400.00 400 400 400];% [PWM] this is scaled to 400 due the the function we were using changed the value from 0-255 to -400 to 400 
trans=(angularVelocity./commandVoltage); %gets us W/(PWM Cnts) = (Rad/(s*PWM))
k=.033; %values for k found from the plotted experimental graph
sigma=11.24; %values of sigma found from plotted experimental graph
figure(1);
plot(time,trans)
xlabel('Time (S)')
ylabel('[(Rad/s)/[PWMcnt]]')
title('Experimental step responce')
%% Corresponding Simulink graph
out=sim('Closed_OpenLoopedSystems'); % For ease put both open and closed loop system on 1 simulink file
figure(2);
plot((out.openLoop))
xlabel('Time (S)')
ylabel('[(Rad/s)/[PWMcnt]]')
title('Simulink step responce')
