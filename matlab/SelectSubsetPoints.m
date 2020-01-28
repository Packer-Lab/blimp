function keep_idx = SelectSubsetPoints(obj)

%%%%%%%% maximum number of pixels apart points can be (2x 512)%%%%%%%%%%%%%%%
max_distance = 256;
disp('WARNING HAVE HACKED THIS, ONLY WORKS AT 1024 0.8x POINTS CANT BE MORE THAN 350UM APART')
%disp(['You have inputted a max distance for SelectSubsetPoints of ' num2str(max_distance)])
%read in stored imaging information from naparm 
zoom = obj.zoom;
%only need to rescale by zoom as resoluition is already downsampled
%max_distance = max_distance / (2 / zoom);

%disp(['This has been rescaled based on the zoom and resolution to ' num2str(max_distance)]) 
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


rng('shuffle')
x_coords = obj.all_points.X;
y_coords = obj.all_points.Y;
subsetSize = obj.inputParameters.subsetSize;

num_points = length(x_coords);

distances = zeros(num_points);
for i = 1:num_points
    x_point = x_coords(i);
    y_point = y_coords(i);
    
    for ii = 1:num_points
        
        x_measure = x_coords(ii);
        y_measure = y_coords(ii);
        
        distance = pdist([x_point, y_point; x_measure, y_measure]);
        distances(i,ii) = distance;
        
    end
end


distant_idx = find(distances > max_distance);
bool_mat = ones(size(distances));
bool_mat(distant_idx) = 0;

summed = sum(bool_mat, 2);


%points that have more than subsetSize points close to them
include_idx = find(summed > subsetSize);

if isempty(include_idx)
     %error(strcat('could not find ', num2str(subsetSize), ' points within ', num2str(max_distance), ' pxiels'))
     error('errr')
end


%%brute force ish solution%%
iter = 0;
while 1
    too_far = 0;
    iter = iter +1;
    if iter > 10000
        error(strcat('could not find ', num2str(subsetSize), ' points within ', num2str(max_distance), ' pxiels'))
    end
    
    rand_point = datasample(include_idx,1);
    close_points = find(bool_mat(rand_point,:));
    %do not include own point
    close_points = close_points(close_points ~= rand_point);
    
    test_selection = datasample(close_points, subsetSize-1, 'Replace', false);
    
    %check that all points in the test_selection are within max_distance
    for i = 1:length(test_selection)
        x = test_selection(i);
        
        for ii = 1:length(test_selection)
            y = test_selection(ii);
            
            if bool_mat(x,y) == 0
                too_far = 1;
                break
            end
        end
        
        if too_far
            break
        end
  
    end
        
    if too_far
        continue
    else
        disp('got solution yo')
        keep_idx = [test_selection rand_point];
        break
    end
   
end
 

%%% useful debugging tool
% fig1 = zeros(512,512);
% fig2 = zeros(512,512);
% 
% for point = 1:length(x_coords)
%     fig1(x_coords(point), y_coords(point)) = 1;
% end
% 
% imwrite(fig1,'all_points.tiff')
% 
% 
% for i = 1:length(keep_idx)
%     point = keep_idx(i);
%     fig2(x_coords(point), y_coords(point)) = 1;
% end
% 
% imwrite(fig2,'split_result.tiff')
    
    
    
    
    
    
    
    
    
    
    
    
