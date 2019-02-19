

function y_out = biased_diffusion()

rng(10);
 
close all;
 
set(0,'Defaultlinelinewidth',2, 'DefaultlineMarkerSize',6,...
    'DefaultTextFontSize',15, 'DefaultAxesFontSize',15);
 
t_array = 0:0.05:400; 
 
v = 1 * 1;
 
phi0 = 0.15;
phic_array = [0.00001, 0.0001, 0.001, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0]; 
D = 0.6;  
gamma = 18; 
 
figure(); legend_array = {}; 
for phic_array_i = 1:length(phic_array)
    phi_c = phic_array(phic_array_i);
    l1 = v.*t_array + 2.*sqrt(D.*t_array) .* sqrt((log(phi0./sqrt(t_array))-log(phi_c)-gamma.*t_array));
    plot(t_array, l1, 'Color', [rand(1), rand(1), rand(1)]); xlabel('t'); ylabel('l(t)'); hold on; 
    legend_array{phic_array_i} = ['\phi_c=',num2str(phi_c)];
end
leg = legend(legend_array, 'Location','NorthEastOutside');
title(leg,'\phi_c')
xlim([0, 2]);
title(['\phi_0=',num2str(phi0), ', D=', num2str(D), ', v_w=', num2str(v), ', \gamma=', num2str(gamma)]);
 
y_out = 0; 
end