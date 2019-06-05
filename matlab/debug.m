naparm_path = 'E:\Data\jrowland\2019-05-20\NAPARM\2019-05-20_RL032_NAPARM_012';

subset_size = 50;

point_obj = Main(naparm_path, 'processAll', 0, 'GroupSize', subset_size, 'splitPoints', 1, 'subsetSize', subset_size, 'Save', 1, 'SavePath', 'C:\Users\User\Documents\Code\blimp');


x = point_obj.split_points.X;
y = point_obj.split_points.Y;

fig = zeros(512,512);

for i = 1:length(x)
    fig(x(i), y(i)) = 1;
end

close all, figure
imshow(fig, [])

    





