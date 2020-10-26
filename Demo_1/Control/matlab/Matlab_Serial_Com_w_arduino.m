%%
clear 
port='COM8';% changes based on system
obj = serial(port, 'BaudRate', 250000);
obj.terminator = 'CR/LF';
if isempty(instrfind) %put a ~ before isempty run then remove the ~ and run again that should get the code to work
     fclose(instrfind);
      delete(instrfind);
end
fopen(obj);
for k =1:600
Velocity=fgetl(obj);
cCheck=convertCharsToStrings(Velocity);
RadVel(k)=cCheck;
display(Velocity);
end
fclose(obj);
%%
Vel_1=str2double(RadVel(1:2:end));
Vel_2=str2double(RadVel(2:2:end));

r=2.88*0.0254; %radius in meters
InstantVel_1=(Vel_1)./400;
InstantVel_2=(Vel_2)./400;
figure(1)
plot(InstantVel_1)
figure(2)
plot(InstantVel_2)