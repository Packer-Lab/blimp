close all 

naparm_path = 'F:\Data\jrowland\2019-12-12\naparm\2019-12-12_plasticSlide_naparm_001';

subset_size = 20;

for i = 1:2
%    try
        point_obj = Main(naparm_path, 'processAll', 0, 'GroupSize', subset_size, 'splitPoints', 1, 'subsetSize', subset_size, 'Save', 1, 'SavePath', 'C:\Users\User\Documents\Code\blimp');
%    catch e
%        disp(e)
%    end
end

x = point_obj.split_points.X; 
y = point_obj.split_points.Y;

x_off = point_obj.split_points.offset_x;
y_off = point_obj.split_points.offset_y;


% fig = zeros(512,512);
% 
% for i = 1:length(x)
%     fig(y(i), x(i)) = 1;
%     fig(y_off(i), x_off(i)) = 2;
%     
% end
% cent_y = point_obj.split_points.centroid_y;
% cent_x = point_obj.split_points.centroid_x;
% %cent_y = round((cent_y * 1024 - (514/2)) / 514);
% 
% %fig(cent_y, cent_x) = 3;
% 
% close all, figure
% imshow(fig, [])
% figure
% imshow(point_obj.split_points.TransformedSLMTargets{1})






